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
import os

from urllib.parse import urlparse, unquote
from helpers.logging import setup_logging
from helpers.manhuaes import Manhuaes
from helpers.manhuaaz import Manhuaaz
from helpers.progress import Progress

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
    "save_location", type=str, help="The location where the manhua should be saved"
)
args = parser.parse_args()


def get_website_class(url: str):
    """Return the class for the website based on the URL."""
    if "manhuaes.com" in url:
        return Manhuaes()
    elif "manhuaaz.com" in url:
        return Manhuaaz()
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
                set(os.listdir(complete_dir)) if os.path.exists(complete_dir) else set()
            )

            for x, chapter_url in enumerate(chapters, start=1):
                if f"Ch. {x}.cbz" in existing_chapters:
                    log.warning("%s Ch. %s already exists, skipping", title_id, x)
                    continue

                images = manga.get_chapter_images(url=chapter_url)
                manga.download_images(
                    images=images,
                    title=title_id,
                    chapter=x,
                    save_location=save_location,
                    series=title_id,
                    genres=genres,
                    summary=summary,
                    multi_threaded=multi_threaded,
                    progress=progress,
                )
            progress.update(chapter_task, advance=1)

        progress.update(manga_task, advance=1)
