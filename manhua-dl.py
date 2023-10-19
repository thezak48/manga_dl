import argparse
import os
from helpers.manhuaes import Manhuaes
import logging

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

        for x in range(len(chapters)):
            images = manga.get_chapter_images(url=chapters[x])
            manga.download_images(
                images=images,
                title=title_id,
                chapter=str(x + 1),
                save_location=save_location,
                series=title_id,
                genres=genres,
                summary=summary,
                multi_threaded=multi_threaded,
            )
