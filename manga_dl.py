"""
This script is used to download manga's, manhua's or manhwa's.

Usage:
    python manga_dl.py manga [options] save_location
"""

import argparse
import concurrent.futures
import os
import re
import signal
import sys
import time
from datetime import datetime, timedelta
from urllib.parse import unquote, urlparse

from manga_dl.utilities.config import ConfigHandler
from manga_dl.utilities.image_downloader import ImageDownloader
from manga_dl.utilities.logging import setup_logging
from manga_dl.utilities.progress import Progress
from manga_dl.utilities.sites.kaiscans import Kaiscans
from manga_dl.utilities.sites.madraNew import MadraNew
from manga_dl.utilities.sites.madraOld import MadraOld
from manga_dl.utilities.sites.mangadex import Mangadex
from manga_dl.utilities.sites.mangakakalot import Mangakakalot
from manga_dl.utilities.sites.manganato import Manganato
from manga_dl.utilities.sites.webtoons import Webtoons


class GracefulThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """A ThreadPoolExecutor that catches SIGINT and SIGTERM and waits for all threads to finish."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shutdown = False
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        self._shutdown = True

    def submit(self, fn, *args, **kwargs):
        if self._shutdown:
            return
        super().submit(fn, *args, **kwargs)


log = setup_logging()

config = ConfigHandler(log, os.path.join("/config", "config.ini"))

parser = argparse.ArgumentParser(
    description="Download download manga's, manhua's or manhwa's",
    usage="%(prog)s [options]",
)
parser.add_argument(
    "-r",
    "--run",
    action="store_true",
    help="Run the script once and exit",
)
args = parser.parse_args()


def get_website_class(url: str):
    """Return the class for the website based on the URL."""
    if "manhuaes.com" in url or "manhuaaz.com" in url:
        return MadraOld(log)
    elif (
        "manhuaus.com" in url
        or "manhuaus.org" in url
        or "mangaread.org" in url
        or "lhtranslation.net" in url
        or "topmanhua.com" in url
        or "ksgroupscans.com" in url
        or "gdscans.com" in url
        or "setsuscans.com" in url
        or "manhwaclan.com" in url
    ):
        return MadraNew(log)
    elif "webtoons.com" in url:
        return Webtoons(log)
    elif "kaiscans.com" in url:
        return Kaiscans(log)
    elif (
        "mangakakalot.com" in url
        or "chapmanganato.com" in url
        or "readmanganato.com" in url
    ):
        return Mangakakalot(log)
    elif "mangadex.org" in url:
        return Mangadex(log)
    elif "manganato.com" in url or "chapmanganato.to" in url:
        return Manganato(log)
    else:
        raise ValueError(f"Unsupported website: {url}")


def sanitize_title(title):
    """Sanitize title id for file path."""
    invalid_chars = r'[\\/*?:"<>|]'
    sanitized_title = re.sub(invalid_chars, "_", title)

    return sanitized_title


mangas = config.get("General", "mangas")
save_location = config.get("General", "save_location")
multi_threaded = config.getboolean("General", "multi_threaded")
num_threads = config.getint("General", "num_threads")
schedule = config.getint("General", "schedule")


def download_manga():
    """Download manga's, manhua's or manhwa's."""
    with open(mangas, "r", encoding="utf-8") as f:
        manga_urls = [line.strip().rstrip("/") for line in f]
    try:
        progress = Progress()

        with progress.progress:
            manga_task = progress.add_task(
                "Downloading manga...", total=len(manga_urls)
            )

            for manga_url in manga_urls:
                manga = get_website_class(manga_url)
                headers_image = manga.headers_image
                headers_image.update({"referer": f"{manga_url}"})

                chapters, title = manga.get_manga_chapters(manga_url)
                chapter_task = progress.add_task(
                    f"Downloading chapters for {title}", total=len(chapters)
                )
                genres, summary = manga.get_manga_metadata(manga_url)
                sanitized_title = sanitize_title(title)

                complete_dir = os.path.join(save_location, sanitized_title)
                existing_chapters = (
                    set(os.listdir(complete_dir))
                    if os.path.exists(complete_dir)
                    else set()
                )

                if multi_threaded:
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=num_threads
                    ) as executor:
                        futures = []
                        for chapter_number, chapter_url in chapters:
                            if f"Ch. {chapter_number}.cbz" in existing_chapters:
                                log.info(
                                    "%s Ch. %s already exists, skipping",
                                    title,
                                    chapter_number,
                                )
                                progress.update(chapter_task, advance=1)
                                continue

                            images = manga.get_chapter_images(chapter_url)
                            futures.append(
                                executor.submit(
                                    ImageDownloader(
                                        log, headers_image
                                    ).download_chapter,
                                    chapter_number,
                                    images,
                                    title,
                                    sanitized_title,
                                    save_location,
                                    progress,
                                    genres,
                                    summary,
                                    complete_dir,
                                    chapter_task,
                                )
                            )

                else:
                    for chapter_number, chapter_url in chapters:
                        if f"Ch. {chapter_number}.cbz" in existing_chapters:
                            log.info(
                                "%s Ch. %s already exists, skipping",
                                title,
                                chapter_number,
                            )
                            progress.update(chapter_task, advance=1)
                            continue

                        images = manga.get_chapter_images(chapter_url)
                        ImageDownloader(log, headers_image).download_chapter(
                            chapter_number,
                            images,
                            title,
                            sanitized_title,
                            save_location,
                            progress,
                            genres,
                            summary,
                            complete_dir,
                            chapter_task,
                        )

            progress.update(manga_task, advance=1)

    except KeyboardInterrupt:
        progress.exit()
        sys.exit(0)


def calc_next_run(schd, write_out=False):
    """Calculates the next run time based on the schedule"""
    current = datetime.now().strftime("%H:%M")
    seconds = schd * 60
    time_to_run = datetime.now() + timedelta(minutes=schd)
    time_to_run_str = time_to_run.strftime("%H:%M")
    new_seconds = (
        datetime.strptime(time_to_run_str, "%H:%M")
        - datetime.strptime(current, "%H:%M")
    ).total_seconds()
    time_until = ""
    next_run = {}
    if args.run is False:
        next_run["next_run"] = time_to_run
        if new_seconds < 0:
            new_seconds += 86400
        if (seconds is None or new_seconds < seconds) and new_seconds > 0:
            seconds = new_seconds
        if seconds is not None:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            time_until = (
                f"{hours} Hour{'s' if hours > 1 else ''}{' and ' if minutes > 1 else ''}"
                if hours > 0
                else ""
            )
            time_until += (
                f"{minutes} Minute{'s' if minutes > 1 else ''}" if minutes > 0 else ""
            )
            if write_out:
                next_run["next_run_str"] = (
                    f"Current Time: {current} | {time_until} until the next run at {time_to_run_str}"
                )
    else:
        next_run["next_run"] = None
        next_run["next_run_str"] = ""
    return time_until, next_run


def main():
    """Main function of the script"""
    try:
        if args.run:
            log.warning("Run Mode: Script will exit after completion.")
            download_manga()
        else:
            while True:
                log.warning(
                    "Schedule Mode: Script will run every %s minutes.", schedule
                )
                download_manga()
                _, next_run = calc_next_run(int(schedule), write_out=True)
                log.info(next_run["next_run_str"])
                time.sleep(int(schedule) * 60)
    except KeyboardInterrupt:
        Progress().exit()
        sys.exit(0)


if __name__ == "__main__":
    main()
