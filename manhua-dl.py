import os
import requests
from bs4 import BeautifulSoup
import zipfile
import re
import shutil
from tqdm.auto import tqdm

def extract_image_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    divs = soup.find_all('div', {'class': 'page-break no-gaps'})
    image_links = []

    for div in divs:
        images = div.find_all('img')
        for image in images:
            if image.has_attr('data-src'): 
                image_links.append(image['data-src'])
            elif image.has_attr('src'):
                image_links.append(image['src'])

    return image_links

def download_images(image_links, download_path):
    if not os.path.exists(download_path): 
        os.makedirs(download_path)  

    for i, url in enumerate(image_links):
        response = requests.get(url, stream=True)
        
        file_size = int(response.headers.get('Content-Length', 0))
        base_url_removed = url.replace('https://img.manhuaes.com/', '')  # remove base_url
        page = re.sub(r'[^/]*/[^/]*/', '', base_url_removed).replace('.jpg', '')  # remove everything up to the second '/'
        progress = tqdm(response.iter_content(1024), f'Downloading: Chapter {chapter_num} Page {page}', total=file_size, unit='B', unit_scale=True, unit_divisor=1024, leave=True, bar_format='{l_bar}{bar:20}{r_bar}{bar:-10b}')

        with open(f'{download_path}/image{i}.jpg', 'wb') as fd:
            for data in progress.iterable:
                fd.write(data)
                progress.update(len(data))

def make_cbz(directory_path, output_path):
    zipf = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.basename(os.path.join(root, file)))

    zipf.close()

def remove_directory(directory_path):
    shutil.rmtree(directory_path)

def extract_chapter_number(url):
    pattern = r'/chapter-(\d+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise Exception("URL does not contain a valid chapter number")

def extract_manga_name(url):
    pattern = r'manga/(.*?)/'
    match = re.search(pattern, url)
    if match:
        return match.group(1).replace('-', ' ').title()
    else:
        raise Exception("URL does not contain a valid manga name")

def get_starting_chapter_num(directory_path):
    existing_files = os.listdir(directory_path)
    cbz_files = [file for file in existing_files if file.endswith('.cbz')]
    if not cbz_files:  # if no .cbz files found, return 1
        return 1
    chapter_nums = [int(re.search(r'Ch\. (\d+)', file).group(1)) for file in cbz_files]
    return max(chapter_nums) + 1

with open('/mnt/data/media/manga/urls.txt', 'r') as f:
    urls = [line.strip() for line in f]

for base_url in urls:
    manga_name = extract_manga_name(base_url)
    output_folder_path = f'/mnt/data/media/manga/{manga_name}'

    chapter_num = get_starting_chapter_num(output_folder_path)
    while True:
        print(f'Downloading chapter {chapter_num}...')
        url = base_url + "chapter-" + str(chapter_num)
        image_links = extract_image_links(url)

        if not image_links:  # if no image links found, stop the loop
            break

        download_path = f'/mnt/data/media/manga/{manga_name}/Chapter_{chapter_num}_Images'
        output_path = f'/mnt/data/media/manga/{manga_name}/Ch. {extract_chapter_number(url)}.cbz'

        download_images(image_links, download_path)
        make_cbz(download_path, output_path)

        remove_directory(download_path)

        print(f'Finished downloading chapter {chapter_num}')

        chapter_num += 1  # increase the chapter number for the next iteration