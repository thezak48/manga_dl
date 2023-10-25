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

    def get_manga_id(self, manga_name):
        """Get the series title for a given URL."""
        manga_id = manga_name
        response = requests.get(manga_id, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        title_id = (
            soup.find(class_="subj")
            .get_text(separator=" ")
            .replace("\n", "")
            .replace("\t", "")
        )
        return manga_id, title_id

    def get_chapter_viewer_url(self, manga_id):
        """Get the chapter viewer URL for a given URL."""
        response = requests.get(manga_id, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        chapter_viewer = soup.find("li", {"class": "_episodeItem"})
        if chapter_viewer:
            viewer_url = chapter_viewer.find("a")
            return viewer_url.get("href") if viewer_url else None
        return None

    def get_first_chapter_episode_no(self, manga_id):
        """
        Get the first chapter episode number for a given manga ID.
        """
        try:
            response = requests.get(manga_id, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            href = soup.find("a", id="_btnEpisode")["href"]
            return int(parse_qs(urlparse(href).query)["episode_no"][0])
        except (TypeError, KeyError):
            response = requests.get(f"{manga_id}&page=9999", timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            return min(
                int(episode["data-episode-no"])
                for episode in soup.find_all("li", {"class": "_episodeItem"})
            )

    def get_manga_chapters(self, manga_id):
        """
        Get the manga chapters for a given manga ID.
        """
        first_chapter = self.get_first_chapter_episode_no(manga_id)
        viewer_url = self.get_chapter_viewer_url(manga_id)
        if viewer_url:
            parsed = urlparse(viewer_url)
            params = parse_qs(parsed.query)
            episode_no = int(params.get("episode_no", [None])[0])
            chapters = []

            for i in range(first_chapter, episode_no + 1):
                chapter_viewer_url = viewer_url.replace(
                    f"/episode-{params['episode_no'][0]}", f"/episode-{i}"
                ).replace(f"&episode_no={params['episode_no'][0]}", f"&episode_no={i}")
                chapters.append(chapter_viewer_url)

            return chapters

        return None

    def get_chapter_images(self, url: str):
        """
        Get the manga chapter images for a given chapter URL.
        """
        result = requests.get(
            url=url,
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

    def get_manga_metadata(self, manga_name: str):
        """
        Get the manga metadata for a given manga name.
        """
        result = requests.get(
            url=manga_name,
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
