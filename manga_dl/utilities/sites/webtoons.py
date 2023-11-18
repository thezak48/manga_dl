"""
This module defines the Webtoons class for interacting with the website webtoons.com.

The Webtoons class provides methods to fetch manga IDs, chapters, images, 
and metadata from webtoons.com, and to download manga images and save them as .cbz files.

Classes:
    Webtoons: A class to interact with the website webtoons.com.
"""
import os
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup


class Webtoons:
    """
    A class to interact with the website webtoons.com.

    This class provides methods to fetch manga IDs, chapters, images,
    and metadata from webtoons.com, and to download manga images and save them as .cbz files.

    Attributes:
        logger: An instance of log.Logger for log.
    """

    USER_AGENT = (
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/92.0.4515.107 Safari/537.36"
        )
        if os.name == "nt"
        else ("Mozilla/5.0 (X11; Linux ppc64le; rv:75.0)" "Gecko/20100101 Firefox/75.0")
    )

    headers = {
        "dnt": "1",
        "user-agent": USER_AGENT,
        "accept-language": "en-US,en;q=0.9",
    }
    headers_image = {"referer": "https://www.webtoons.com/", **headers}

    def __init__(self, logger):
        self.logger = logger

    def get_manga_title(self, manga_url):
        """Get the series title for a given URL."""
        try:
            self.logger.info(f"Fetching manga title for {manga_url}")
            response = requests.get(manga_url, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            title = (
                soup.find(class_="subj")
                .get_text(separator=" ")
                .replace("\n", "")
                .replace("\t", "")
            )
            return title
        except Exception as e:
            self.logger.error("Unable to find the manga title")
            self.logger.error(e)
            return None

    def get_chapter_viewer_url(self, manga_url):
        """Get the chapter viewer URL for a given URL."""
        try:
            self.logger.info(f"Fetching chapter viewer URL for {manga_url}")
            response = requests.get(manga_url, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            chapter_viewer = soup.find("li", {"class": "_episodeItem"})
            if chapter_viewer:
                viewer_url = chapter_viewer.find("a")
                return viewer_url.get("href") if viewer_url else None
        except Exception as e:
            self.logger.error("Unable to find the chapter viewer URL")
            self.logger.error(e)
            return None

    def get_first_chapter_episode_no(self, manga_url):
        """
        Get the first chapter episode number for a given manga ID.
        """
        try:
            response = requests.get(manga_url, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            href = soup.find("a", id="_btnEpisode")["href"]
            return int(parse_qs(urlparse(href).query)["episode_no"][0])
        except (TypeError, KeyError):
            response = requests.get(f"{manga_url}&page=9999", timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            return min(
                int(episode["data-episode-no"])
                for episode in soup.find_all("li", {"class": "_episodeItem"})
            )

    def get_manga_chapters(self, manga_url):
        """
        Get the manga chapters for a given manga ID.
        """
        try:
            self.logger.info(f"Fetching manga chapters for {manga_url}")
            title = self.get_manga_title(manga_url)
            first_chapter = self.get_first_chapter_episode_no(manga_url)
            viewer_url = self.get_chapter_viewer_url(manga_url)
            if viewer_url:
                parsed = urlparse(viewer_url)
                params = parse_qs(parsed.query)
                episode_no = int(params.get("episode_no", [None])[0])
                chapters = []

                for i in range(first_chapter, episode_no + 1):
                    chapter_viewer_url = viewer_url.replace(
                        f"/episode-{params['episode_no'][0]}", f"/episode-{i}"
                    ).replace(
                        f"&episode_no={params['episode_no'][0]}", f"&episode_no={i}"
                    )
                    chapters.append((i, chapter_viewer_url))

                return chapters, title

        except Exception as e:
            self.logger.error("Unable to find the manga chapters")
            self.logger.error(e)
            return None

    def get_chapter_images(self, chapter_url):
        """
        Get the manga chapter images for a given chapter URL.
        """
        result = requests.get(
            chapter_url,
            headers=self.headers,
            timeout=30,
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")
            node = soup.find("div", class_="viewer_img _img_viewer_area")
            image_nodes = node.find_all("img")
            images = []
            for image_node in image_nodes:
                url = image_node.get("data-url")
                if url:
                    images.append(url.strip())

            return images

    def get_manga_metadata(self, manga_url):
        """
        Get the manga metadata for a given manga name.
        """
        result = requests.get(
            manga_url,
            headers=self.headers,
            timeout=30,
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")

            genres_content = soup.find("div", {"class": "info"})
            genres = [h2.text for h2 in genres_content.find_all("h2")]

            summary_content = soup.find("p", {"class": "summary"})
            summary = summary_content.text

            return genres, summary

        self.logger.error("unable to fetch the manga metadata")
        return None
