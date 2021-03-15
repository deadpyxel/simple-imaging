import argparse
import os

from simple_imaging.image import read_file
from simple_imaging.image import save_file


def main(args):
    image = None
    if args.filepath:
        for filepath in args.filepath:
            image = read_file(filepath)
    if args.output:
        output_dir = args.output
    result = image.average_filter(kernel=15).binarization(
        threshold=64, inplace=False
    )
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    save_file(f"{output_dir}/atv05/hubble_avg15_bin.pgm", result)


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
