"""
Something"""

import requests
import re
from bs4 import BeautifulSoup


class MadraNew:
    """
    WIP"""

    base_headers = {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ),
    }

    headers_image = base_headers.copy()
    headers_image.update({})

    def __init__(self, logger):
        self.logger = logger

    def get_manga_title(self, manga_url):
        """
        WIP"""
        try:
            self.logger.info("Getting manga title")
            result = requests.get(manga_url, headers=self.base_headers, timeout=30)

            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")
                node = soup.find("div", {"class": "post-title"})
                title = node.h1

                self.logger.debug("Found the following title: %s", title.text)
                return title.text.lstrip().rstrip()

        except Exception as e:
            self.logger.error("Unable to find the manga title")
            self.logger.error(e)

            return None

    def get_manga_chapters(self, manga_url):
        """
        WIP"""
        try:
            self.logger.info("Getting manga chapters")
            title = self.get_manga_title(manga_url)
            result = requests.post(
                url=f"{manga_url}/ajax/chapters", headers=self.base_headers, timeout=30
            )

            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")
                nodes = soup.find_all("li", {"class": "wp-manga-chapter"})
                chapters = []

                for node in nodes:
                    url = node.a["href"]
                    chapter_number_raw = url.split("/chapter-")[-1].split("/")[0]
                    number_parts = re.findall(r"\d+", chapter_number_raw)

                    if len(number_parts) >= 2:
                        chapter_number = float(f"{number_parts[0]}.{number_parts[1]}")
                    else:
                        chapter_number = int(float(number_parts[0]))

                    chapters.append((chapter_number, url))

                def chapter_sort_key(chapter_info):
                    return chapter_info[0]

                chapters.sort(key=chapter_sort_key)

                return chapters, title

        except Exception as e:
            self.logger.error("Unable to find the manga chapters")
            self.logger.error(e)

            return None

    def get_chapter_images(self, chapter_url):
        try:
            self.logger.info("Getting chapter images")
            result = requests.get(chapter_url, headers=self.base_headers, timeout=30)

            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")
                nodes = soup.find("div", {"class": "reading-content"})
                images = []

                for img in nodes.find_all("img"):
                    if "data-src" in img.attrs:
                        images.append(img["data-src"].strip())
                    elif "src" in img.attrs:
                        images.append(img["src"].strip())

                return images

        except Exception as e:
            self.logger.error("Unable to find the chapter images")
            self.logger.error(e)

            return None

    def get_manga_metadata(self, manga_url):
        """
        WIP"""
        try:
            self.logger.info("Getting manga metadata")
            result = requests.get(manga_url, headers=self.base_headers, timeout=30)

            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")

                genres_content = soup.find("div", {"class": "genres-content"})
                genres = [a.text for a in genres_content.find_all("a")]

                summary_content = soup.find(
                    "div", {"class": "summary__content show-more"}
                )
                summary = summary_content.p.text

                return genres, summary

        except Exception as e:
            self.logger.error("Unable to find the manga metadata")
            self.logger.error(e)

            return None
