import argparse

from simple_imaging.image import read_file
from simple_imaging.image import save_file


def main(args):
    image = None
    if args.filepath:
        for filepath in args.filepath:
            image = read_file(filepath)
    if args.output:
        output_dir = args.output

    # processamentos em cadeia
    result = image.laplacian_filter().high_boost_filter(k=1.5).histogram_equalization()

    # escrita do resultado
    save_file(f"{output_dir}/result.pgm", result)


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
