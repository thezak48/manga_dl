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
from selenium.webdriver.chrome.options import Options


class Kaiscans:
    """
    A class to interact with the website kaiscans.com.

    This class provides methods to fetch manga IDs, chapters, images,
    and metadata from kaiscans.com, and to download manga images and save them as .cbz files.

    Attributes:
        logger: An instance of log.Logger for log.
    """

    base_headers = {
        "authority": "kaiscans.com",
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
    headers_image = base_headers

    def __init__(self, logger, driver_path):
        self.logger = logger
        self.driver_path = driver_path

    def get_manga_id(self, manga_name: str):
        """Get the series title for a given URL."""
        response = requests.get(manga_name, headers=self.base_headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            node = soup.find("div", {"id": "titlemove"})
            title = node.h1
            return manga_name, title.text.lstrip().rstrip()
        self.logger.error(f"Status code: {response.status_code}")
        return None

    def get_manga_chapters(self, manga_id: str):
        """
        Get the manga chapters for a given manga ID.
        """
        result = requests.get(
            manga_id,
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

            return chapters

        return None

    def get_chapter_images(self, url: str):
        """
        Get the manga chapter images for a given chapter URL.
        """
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(self.driver_path, options=options)
        driver.get(url)

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

    def get_manga_metadata(self, manga_url: str):
        """
        Get the manga metadata for a given manga name.
        """
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

        self.logger.error("unable to fetch the manga metadata")
        return None
