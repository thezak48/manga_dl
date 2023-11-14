"""
This module defines the Mangakakalot class for interacting with the website mangakakalot.com.

The Mangakakalot class provides methods to fetch manga IDs, chapters, images, 
and metadata from mangakakalot.com, and to download manga images and save them as .cbz files.

Classes:
    Mangakakalot: A class to interact with the website mangakakalot.com.
"""
import re

import requests
from bs4 import BeautifulSoup


class Mangakakalot:
    """
    A class to interact with the website mangakakalot.com.

    This class provides methods to fetch manga IDs, chapters, images,
    and metadata from mangakakalot.com, and to download manga images and save them as .cbz files.

    Attributes:
        logger: An instance of log.Logger for log.
    """

    base_headers = {
        "authority": "mangakakalot.com",
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

    headers_image = base_headers.copy()
    headers_image.update(
        {
            "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "referer": "https://mangakakalot.com/",
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

        url = manga_name

        result = requests.get(url, headers=self.base_headers, timeout=30)

        if "mangakakalot" in manga_name:
            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")
                node = soup.find("ul", {"class": "manga-info-text"})
                title = node.h1
                return url, title.text.lstrip().rstrip()
        elif "chapmanganato" in manga_name:
            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")
                node = soup.find("div", {"class": "story-info-right"})
                title = node.h1
                return url, title.text.lstrip().rstrip()
        self.logger.error("unable to find the manga id needed")
        return None

    def get_manga_chapters(self, manga_id: str):
        """
        Get the manga chapters for a given manga ID.
        """
        result = requests.get(
            url=f"{manga_id}",
            headers=self.base_headers,
            timeout=30,
        )
        if "mangakakalot" in manga_id:
            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")
                chapter_list = soup.find(
                    "div", {"class": "chapter-list"}
                )  # find chapter list first
                if chapter_list is not None:
                    rows = chapter_list.find_all(
                        "div", {"class": "row"}
                    )  # then find rows within the chapter list
                    chapters = []
                    for row in rows:
                        try:
                            url = row.find("a")[
                                "href"
                            ]  # URL is still in 'href' of 'a' tag in each row
                            chapter_number_raw = url.split("/chapter_")[-1]
                            number_parts = re.findall(
                                r"\d+\.\d+|\d+", chapter_number_raw
                            )  # capture float or int types
                            if (
                                "." in number_parts[0]
                            ):  # if chapter number is of float type e.g. 7.6
                                chapter_number = float(number_parts[0])
                            else:  # if it is of integer type e.g. 7
                                chapter_number = int(float(number_parts[0]))
                            chapters.append((chapter_number, url))
                        except TypeError:
                            continue
                    chapters.sort(key=lambda x: x[0])  # sort by chapter number
                    return chapters
        elif "chapmanganato" in manga_id:
            if result.status_code == 200:
                soup = BeautifulSoup(result.text, "html.parser")
                chapter_list = soup.find(
                    "div", {"class": "panel-story-chapter-list"}
                )  # find chapter list first
                if chapter_list is not None:
                    rows = chapter_list.find_all(
                        "li", {"class": "a-h"}
                    )  # then find rows within the chapter list
                    chapters = []
                    for row in rows:
                        try:
                            url = row.find("a")[
                                "href"
                            ]  # URL is still in 'href' of 'a' tag in each row
                            chapter_number_raw = url.split("/chapter-")[-1]
                            number_parts = re.findall(
                                r"\d+\.\d+|\d+", chapter_number_raw
                            )  # capture float or int types
                            if (
                                "." in number_parts[0]
                            ):  # if chapter number is of float type e.g. 7.6
                                chapter_number = float(number_parts[0])
                            else:  # if it is of integer type e.g. 7
                                chapter_number = int(float(number_parts[0]))
                            chapters.append((chapter_number, url))
                        except TypeError:
                            continue
                    chapters.sort(key=lambda x: x[0])  # sort by chapter number
                    return chapters
        self.logger.error("unable to find the manga chapters needed")
        return None

    def get_chapter_images(self, url: str):
        """
        Get the manga chapter images for a given chapter URL.
        """
        result = requests.get(
            url=url,
            headers=self.base_headers,
            timeout=30,
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")
            node = soup.find("div", {"class": "container-chapter-reader"})
            image_nodes = node.find_all("img")
            images = []
            for image_node in image_nodes:
                images.append(image_node["src"].lstrip().rstrip())

            return images

    def get_manga_metadata(self, manga_name: str):
        """
        Get the manga metadata for a given manga name.
        """
        genres = []
        summary = []

        return genres, summary
