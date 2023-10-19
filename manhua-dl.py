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
import logging
import os

from helpers.manhuaes import Manhuaes

parser = argparse.ArgumentParser(
    description="Download manhua from manhuaes.com",
    usage="%(prog)s manhua [options] save_location",
)
parser.add_argument(
    "manhua",
    type=str,
    help="The name and path of the file containing the manhua names or the name of the manhua",
)
parser.add_argument(
    "-mt", "--multi_threaded", action="store_true", help="Enable multi-threading"
)
parser.add_argument(
    "save_location", type=str, help="The location where the manhua should be saved"
)
args = parser.parse_args()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s",
)

manga = Manhuaes()
save_location = args.save_location
multi_threaded = args.multi_threaded

if os.path.isfile(args.manhua):
    with open(args.manhua, "r", encoding="utf-8") as f:
        manga_names = [line.strip() for line in f]
else:
    manga_names = [args.manhua]

for manga_name in manga_names:
    manga_id, title_id = manga.get_manga_id(manga_name)

    if manga_id:
        chapters = manga.get_manga_chapters(manga_id=manga_id)
        genres, summary = manga.get_manga_metadata(manga_name)

        complete_dir = os.path.join(save_location, title_id)
        existing_chapters = (
            set(os.listdir(complete_dir)) if os.path.exists(complete_dir) else set()
        )

        for x, chapter_url in enumerate(chapters, start=1):
            if f"Ch. {x}.cbz" in existing_chapters:
                logging.warning("%s Ch. %s already exists, skipping", title_id, x)
                continue

            images = manga.get_chapter_images(url=chapters[x])
            manga.download_images(
                images=images,
                title=title_id,
                chapter=x,
                save_location=save_location,
                series=title_id,
                genres=genres,
                summary=summary,
                multi_threaded=multi_threaded,
            )
