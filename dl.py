import requests
from bs4 import BeautifulSoup
import time
import os
import argparse
import logging
from requests.exceptions import SSLError

HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

# Add logging to both console and file:
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('errors.log', mode='a', encoding='utf-8')
    ]
)

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

def download_image(img_url, save_dir='downloads', dry_run=False, timeout=10):
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, img_url.split('/')[-1])

    if os.path.exists(filename):
        print(f"Image already exists: {filename}, skipping.")
        return False

    if dry_run:
        print(f"[DRY RUN] Would download: {img_url} -> {filename}")
        return False

    print(f"Downloading: {img_url}")
    try:
        res = requests.get(img_url, headers=HEADERS, timeout=timeout)
        if res.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(res.content)
            print(f"Saved to: {filename}")
            return True
        else:
            err_msg = f"Failed to download image: {img_url} (status: {res.status_code})"
            print(err_msg)
            logging.error(err_msg)
            return False
    except SSLError as ssl_err:
        err_msg = f"SSL error while downloading {img_url}: {ssl_err}. Skipping..."
        print(err_msg)
        logging.warning(err_msg)
    except requests.exceptions.Timeout:
        err_msg = f"Timeout while downloading {img_url}. Skipping..."
        print(err_msg)
        logging.warning(err_msg)
    except Exception as e:
        err_msg = f"Error while downloading {img_url}: {e}. Skipping..."
        print(err_msg)
        logging.error(err_msg)
    return False

def download_gallery_images(base_url, max_pages, save_dir="downloads", dry_run=False, timeout=10):
    image_page_urls = get_image_page_urls(base_url, max_pages)
    print(f"Found {len(image_page_urls)} image pages.")

    for idx, url in enumerate(image_page_urls):
        print(f"[{idx+1}/{len(image_page_urls)}] Getting full image from {url}")
        full_img_url = get_full_image_url(url)
        if full_img_url:
            downloaded = download_image(full_img_url, save_dir=save_dir, dry_run=dry_run, timeout=timeout)
            if downloaded:
                time.sleep(0.5)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='image downloader with dry-run and page limit')
    parser.add_argument('--dry-run', action='store_true', help='Only show what would be downloaded')
    parser.add_argument('--max-pages', type=int, required=True, help='Maximum number of gallery pages to parse')
    parser.add_argument('--base-url', type=str, required=True, help='Gallery base URL')
    parser.add_argument('--save-dir', type=str, default='downloads', help='Directory to save images')
    parser.add_argument('--timeout', type=int, default=10, help='Download timeout in seconds per image')
    args = parser.parse_args()

    download_gallery_images(
        args.base_url,
        args.max_pages,
        save_dir=args.save_dir,
        dry_run=args.dry_run,
        timeout=args.timeout
    )
