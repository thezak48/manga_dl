""" Module for handling mangadex """ ""
import json
import re
import time
import requests


class Mangadex:
    """Class for handling mangadex"""

    base_headers = {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ),
    }

    headers_image = base_headers.copy()

    uuid_pattern = (
        r"([0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})"
    )

    def __init__(self, logger):
        self.logger = logger

    def get_manga_title(self, manga_id):
        """Get the manga title from the manga id"""
        try:
            while True:
                result = requests.get(
                    f"https://api.mangadex.org/manga/{manga_id}",
                    headers=self.base_headers,
                    timeout=30,
                )
                if result.status_code == 429:
                    self.logger.info("Rate limited, waiting 20 seconds")
                    time.sleep(20)
                    continue
                result.raise_for_status()
                break

            data = result.json()
            attributes = data.get("data", {}).get("attributes", {})
            alt_titles = attributes.get("altTitles", [])
            main_title = attributes.get("title", {}).get("en", "")

            short_title = min(
                (alt for alt in alt_titles if "en" in alt),
                key=lambda x: len(x["en"]),
                default={"en": main_title},
            ).get("en")

            self.logger.debug("Found the following title: %s", short_title)
            return short_title

        except Exception as e:
            self.logger.error(f"Unable to find the manga title on {manga_url}")
            self.logger.error(e)

            return None

    def get_manga_chapters(self, manga_url):
        """Get the manga chapters from the manga url"""
        chapters = []

        try:
            self.logger.info("Getting manga chapters")
            match = re.search(self.uuid_pattern, manga_url)
            manga_id = match.group(1) if match else None
            self.logger.debug("Found the following manga id: %s", manga_id)
            title = self.get_manga_title(manga_id)
            while True:
                result = requests.get(
                    f"https://api.mangadex.org/manga/{manga_id}/feed?limit=500&translatedLanguage%5B%5D=en&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&contentRating%5B%5D=pornographic&includeFutureUpdates=1&order%5Bchapter%5D=asc",
                    headers=self.base_headers,
                    timeout=30,
                )
                if result.status_code == 429:
                    self.logger.info("Rate limited, waiting 20 seconds")
                    time.sleep(20)
                    continue
                result.raise_for_status()
                break

            data = result.json()
            for chap in data.get("data", []):
                if "chapter" in chap["attributes"]:
                    chapter_number = chap["attributes"]["chapter"]
                    id = chap["id"]
                    chapters.append((chapter_number, id))

            def chapter_sort_key(chapter):
                return float(chapter[0])

            chapters.sort(key=chapter_sort_key)

            return chapters, title

        except Exception as e:
            self.logger.error(f"Unable to find the manga chapters for {manga_url}")
            self.logger.error(e)

            return None

    def get_chapter_images(self, chapter_id):
        """Get the chapter images from the chapter id"""
        try:
            self.logger.info("Getting chapter images for %s", chapter_id)
            while True:
                result = requests.get(
                    f"https://api.mangadex.org/at-home/server/{chapter_id}",
                    headers=self.base_headers,
                    timeout=30,
                )
                if result.status_code == 429:
                    self.logger.info("Rate limited, waiting 20 seconds")
                    time.sleep(20)
                    continue
                result.raise_for_status()
                break

            data = result.json()
            base_url = data.get("baseUrl")
            chapter_hash = data["chapter"]["hash"]
            filenames = data["chapter"]["data"]

            images = [
                f"{base_url}/data/{chapter_hash}/{filename}" for filename in filenames
            ]

            return images

        except Exception as e:
            self.logger.error(f"Unable to find the chapter images for {chapter_id}")
            self.logger.error(e)

            return None

    def get_manga_metadata(self, manga_url):
        """Get the manga metadata from the manga url"""
        try:
            self.logger.info("Getting manga metadata")
            match = re.search(self.uuid_pattern, manga_url)
            manga_id = match.group(1) if match else None
            self.logger.debug("Found the following manga id: %s", manga_id)
            while True:
                result = requests.get(
                    f"https://api.mangadex.org/manga/{manga_id}",
                    headers=self.base_headers,
                    timeout=30,
                )
                if result.status_code == 429:
                    self.logger.info("Rate limited, waiting 20 seconds")
                    time.sleep(20)
                    continue
                result.raise_for_status()
                break

            data = result.json()
            attributes = data.get("data", {}).get("attributes", {})
            tags = attributes.get("tags", [])
            genres = [tag["attributes"]["name"]["en"] for tag in tags]
            summary = attributes.get("description", {}).get("en", "")

            return genres, summary

        except Exception as e:
            self.logger.error(f"Unable to find the manga metadata for {manga_url}")
            self.logger.error(e)

            return None
