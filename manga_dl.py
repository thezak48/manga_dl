"""
This script is used to download manga's, manhua's or manhwa's.

Usage:
    python manga_dl.py manga [options] save_location
"""
import argparse
import concurrent.futures
import os
import signal
import sys
import time
from urllib.parse import unquote, urlparse
from datetime import datetime
from datetime import timedelta


from manga_dl.utilities.logging import setup_logging
from manga_dl.utilities.config import ConfigHandler
from manga_dl.utilities.image_downloader import ImageDownloader
from manga_dl.utilities.progress import Progress
from manga_dl.utilities.sites.manhuaaz import Manhuaaz
from manga_dl.utilities.sites.manhuaes import Manhuaes
from manga_dl.utilities.sites.manhuaus import Manhuaus
from manga_dl.utilities.sites.mangaread import Mangaread
from manga_dl.utilities.sites.webtoons import Webtoons
from manga_dl.utilities.sites.kaiscans import Kaiscans


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


if os.path.exists("/.dockerenv"):
    config_path = "/config"
else:
    config_path = os.path.dirname(__file__), "data"

log = setup_logging(config_path)

config = ConfigHandler(log, os.path.join(config_path, "config.ini"))

if config.has_option("General", "driver_path"):
    driver_path = config.get("General", "driver_path")
else:
    driver_path = "/usr/bin/chromedriver"

parser = argparse.ArgumentParser(
    description="Download download manga's, manhua's or manhwa's",
    usage="%(prog)s manga [options] save_location",
)
parser.add_argument(
    "-m",
    "--manga",
    type=str,
    nargs="?",
    default=config.get("General", "mangas"),
    help="The name and path of the file containing the manga URLs or the URL of the manga",
)
parser.add_argument(
    "-mt",
    "--multi_threaded",
    action="store_true",
    default=config.getboolean("General", "multi_threaded"),
    help="Enable multi-threading",
)
parser.add_argument(
    "-nt",
    "--num_threads",
    type=int,
    default=config.getint("General", "num_threads"),
    help="Number of threads to use in case of multi-threading",
)
parser.add_argument(
    "-r",
    "--run",
    action="store_true",
    help="Run the script once and exit",
)
parser.add_argument(
    "-sch",
    "--schedule",
    default="1440",
    type=str,
    help="Schedule to run every x minutes. (Default set to 1440 (1 day))",
)
parser.add_argument(
    "-s",
    "--save_location",
    type=str,
    default=config.get("General", "save_location"),
    help="The location where the manga should be saved",
)
args = parser.parse_args()


def get_website_class(url: str):
    """Return the class for the website based on the URL."""
    if "manhuaes.com" in url:
        return Manhuaes(log)
    elif "manhuaaz.com" in url:
        return Manhuaaz(log)
    elif "manhuaus.com" in url:
        return Manhuaus(log)
    elif "mangaread.org" in url:
        return Mangaread(log)
    elif "webtoons.com" in url:
        return Webtoons(log)
    elif "kaiscans.com" in url:
        return Kaiscans(log, driver_path)
    else:
        raise ValueError(f"Unsupported website: {url}")


save_location = args.save_location
multi_threaded = args.multi_threaded
schedule = args.schedule


def download_manga():
    if os.path.isfile(args.manga):
        with open(args.manga, "r", encoding="utf-8") as f:
            manga_urls = [line.strip().rstrip("/") for line in f]
    else:
        manga_urls = [args.manga.rstrip("/")]

    progress = Progress()
    try:
        with progress.progress:
            manga_task = progress.add_task(
                "Downloading manga...", total=len(manga_urls)
            )

            for manga_url in manga_urls:
                manga = get_website_class(manga_url)
                if isinstance(manga, (Webtoons, Kaiscans)):
                    manga_name = manga_url
                else:
                    manga_name = unquote(urlparse(manga_url).path.split("/")[-1])
                manga_id, title_id = manga.get_manga_id(manga_name)

                if manga_id:
                    chapters = manga.get_manga_chapters(manga_id=manga_id)
                    chapter_task = progress.add_task(
                        f"Downloading chapters for {title_id}", total=len(chapters)
                    )
                    genres, summary = manga.get_manga_metadata(manga_name)

                    complete_dir = os.path.join(save_location, title_id)
                    existing_chapters = (
                        set(os.listdir(complete_dir))
                        if os.path.exists(complete_dir)
                        else set()
                    )

                    if multi_threaded:
                        with concurrent.futures.ThreadPoolExecutor(
                            max_workers=args.num_threads
                        ) as executor:
                            futures = []
                            for chapter_number, chapter_url in chapters:
                                if f"Ch. {chapter_number}.cbz" in existing_chapters:
                                    log.info(
                                        "%s Ch. %s already exists, skipping",
                                        title_id,
                                        chapter_number,
                                    )
                                    progress.update(chapter_task, advance=1)
                                    continue

                                images = manga.get_chapter_images(url=chapter_url)
                                futures.append(
                                    executor.submit(
                                        ImageDownloader(
                                            log, manga.headers_image
                                        ).download_chapter,
                                        chapter_number,
                                        images,
                                        title_id,
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
                                    title_id,
                                    chapter_number,
                                )
                                progress.update(chapter_task, advance=1)
                                continue

                            images = manga.get_chapter_images(url=chapter_url)
                            ImageDownloader(log, manga.headers_image).download_chapter(
                                chapter_number,
                                images,
                                title_id,
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
                next_run[
                    "next_run_str"
                ] = f"Current Time: {current} | {time_until} until the next run at {time_to_run_str}"
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
                _, next_run = calc_next_run(int(args.schedule), write_out=True)
                log.info(next_run["next_run_str"])
                time.sleep(int(args.schedule) * 60)
    except KeyboardInterrupt:
        Progress().exit()
        sys.exit(0)


if __name__ == "__main__":
    main()
