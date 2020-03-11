import argparse

from simple_matrix.matrix import Matrix
from simple_matrix.utils import read_file, save_file


def main(args):
    m1 = None
    m2 = None
    if args.filepath:
        for filepath in args.filepath:
            m1 = read_file(filepath)
    m2 = Matrix(3, 3)
    m2.values = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]

    m = m1.sum(m2)
    print(m)
    save_file("output1.txt", m)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", nargs='+', help="File path for reading")
    parser.add_argument("-o","--output", help="file path for output")
    args = parser.parse_args()
    main(args)
