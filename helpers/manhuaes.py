import logging
import os.path
import shutil
import zipfile

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import xml.etree.ElementTree as ET


class Manhuaes:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_manga_id(self, manga_name: str):
        result = requests.get(
            url="https://manhuaes.com/manga/{}".format(manga_name),
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
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")
            node = soup.find("div", {"id": "manga-chapters-holder"})
            if node:
                data_id = node["data-id"]
                node = soup.find("div", {"class": "post-title"})
                title = node.h1
                self.logger.debug("found the following id: {}".format(data_id))
                return data_id, title.text.lstrip().rstrip()
        self.logger.error("unable to find the manga id needed")
        return None

    def get_manga_chapters(self, manga_id: str):
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
        )
        if result.status_code == 200:
            soup = BeautifulSoup(result.text, "html.parser")
            nodes = soup.find_all("li", {"class": "wp-manga-chapter"})
            chapters = []

            for node in nodes:
                chapters.append(node.a["href"])

            return chapters

        return None

    def get_chapter_images(self, url: str):
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
        result = requests.get(
            url="https://manhuaes.com/manga/{}".format(manga_name),
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
        # Create XML elements
        root = ET.Element("ComicInfo")
        ET.SubElement(root, "Series").text = series
        ET.SubElement(root, "Genre").text = ", ".join(genres)
        ET.SubElement(root, "Summary").text = summary
        ET.SubElement(root, "LanguageISO").text = language_iso

        # Create XML tree and write to file
        tree = ET.ElementTree(root)
        tree.write("ComicInfo.xml", encoding="utf-8", xml_declaration=True)

    def download_images(
        self, images: list, title: str, save_location: str, series, genres, summary
    ):
        compelte_dir = os.path.join(save_location, title)
        if os.path.exists(os.path.join(compelte_dir, "{}.cbz".format(title))):
            self.logger.warning("{} already exists, skipping".format(title))
        if not os.path.exists(compelte_dir):
            os.makedirs(compelte_dir)

        tmp_path = os.path.join(save_location, "tmp", title)

        completed = True
        self.logger.info("downloading {}".format(title))

        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

        for x in tqdm(range(len(images)), desc="Progress"):
            image = images[x]

            with open(
                os.path.join(tmp_path, "{} Page {}.jpg".format(title, str(x).zfill(3))),
                "wb",
            ) as writer:
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
                )
                if result.status_code == 200:
                    writer.write(result.content)
                else:
                    self.logger.error("incomplete download of {}".format(title))
                    completed = False
                    break

        if completed:
            self.logger.info("zipping: {}".format(title))
            self.create_comic_info(series=series, genres=genres, summary=summary)
            self.make_cbz(
                directory_path=tmp_path,
                compelte_dir=compelte_dir,
                output_path="{}.cbz".format(title),
            )
            shutil.rmtree(tmp_path)
            self.logger.info("done zipping: {}".format(title))

    def make_cbz(self, directory_path, compelte_dir, output_path):
        output_path = os.path.join(
            compelte_dir, "{}.cbz".format(os.path.basename(directory_path))
        )
        zipf = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(
                    os.path.join(root, file), os.path.basename(os.path.join(root, file))
                )

        zipf.write("ComicInfo.xml", "ComicInfo.xml")

        zipf.close()
