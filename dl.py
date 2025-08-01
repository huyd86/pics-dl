import requests
from bs4 import BeautifulSoup
import time
import os
import argparse

BASE_URL = 'https://e-hentai.org/g/218789/d4618202db/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

def get_image_page_urls(gallery_base_url, max_pages):
    all_image_pages = []

    for page in range(max_pages):
        url = f'{gallery_base_url}?p={page}'
        print(f"Parsing gallery page {page} -> {url}")
        res = requests.get(url, headers=HEADERS)

        if res.status_code != 200:
            print(f"Failed to load page: {res.status_code}")
            break

        soup = BeautifulSoup(res.text, 'html.parser')
        thumbs = soup.select('div#gdt > a')

        if not thumbs:
            print("No thumbnails found on this page — stopping.")
            break

        page_urls = [a['href'] for a in thumbs]
        all_image_pages.extend(page_urls)
        time.sleep(0.5)

    return all_image_pages

def get_full_image_url(image_page_url):
    res = requests.get(image_page_url, headers=HEADERS)
    if res.status_code != 200:
        print(f"Failed to load image page: {image_page_url}")
        return None

    soup = BeautifulSoup(res.text, 'html.parser')
    img = soup.select_one('img#img')
    return img['src'] if img else None

def download_image(img_url, save_dir='downloads', dry_run=False):
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, img_url.split('/')[-1])

    if dry_run:
        print(f"[DRY RUN] Would download: {img_url} -> {filename}")
    else:
        print(f"Downloading: {img_url}")
        res = requests.get(img_url, headers=HEADERS)
        if res.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(res.content)
            print(f"Saved to: {filename}")
        else:
            print(f"Failed to download image: {img_url}")

def download_gallery_images(BASE_URL, max_pages, save_dir="downloads", dry_run=False):
    image_page_urls = get_image_page_urls(BASE_URL, max_pages)
    print(f"Found {len(image_page_urls)} image pages.")

    for idx, url in enumerate(image_page_urls):
        print(f"[{idx+1}/{len(image_page_urls)}] Getting full image from {url}")
        full_img_url = get_full_image_url(url)
        if full_img_url:
            download_image(full_img_url, save_dir=save_dir, dry_run=dry_run)
            if not dry_run:
                time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='image downloader with dry-run and page limit')
    parser.add_argument('--dry-run', action='store_true', help='Only show what would be downloaded')
    parser.add_argument('--max-pages', type=int, required=True, help='Maximum number of gallery pages to parse')
    parser.add_argument('--base-url', type=str, default=BASE_URL, help='Gallery base URL')
    parser.add_argument('--save-dir', type=str, default='downloads', help='Directory to save images')
    args = parser.parse_args()

    download_gallery_images(args.base_url, args.max_pages, save_dir=args.save_dir, dry_run=args.dry_run)
