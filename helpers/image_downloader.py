"""Download images helper"""
import os
import time

import requests

from helpers.file_handler import FileHandler


class ImageDownloader:
    """
    A class to download images.

    This class provides methods to download a single image or multiple images.

    Attributes:
        logger: An instance of log.Logger for log.
    """

    def __init__(self, logger, headers):
        self.logger = logger
        self.headers_image = headers

    def download_image(self, chapter, image, path, progress, download_task):
        """
        Download a single image.
        """
        with open(path, "wb") as writer:
            result = requests.get(
                url=image,
                headers=self.headers_image,
                timeout=30,
            )
            if result.status_code == 200:
                writer.write(result.content)
                progress.update(download_task, advance=1)
                self.logger.info("Downloaded Ch. %s image: %s", chapter, image)
                return len(result.content)
            else:
                self.logger.error("Failed to download Ch. %s image: %s", chapter, image)
                return False

    def download_images(
        self,
        images: list,
        title_id: str,
        chapter,
        save_location: str,
        progress,
        download_task,
    ):
        """
        Download images for a given manga chapter.
        """
        compelte_dir = os.path.join(save_location, title_id)
        if not os.path.exists(compelte_dir):
            os.makedirs(compelte_dir)

        tmp_path = os.path.join(save_location, "tmp", title_id, f"Ch. {chapter}")
        completed = True

        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

        self.logger.info("downloading %s Ch. %s", title_id, chapter)
        paths = [
            os.path.join(tmp_path, f"{str(x).zfill(3)}.jpg") for x in range(len(images))
        ]

        results = []

        for i, image in enumerate(images):
            image_path = paths[i]

            start_time = time.time()
            image_size = self.download_image(
                chapter, image, image_path, progress, download_task
            )
            elapsed_time = time.time() - start_time

            download_speed = (
                (image_size / elapsed_time) / 1024 if elapsed_time > 0 else 0
            )
            progress.progress.tasks[download_task].fields[
                "speed"
            ] = f"{download_speed:.2f}"

            if image_size:
                results.append(True)
            else:
                results.append(False)

        if not all(results):
            self.logger.error("Incomplete download of %s Ch. %s", title_id, chapter)
            completed = False

        return completed

    def download_chapter(
        self,
        x,
        images,
        title_id,
        save_location,
        progress,
        genres,
        summary,
        complete_dir,
    ):
        """Download a chapter."""
        download_task = progress.add_task(
            f"[cyan]Downloading Ch. {x}", total=len(images)
        )
        completed = self.download_images(
            images,
            title_id,
            chapter=x,
            save_location=save_location,
            progress=progress,
            download_task=download_task,
        )

        if completed:
            FileHandler(self.logger).create_comic_info(
                series=title_id, genres=genres, summary=summary
            )
            FileHandler(self.logger).make_cbz(
                directory_path=os.path.join(save_location, "tmp", title_id, f"Ch. {x}"),
                compelte_dir=complete_dir,
                output_path=f"{x}.cbz",
            )
            FileHandler(self.logger).cleanup(
                directory_path=os.path.join(save_location, "tmp", title_id, f"Ch. {x}")
            )
            self.logger.info("done zipping: Ch. %s", x)
