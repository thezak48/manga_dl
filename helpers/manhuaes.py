"""
This module defines the Manhuaes class for interacting with the website manhuaes.com.

The Manhuaes class provides methods to fetch manga IDs, chapters, images, 
and metadata from manhuaes.com, and to download manga images and save them as .cbz files.

Classes:
    Manhuaes: A class to interact with the website manhuaes.com.
"""
import concurrent.futures
import logging
import os.path
import shutil
import xml.etree.ElementTree as ET
import zipfile

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class Manhuaes:
    """
    A class to interact with the website manhuaes.com.

    This class provides methods to fetch manga IDs, chapters, images,
    and metadata from manhuaes.com, and to download manga images and save them as .cbz files.

    Attributes:
        logger: An instance of logging.Logger for logging.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_manga_id(self, manga_name: str):
        """
        Get the manga ID for a given manga name.
        """
        result = requests.get(
            url=f"https://manhuaes.com/manga/{manga_name}",
            headers={
                "authority": "manhuaes.com",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            },
            timeout=30,
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")
            node = soup.find("div", {"id": "manga-chapters-holder"})
            if node:
                data_id = node["data-id"]
                node = soup.find("div", {"class": "post-title"})
                title = node.h1
                self.logger.debug("found the following id: %s", data_id)
                return data_id, title.text.lstrip().rstrip()
        self.logger.error("unable to find the manga id needed")
        return None

    def get_manga_chapters(self, manga_id: str):
        """
        Get the manga chapters for a given manga ID.
        """
        result = requests.post(
            url="https://manhuaes.com/wp-admin/admin-ajax.php",
            headers={
                "authority": "manhuaes.com",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": "cf_clearance=m7VNXTw9pXW.TZjAcfE8WugDgdw2lxi7uxJpbR6f84w-1697660577-0-1-fd160a8f.9191ec7.aa17556f-0.2.1697660577; PHPSESSID=rfc7vboe7q7h82e8r3bkms4of9",
                "origin": "https://manhuaes.com",
                "pragma": "no-cache",
                "referer": "https://manhuaes.com/manga/survive-on-a-deserted-island-with-beautiful-girls/",
                "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
            },
            data={"action": "manga_get_chapters", "manga": manga_id},
            timeout=30,
        )
        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")
            nodes = soup.find_all("li", {"class": "wp-manga-chapter"})
            chapters = []

            for node in nodes:
                url = node.a["href"]
                if "/chapter-0" not in url:
                    chapters.append(url)

            chapters.sort(key=lambda url: int(url.split("/chapter-")[-1].split("/")[0]))

            return chapters

        return None

    def get_chapter_images(self, url: str):
        """
        Get the manga chapter images for a given chapter URL.
        """
        result = requests.get(
            url=url,
            headers={
                "authority": "manhuaes.com",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            },
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
            url=f"https://manhuaes.com/manga/{manga_name}",
            headers={
                "authority": "manhuaes.com",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            },
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

    def create_comic_info(self, series, genres, summary, language_iso="en"):
        """
        Create a ComicInfo.xml file for the .cbz file.
        """
        # Create XML elements
        root = ET.Element("ComicInfo")
        ET.SubElement(root, "Series").text = series
        ET.SubElement(root, "Genre").text = ", ".join(genres)
        ET.SubElement(root, "Summary").text = summary
        ET.SubElement(root, "LanguageISO").text = language_iso

        # Create XML tree and write to file
        tree = ET.ElementTree(root)
        tree.write("ComicInfo.xml", encoding="utf-8", xml_declaration=True)

    def download_image(self, image, path):
        """
        Download a single image.
        """
        with open(path, "wb") as writer:
            result = requests.get(
                url=image,
                headers={
                    "authority": "img.manhuaes.com",
                    "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "accept-language": "en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6",
                    "cache-control": "no-cache",
                    "pragma": "no-cache",
                    "referer": "https://manhuaes.com/",
                    "sec-ch-ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "image",
                    "sec-fetch-mode": "no-cors",
                    "sec-fetch-site": "same-site",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                },
                timeout=30,
            )
            if result.status_code == 200:
                writer.write(result.content)
            else:
                self.logger.error("Failed to download image: %s", image)
                return False
        return True

    def download_images(
        self,
        images: list,
        title: str,
        chapter,
        save_location: str,
        series,
        genres,
        summary,
        multi_threaded,
    ):
        """
        Download images for a given manga chapter.
        """
        compelte_dir = os.path.join(save_location, title)
        if not os.path.exists(compelte_dir):
            os.makedirs(compelte_dir)

        tmp_path = os.path.join(save_location, "tmp", title, "Ch. {}".format(chapter))
        completed = True

        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

            self.logger.info("downloading %s Ch. %s", title, chapter)
            paths = [
                os.path.join(tmp_path, "%s.jpg", str(x).zfill(3))
                for x in range(len(images))
            ]

            if multi_threaded:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    results = list(
                        tqdm(
                            executor.map(self.download_image, images, paths),
                            total=len(images),
                            desc="Progress",
                        )
                    )
            else:
                results = [
                    self.download_image(image, path)
                    for image, path in tqdm(
                        zip(images, paths), total=len(images), desc="Progress"
                    )
                ]

            if not all(results):
                self.logger.error("Incomplete download of %s", title)
                completed = False

        if completed:
            self.logger.info("zipping: Ch. %s", chapter)
            self.create_comic_info(series=series, genres=genres, summary=summary)
            self.make_cbz(
                directory_path=tmp_path,
                compelte_dir=compelte_dir,
                output_path=f"{chapter}.cbz",
            )
            shutil.rmtree(tmp_path)
            self.logger.info("done zipping: Ch. %s", chapter)

    def make_cbz(self, directory_path, compelte_dir, output_path):
        """
        Create a .cbz file from a directory.
        """
        output_path = os.path.join(
            compelte_dir, f"{os.path.basename(directory_path)}.cbz"
        )
        zipf = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(
                    os.path.join(root, file), os.path.basename(os.path.join(root, file))
                )

        zipf.write("ComicInfo.xml", "ComicInfo.xml")

        zipf.close()
