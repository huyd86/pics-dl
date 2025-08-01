import os
import numpy as np
from PIL import Image, ImageOps
import imageio
from tqdm import tqdm
import argparse

def create_gif(
    image_folder,
    output_path,
    fps=10,
    resize=None,
    sort_key=None,
    padding_color=(0, 0, 0)
):
    """
    Create a GIF from images in a folder.

    Parameters:
    - image_folder: path to folder containing images
    - output_path: output .gif file path
    - fps: frames per second
    - resize: (width, height) tuple to resize+pad frames to a fixed size
    - sort_key: optional function to sort file names
    - padding_color: background color for padding (R, G, B)
    """
    images = [f for f in os.listdir(image_folder)
              if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not images:
        print("No valid image files found in folder.")
        return

    if sort_key:
        images.sort(key=sort_key)
    else:
        images.sort()

    frames = []

    try:
        resample = Image.Resampling.LANCZOS
    except AttributeError:
        resample = Image.ANTIALIAS

    print(f"🖼️ Processing {len(images)} images...")

    for fname in tqdm(images, desc="Resizing & padding"):
        path = os.path.join(image_folder, fname)
        img = Image.open(path).convert("RGB")

        if resize:
            max_w, max_h = resize
            orig_w, orig_h = img.size
            ratio = min(max_w / orig_w, max_h / orig_h)
            new_w, new_h = int(orig_w * ratio), int(orig_h * ratio)
            img_resized = img.resize((new_w, new_h), resample)

            canvas = Image.new("RGB", (max_w, max_h), padding_color)
            offset = ((max_w - new_w) // 2, (max_h - new_h) // 2)
            canvas.paste(img_resized, offset)
            final_img = canvas
        else:
            final_img = img

        frames.append(np.array(final_img))

    print("🌀 Creating GIF...")
    with imageio.get_writer(output_path, mode='I', fps=fps) as writer:
        for frame in tqdm(frames, desc="Writing frames"):
            writer.append_data(frame)

    print(f"✅ GIF saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a GIF from images in a folder.")
    parser.add_argument("--image_folder", type=str, default="downloads",
                        help="Path to the folder containing images")
    parser.add_argument("--output", type=str, default="output.gif",
                        help="Output GIF file path")
    parser.add_argument("--fps", type=int, default=1,
                        help="Frames per second")
    parser.add_argument("--resize", nargs=2, type=int, metavar=('width', 'height'),
                        default=[512, 512],
                        help="Resize images to WIDTH HEIGHT (default: 512 512)")
    parser.add_argument("--padding_color", nargs=3, type=int, metavar=('R', 'G', 'B'), default=[0, 0, 0],
                        help="RGB padding color (e.g., --padding_color 0 0 0)")

    args = parser.parse_args()

    create_gif(
        image_folder=args.image_folder,
        output_path=args.output,
        fps=args.fps,
        resize=tuple(args.resize) if args.resize else None,
        padding_color=tuple(args.padding_color),
    )
