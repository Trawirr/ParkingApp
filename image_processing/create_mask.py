from PIL import Image, ImageDraw
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="path to json file containing mask polygons")
    parser.add_argument("-o", "--output", type=str, help="path to output jpg file")
    parser.add_argument('-s', '--size', nargs='+', type=int, help="size of image")
    parser.add_argument('-c', '--color', nargs='+', type=int, help="color of mask")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    color = tuple(args.color + [255])
    print(f"{color=}")
    mask_image = Image.new("RGBA", args.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask_image)

    with open(args.path, 'r') as f:
        json_data = json.load(f)

    for mask in json_data['objects']:
        points = [tuple(int(pp) for pp in p) for p in mask['points']]
        print(f"{points=}")
        draw.polygon(points, fill=color)

    mask_image.save(args.output, "JPG")
    print(f"Image saved as {args.output}")
