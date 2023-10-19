from helpers.manhuaes import Manhuaes
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s",
)

manga = Manhuaes()
save_location = "C:\\Users\\thezak48\\Desktop\\test\\"
multi_threaded = True

with open("manhua.txt", "r", encoding="utf-8") as f:
    manga_names = [line.strip() for line in f]

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
