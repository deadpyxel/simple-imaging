import argparse
import os

from simple_imaging.utils import read_file, save_file


def main(args):
    image = None
    if args.filepath:
        for filepath in args.filepath:
            image = read_file(filepath)
    if args.output:
        output_dir = args.output
    negative_image = image.negative()
    darken_image = image.darken(50)
    lighten_image = image.lighten(50)
    rotate_90_image = image.rotate_90()
    rotate_90_counter_image = image.rotate_90(clockwise=False)
    rotate_180_image = image.rotate_180()
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    save_file(f"{output_dir}/negative.pgm", negative_image)
    save_file(f"{output_dir}/darken.pgm", darken_image)
    save_file(f"{output_dir}/light.pgm", lighten_image)
    save_file(f"{output_dir}/rot90.pgm", rotate_90_image)
    save_file(f"{output_dir}/rot90counter.pgm", rotate_90_counter_image)
    save_file(f"{output_dir}/rot180.pgm", rotate_180_image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", nargs="+", help="Input file for reading")
    parser.add_argument(
        "-o",
        "--output",
        help="folder to use for output, defaults to output and will create itif doesn't exists",
        default="output",
    )
    args = parser.parse_args()
    main(args)
