import argparse

from simple_matrix.matrix import Matrix
from simple_matrix.utils import read_file, save_file


def main(args):
    image = None
    if args.filepath:
        for filepath in args.filepath:
            image = read_file(filepath)
    negative_image = image.negative()
    darken_image = image.darken(50)
    lighten_image = image.lighten(75)
    rotate_90_image = image.rotate_90()
    save_file("negative.pgm", negative_image)
    save_file("darken.pgm", darken_image)
    save_file("light.pgm", lighten_image)
    save_file("rot90.pgm", rotate_90_image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", nargs="+", help="File path for reading")
    parser.add_argument("-o", "--output", help="file path for output")
    args = parser.parse_args()
    main(args)
