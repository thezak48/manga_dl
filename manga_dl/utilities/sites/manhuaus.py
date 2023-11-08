"""
This module defines the Manhuaus class for interacting with the website manhuaus.com.

The Manhuaus class provides methods to fetch manga IDs, chapters, images, 
and metadata from manhuaus.com, and to download manga images and save them as .cbz files.

Classes:
    Manhuaus: A class to interact with the website manhuaus.com.
"""
import requests
from bs4 import BeautifulSoup


class Manhuaus:
    """
    A class to interact with the website manhuaus.com.

    This class provides methods to fetch manga IDs, chapters, images,
    and metadata from manhuaus.com, and to download manga images and save them as .cbz files.

    Attributes:
        logger: An instance of log.Logger for log.
    """

    base_headers = {
        "authority": "manhuaus.com",
        "accept-language": "en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-site": "none",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ),
    }

    headers_get = base_headers.copy()
    headers_get.update(
        {
            "accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            ),
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
    )

    headers_post = base_headers.copy()
    headers_post.update(
        {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://manhuaus.com",
            "referer": "https://manhuaus.com/manga/the-school-beauty-president-is-all-over-me/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
        }
    )

    headers_image = base_headers.copy()
    headers_image.update(
        {
            "authority": "cdn.manhuaus.org",
            "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "referer": "https://manhuaus.com/",
            "sec-fetch-dest": "image",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-site": "same-site",
        }
    )

    def __init__(self, logger):
        self.logger = logger

    def get_manga_id(self, manga_name: str):
        """
        Get the manga ID for a given manga name.
        """

        url = f"https://manhuaus.com/manga/{manga_name}"

        result = requests.get(url, headers=self.headers_get, timeout=30)

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")
            node = soup.find("div", {"class": "post-title"})
            title = node.h1
            return url, title.text.lstrip().rstrip()
        self.logger.error("unable to find the manga id needed")
        return None

    def get_manga_chapters(self, manga_id: str):
        """
        Get the manga chapters for a given manga ID.
        """
        result = requests.post(
            url=f"{manga_id}/ajax/chapters",
            headers=self.headers_post,
            timeout=30,
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")
            nodes = soup.find_all("li", {"class": "wp-manga-chapter"})
            chapters = []

            for node in nodes:
                url = node.a["href"]
                if "/chapter-0" not in url:
                    chapter_number_raw = (
                        url.split("/chapter-")[-1].split("/")[0].replace("-", ".")
                    )
                    chapter_number = (
                        int(float(chapter_number_raw))
                        if chapter_number_raw.isdigit()
                        else float(chapter_number_raw)
                    )
                    chapters.append((chapter_number, url))

            def chapter_sort_key(chapter_info):
                return chapter_info[0]

            chapters.sort(key=chapter_sort_key)

            return chapters

        return None

    def get_chapter_images(self, url: str):
        """
        Get the manga chapter images for a given chapter URL.
        """
        result = requests.get(
            url=url,
            headers=self.headers_get,
            timeout=30,
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")
            node = soup.find("div", {"class": "reading-content"})
            image_nodes = node.find_all("img")
            images = []
            for image_node in image_nodes:
                images.append(image_node["data-src"].lstrip().rstrip())

            return images

    def get_manga_metadata(self, manga_name: str):
        """
        Get the manga metadata for a given manga name.
        """
        result = requests.get(
            url=f"https://manhuaus.com/manga/{manga_name}",
            headers=self.headers_get,
            timeout=30,
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")

            genres_content = soup.find("div", {"class": "genres-content"})
            genres = [a.text for a in genres_content.find_all("a")]

            summary_content = soup.find("div", {"class": "summary__content show-more"})
            summary = summary_content.p.text

            return genres, summary

        self.logger.error("unable to fetch the manga metadata")
        return None
