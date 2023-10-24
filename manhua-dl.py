"""
This script is used to download manga from manhuaes.com.

It reads manga names from a text file, fetches their IDs, metadata,
and chapters from manhuaes.com, and then downloads the images for each chapter. 
The images are saved to a specified location on the local file system.

The script uses the Manhuaes class defined in the helpers.manhuaes module
to interact with manhuaes.com. This class provides methods to fetch and download manga data.

The script can optionally use multi-threading to download images concurrently,
which can significantly speed up the download process.

Usage:
    python manhua-dl.py manhua [options] save_location
"""
import argparse
import concurrent.futures
import os
import signal
import sys
from urllib.parse import unquote, urlparse

from helpers.image_downloader import ImageDownloader
from helpers.logging import setup_logging
from helpers.manhuaaz import Manhuaaz
from helpers.manhuaes import Manhuaes
from helpers.manhuaus import Manhuaus
from helpers.progress import Progress


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

parser = argparse.ArgumentParser(
    description="Download manhua from manhuaes.com or manhuaaz.com",
    usage="%(prog)s manhua [options] save_location",
)
parser.add_argument(
    "manhua",
    type=str,
    help="The name and path of the file containing the manhua URLs or the URL of the manhua",
)
parser.add_argument(
    "-mt", "--multi_threaded", action="store_true", help="Enable multi-threading"
)
parser.add_argument(
    "-nt",
    "--num_threads",
    type=int,
    default=10,
    help="Number of threads to use in case of multi-threading",
)
parser.add_argument(
    "save_location", type=str, help="The location where the manhua should be saved"
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
    else:
        raise ValueError(f"Unsupported website: {url}")


save_location = args.save_location
multi_threaded = args.multi_threaded

if os.path.isfile(args.manhua):
    with open(args.manhua, "r", encoding="utf-8") as f:
        manga_urls = [line.strip() for line in f]
else:
    manga_urls = [args.manhua]

progress = Progress()
try:
    with progress.progress:
        manga_task = progress.add_task("Downloading manga...", total=len(manga_urls))

        for manga_url in manga_urls:
            manga = get_website_class(manga_url)
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
                        for x, chapter_url in enumerate(chapters, start=1):
                            if f"Ch. {x}.cbz" in existing_chapters:
                                log.info(
                                    "%s Ch. %s already exists, skipping", title_id, x
                                )
                                progress.update(chapter_task, advance=1)
                                continue

                            images = manga.get_chapter_images(url=chapter_url)
                            futures.append(
                                executor.submit(
                                    ImageDownloader(
                                        log, manga.headers_image
                                    ).download_chapter,
                                    x,
                                    images,
                                    title_id,
                                    save_location,
                                    progress,
                                    genres,
                                    summary,
                                    complete_dir,
                                )
                            )

                            progress.update(chapter_task, advance=1)
                else:
                    for x, chapter_url in enumerate(chapters, start=1):
                        if f"Ch. {x}.cbz" in existing_chapters:
                            log.info("%s Ch. %s already exists, skipping", title_id, x)
                            progress.update(chapter_task, advance=1)
                            continue

                        images = manga.get_chapter_images(url=chapter_url)
                        ImageDownloader(log, manga.headers_image).download_chapter(
                            x,
                            images,
                            title_id,
                            save_location,
                            progress,
                            genres,
                            summary,
                            complete_dir,
                        )

                        progress.update(chapter_task, advance=1)

        progress.update(manga_task, advance=1)

except KeyboardInterrupt:
    progress.exit()
    sys.exit(0)
