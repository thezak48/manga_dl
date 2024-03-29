"""Download images helper"""

import os
import re
import time
import shutil
import requests

from manga_dl.utilities.file_handler import FileHandler


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

    def download_image(
        self, chapter, image, path, progress, download_task, tmp_path, image_index
    ):
        """
        Download a single image.
        """
        start_time = time.time()
        image_size = 0
        success = False

        if "webtoon" in image:
            clean_url = image.split("?")[0]
            image_ext = os.path.splitext(clean_url)[1]
            image_name = f"{str(image_index).zfill(3)}{image_ext}"
            webtoons_path = os.path.join(tmp_path, image_name)
            result = requests.get(
                url=image,
                headers=self.headers_image,
                stream=True,
                timeout=30,
            )
            if result.status_code == 200:
                result.raw.decode_content = True
                with open(webtoons_path, "wb") as f:
                    shutil.copyfileobj(result.raw, f)
                progress.update(download_task, advance=1)
                self.logger.info("Downloaded Ch. %s image: %s", chapter, image_name)
                return True
            else:
                self.logger.error(
                    "[bold red blink]Unable to download page[/][medium_spring_green]%d[/]"
                    "from chapter [medium_spring_green]%d[/], request returned"
                    "error [bold red blink]%d[/]",
                    image,
                    chapter,
                    result.status_code,
                )
                return False
        else:
            with open(path, "wb") as writer:
                result = requests.get(
                    url=image,
                    headers=self.headers_image,
                    timeout=30,
                )
                if result.status_code == 200:
                    success = True
                    image_size = len(result.content)
                    elapsed_time = (time.time() - start_time) * 1000
                    writer.write(result.content)
                    progress.update(download_task, advance=1)
                    self.logger.info("Downloaded Ch. %s image: %s", chapter, image)
                    return len(result.content)
                else:
                    self.logger.error(
                        "[bold red blink]Unable to download page[/][medium_spring_green]%d[/]"
                        "from chapter [medium_spring_green]%d[/], request returned"
                        "error [bold red blink]%d[/]",
                        image,
                        chapter,
                        result.status_code,
                    )
                    success = False
                    elapsed_time = (time.time() - start_time) * 1000
                    return False

        if re.match(r".*/data/(?P<chapter_hash>[^/]+)/(?P<filename>.+)$", image):
            cached = result.headers.get("X-Cache", "").startswith("HIT")
            report_data = {
                "url": image,
                "success": success,
                "cached": cached,
                "bytes": image_size,
                "duration": elapsed_time,
            }
            report_response = requests.post(
                "https://api.mangadex.network/report", json=report_data, timeout=30
            )
            if report_response.status_code != 200:
                self.logger.error("Failed to report download status to MangaDex.")

    def sanitize_filename(self, filename):
        """Sanitize a string to be safe for use as a filename."""
        # Define a pattern to capture the file extension for common image files
        pattern = re.compile(
            r"(.*)(\.(jpg|jpeg|png|gif|bmp|webp))(\?.*)?", re.IGNORECASE
        )

        # Use the pattern to search for matches in the filename
        match = pattern.search(filename)
        if match:
            # Construct the sanitized filename using the captured groups
            sanitized = match.group(1) + match.group(2)
        else:
            # If no match, return the original filename (or handle as needed)
            sanitized = filename

        # Replace any remaining invalid characters with an underscore
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", sanitized)
        return sanitized

    def download_images(
        self,
        images,
        title_id,
        sanitized_title_id,
        chapter,
        save_location,
        progress,
        download_task,
    ):
        """
        Download images for a given manga chapter.
        """
        complete_dir = os.path.join(save_location, sanitized_title_id)
        if not os.path.exists(complete_dir):
            os.makedirs(complete_dir)

        tmp_path = os.path.join(
            save_location, "tmp", sanitized_title_id, f"Ch. {chapter}"
        )
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

        self.logger.info("Downloading %s Ch. %s", sanitized_title_id, chapter)

        results = []
        for i, image_url in enumerate(images):
            match = re.match(
                r".*/data/(?P<chapter_hash>[^/]+)/(?P<filename>.+)$", image_url
            )
            if match:
                file_extension = os.path.splitext(match.group("filename"))[1]
                image = f"{str(i+1).zfill(3)}{file_extension}"
                image_name = self.sanitize_filename(os.path.basename(image))
            else:
                image_name = self.sanitize_filename(os.path.basename(image_url))

            image_path = os.path.join(tmp_path, image_name)

            image_size = self.download_image(
                chapter, image_url, image_path, progress, download_task, tmp_path, i
            )
            if image_size:
                results.append(True)
            else:
                results.append(False)

        completed = all(results)
        if not completed:
            self.logger.error("Incomplete download of %s Ch. %s", title_id, chapter)

        return completed

    def download_chapter(
        self,
        x,
        images,
        title_id,
        sanitized_title_id,
        save_location,
        progress,
        genres,
        summary,
        complete_dir,
        chapter_task,
    ):
        """Download a chapter."""
        download_task = progress.add_task(
            f"[cyan]Downloading Ch. {x}", total=len(images)
        )
        completed = self.download_images(
            images,
            title_id,
            sanitized_title_id,
            chapter=x,
            save_location=save_location,
            progress=progress,
            download_task=download_task,
        )

        if completed:
            FileHandler(self.logger).create_comic_info(
                series=title_id,
                genres=genres,
                summary=summary,
                comic_info_path=os.path.join(save_location, "tmp", sanitized_title_id),
            )
            FileHandler(self.logger).make_cbz(
                directory_path=os.path.join(
                    save_location, "tmp", sanitized_title_id, f"Ch. {x}"
                ),
                compelte_dir=complete_dir,
                output_path=f"{x}.cbz",
                comic_info_path=os.path.join(
                    save_location, "tmp", sanitized_title_id, "ComicInfo.xml"
                ),
            )
            FileHandler(self.logger).cleanup(
                directory_path=os.path.join(
                    save_location, "tmp", sanitized_title_id, f"Ch. {x}"
                )
            )
            self.logger.info("done zipping: Ch. %s", x)
            progress.remove_task(download_task)
            progress.update(chapter_task, advance=1)
