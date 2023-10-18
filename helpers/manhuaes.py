import logging
import os.path
import shutil
import zipfile

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class Manhuaes:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_manga_id(self, manga_name: str):
        result = requests.get(
            url='https://manhuaes.com/manga/{}'.format(manga_name),
            headers={
                'authority': 'manhuaes.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
            }
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, 'html.parser')
            node = soup.find('div', {'id': 'manga-chapters-holder'})
            if node:
                data_id = node['data-id']
                node = soup.find('div', {'class': 'post-title'})
                title = node.h1
                self.logger.debug('found the following id: {}'.format(data_id))
                return data_id, title.text.lstrip().rstrip()
        self.logger.error('unable to find the manga id needed')
        return None

    def get_manga_chapters(self, manga_id: str):
        result = requests.post(
            url='https://manhuaes.com/wp-admin/admin-ajax.php',
            headers={
                  'authority': 'manhuaes.com',
                  'accept': '*/*',
                  'accept-language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6',
                  'cache-control': 'no-cache',
                  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                  'cookie': 'cf_clearance=m7VNXTw9pXW.TZjAcfE8WugDgdw2lxi7uxJpbR6f84w-1697660577-0-1-fd160a8f.9191ec7.aa17556f-0.2.1697660577; PHPSESSID=rfc7vboe7q7h82e8r3bkms4of9',
                  'origin': 'https://manhuaes.com',
                  'pragma': 'no-cache',
                  'referer': 'https://manhuaes.com/manga/survive-on-a-deserted-island-with-beautiful-girls/',
                  'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                  'sec-ch-ua-mobile': '?0',
                  'sec-ch-ua-platform': '"Windows"',
                  'sec-fetch-dest': 'empty',
                  'sec-fetch-mode': 'cors',
                  'sec-fetch-site': 'same-origin',
                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                  'x-requested-with': 'XMLHttpRequest'
            },
            data={
                'action': 'manga_get_chapters',
                'manga': manga_id
            }
        )
        if result.status_code == 200:
            soup = BeautifulSoup(result.text, 'html.parser')
            nodes = soup.find_all('li', {'class': 'wp-manga-chapter'})
            chapters = []

            for node in nodes:
                chapters.append(node.a['href'])

            return chapters

        return None

    def get_chapter_images(self, url: str):

        result = requests.get(
            url=url,
            headers={
              'authority': 'manhuaes.com',
              'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
              'accept-language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6',
              'cache-control': 'no-cache',
              'pragma': 'no-cache',
              'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
              'sec-ch-ua-mobile': '?0',
              'sec-ch-ua-platform': '"Windows"',
              'sec-fetch-dest': 'document',
              'sec-fetch-mode': 'navigate',
              'sec-fetch-site': 'none',
              'sec-fetch-user': '?1',
              'upgrade-insecure-requests': '1',
              'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
            }
        )

        if result.status_code == 200:
            soup = BeautifulSoup(result.text, 'html.parser')
            node = soup.find('div', {'class': 'reading-content'})
            image_nodes = node.find_all('img')
            images = []
            for image_node in image_nodes:
                images.append(image_node['data-src'].lstrip().rstrip())

            return images

    def download_images(self, images: list, title: str):
        if os.path.exists('{}.cbz'.format(title)):
            self.logger.warning('{} already exists, skipping'.format(title))
        if not os.path.exists(title):
            os.makedirs(title)
        completed = True
        self.logger.info('downloading {}'.format(title))
        for x in tqdm(range(len(images)), desc='Progress'):
            image = images[x]

            with open(os.path.join(title, '{} Page {}.jpg'.format(
                title,
                str(x).zfill(3)
            )), 'wb') as writer:

                result = requests.get(
                    url=image,
                    headers={
                      'authority': 'img.manhuaes.com',
                      'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                      'accept-language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,en-GB-oxendict;q=0.6',
                      'cache-control': 'no-cache',
                      'pragma': 'no-cache',
                      'referer': 'https://manhuaes.com/',
                      'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                      'sec-ch-ua-mobile': '?0',
                      'sec-ch-ua-platform': '"Windows"',
                      'sec-fetch-dest': 'image',
                      'sec-fetch-mode': 'no-cors',
                      'sec-fetch-site': 'same-site',
                      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
                    }
                )
                if result.status_code == 200:
                    writer.write(result.content)
                else:
                    self.logger.error('incomplete download of {}'.format(title))
                    completed = False
                    break

        if completed:
            self.logger.info('zipping: {}'.format(title))
            self.make_cbz(
                directory_path=title,
                output_path='{}.cbz'.format(title)
            )
            shutil.rmtree(title)
            self.logger.info('done zipping: {}'.format(title))
    def make_cbz(self, directory_path, output_path):
        # TODO add manga metadata, somehow
        zipf = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.basename(os.path.join(root, file)))

        zipf.close()