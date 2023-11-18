"""
This module defines the Kaiscans class for interacting with the website kaiscans.com.

The Kaiscans class provides methods to fetch manga IDs, chapters, images, 
and metadata from kaiscans.com, and to download manga images and save them as .cbz files.

Classes:
    Kaiscans: A class to interact with the website kaiscans.com.
"""

import requests
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver


class Kaiscans:
    """
    A class to interact with the website kaiscans.com.

    This class provides methods to fetch manga IDs, chapters, images,
    and metadata from kaiscans.com, and to download manga images and save them as .cbz files.

    Attributes:
        logger: An instance of log.Logger for log.
    """

    base_headers = {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ),
    }
    headers_image = base_headers

    def __init__(
        self,
        logger,
    ):
        self.logger = logger

    def get_manga_title(self, manga_url):
        """Get the series title for a given URL."""
        try:
            self.logger.info(f"Fetching manga title for {manga_url}")
            response = requests.get(manga_url, headers=self.base_headers, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                node = soup.find("div", {"id": "titlemove"})
                title = node.h1

                return title.text.lstrip().rstrip()

        except Exception as e:
            self.logger.error(f"Unable to fetch manga title for {manga_url}")
            self.logger.error(e)

        return None

    def get_manga_chapters(self, manga_url):
        """
        Get the manga chapters for a given manga ID.
        """
        try:
            self.logger.info(f"Fetching manga chapters for {manga_url}")
            title = self.get_manga_title(manga_url)
            result = requests.get(
                manga_url,
                headers=self.base_headers,
                timeout=30,
            )

            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")
                chapters = []

                for li in soup.find("div", class_="eplister").find_all("li"):
                    chapter_number = li.get("data-num")
                    url = li.find("a").get("href")
                    chapters.append((chapter_number, url))

                chapters = sorted(chapters, key=lambda x: float(x[0]))

                return chapters, title

        except Exception as e:
            self.logger.error(f"Unable to fetch manga chapters for {manga_url}")
            self.logger.error(e)

            return None

    def get_chapter_images(self, chapter_url):
        """
        Get the manga chapter images for a given chapter URL.
        """
        try:
            self.logger.info(f"Fetching chapter images for {chapter_url}")

            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            options.add_argument("no-sandbox")
            options.add_argument("disable-dev-shm-usage")
            options.add_argument("user-data-dir=/config/.cache/selenium")
            driver = webdriver.Chrome(options=options)
            driver.get(chapter_url)

            sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            image_nodes = soup.find("div", id="readerarea").find_all("img")
            images = []
            for image_node in image_nodes:
                data_src = image_node.get("data-src")
                if data_src:
                    images.append(data_src.strip())
                else:
                    images.append(image_node["src"].strip())

            driver.quit()

            return images
        except Exception as e:
            self.logger.error(f"Unable to fetch chapter images for {chapter_url}")
            self.logger.error(e)

            return None

    def get_manga_metadata(self, manga_url):
        """
        Get the manga metadata for a given manga name.
        """
        try:
            self.logger.info(f"Fetching manga metadata for {manga_url}")
            result = requests.get(
                manga_url,
                headers=self.base_headers,
                timeout=30,
            )

            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")

                genres_content = soup.find("div", {"class": "wd-full"})
                genres = [a.text for a in genres_content.find_all("a")]

                summary_content = soup.find("div", {"itemprop": "description"})
                summary = summary_content.p.text

                return genres, summary

        except Exception as e:
            self.logger.error("unable to fetch the manga metadata")
            self.logger.error(e)

            return None
