from helpers.manhuaes import Manhuaes
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s'
)

manga = Manhuaes()
save_location = 'C:\\Users\\thezak48\\Desktop\\test\\'

# bewarn, this will download all chapters from this manga
# at the moment it has 50
manga_id, title_id = manga.get_manga_id(
    manga_name='carnephelias-curse-is-never-ending'
)

if manga_id:
    chapters = manga.get_manga_chapters(
        manga_id=manga_id
    )

    for x in range(len(chapters)):
        title = '{} Chapter {}'.format(
            title_id,
            str(x + 1)
        )
        images = manga.get_chapter_images(
            url=chapters[x]
        )
        manga.download_images(
            images=images,
            title=title,
            save_location=save_location,
        )
