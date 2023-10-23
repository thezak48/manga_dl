"""Download images helper"""
import os
import concurrent.futures
import requests
from helpers.logging import setup_logging


class ImageDownloader:
    """
    A class to download images.

    This class provides methods to download a single image or multiple images.

    Attributes:
        logger: An instance of log.Logger for log.
    """

    headers_image = {
        "authority": "img.manhuaes.com",
        "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "referer": "https://manhuaes.com/",
        "sec-fetch-dest": "image",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
    }

    def __init__(self):
        self.logger = setup_logging()

    def download_image(self, image, path):
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
                return True
            else:
                self.logger.error("Failed to download image: %s", image)
                return False

    def download_images(
        self,
        images: list,
        title: str,
        chapter,
        save_location: str,
        multi_threaded,
        progress,
    ):
        """
        Download images for a given manga chapter.
        """
        compelte_dir = os.path.join(save_location, title)
        if not os.path.exists(compelte_dir):
            os.makedirs(compelte_dir)

        tmp_path = os.path.join(save_location, "tmp", title, f"Ch. {chapter}")
        completed = True

        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

        self.logger.info("downloading %s Ch. %s", title, chapter)
        paths = [
            os.path.join(tmp_path, f"{str(x).zfill(3)}.jpg") for x in range(len(images))
        ]

        results = []

        with progress.progress:
            download_task = progress.add_task(
                f"[cyan]Downloading Ch. {chapter}", total=len(images)
            )

            if multi_threaded:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(self.download_image, image, path)
                        for image, path in zip(images, paths)
                    ]
                    for future in concurrent.futures.as_completed(futures):
                        results.append(future.result())
                        progress.update(download_task, advance=1)
            else:
                for image, path in zip(images, paths):
                    result = self.download_image(image, path)
                    results.append(result)
                    progress.update(download_task, advance=1)

        if not all(results):
            self.logger.error("Incomplete download of %s", title)
            completed = False

        return completed
