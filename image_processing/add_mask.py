from PIL import Image
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mask", type=str, help="path to masks directory")
    parser.add_argument("-p", "--path", type=str, help="path to directory with images to be combined")
    parser.add_argument("-o", "--output", type=str, help="path to output directory")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    masks = {}
    for mask_file in os.listdir(args.mask):
        mask = Image.open(os.path.join(args.mask, mask_file)).convert("RGBA")
        masks[mask_file.split('_')[0]] = mask

    # fix directories
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    for f in os.listdir(args.path):
        if f.endswith(('.jpg', '.png')):
            camera_image = Image.open(os.path.join(args.path, f)).convert("RGBA")
            for cam in masks:
                if cam in f:
                    mask_image = Image.alpha_composite(camera_image, masks[cam])
                    mask_image.save(os.path.join(args.output, f), "PNG")