import os
import csv

from dl import download_gallery_images
from cvrt_gif import create_gif

def safe_dirname(name):
    # Make a safe directory name for output, based on gif name
    return os.path.splitext(name)[0]

def process_row(url, max_pages, gif_name):
    out_dir = safe_dirname(gif_name)
    print(f"\n--- Processing {url} (pages: {max_pages}) -> {gif_name} ---")
    download_gallery_images(url, int(max_pages), save_dir=out_dir, dry_run=False)
    create_gif(
        image_folder=out_dir,
        output_path=gif_name,
        resize=(512, 512),
        fps=1,              # Adjust as necessary
        chunk_size=180,
        padding_color=(0,0,0)
    )
    print(f"GIF created: {gif_name}\n")

def main(urls_txt_path='urls.txt'):
    with open(urls_txt_path, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 3: continue
            url, max_pages, gif_name = [x.strip() for x in row[:3]]
            process_row(url, max_pages, gif_name)

if __name__ == '__main__':
    main('urls.txt')