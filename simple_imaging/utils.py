from itertools import chain
from typing import List

from .errors import InvalidFileError, InvalidHeaderError
from .image import Image


def get_split_strings(filepath: str) -> List[str]:
    """Utility function to read file contents

    Given a filepath as string, this function will read it's contents
    and split out the values by newlines and spaces. Returns a non-agnostic
    representation of its contents as a list fo strings

    Arguments:
        filepath {str} -- path to the desired file for processing

    Returns:
        List[str] -- representation of file contents as a list fo strings 
    """
    with open(filepath) as f:
        return list(chain.from_iterable(x.strip().split(" ") for x in f))


def read_file(filepath: str) -> Image:
    header, *content = get_split_strings(filepath)  # type: str, List[str]
    acceptable_headers = ("P1", "P2", "P3")
    if header not in acceptable_headers:
        raise InvalidHeaderError(f"Header {header} is not allowed or invalid")
    try:
        # All remaining values should be integers
        m, n, max_grayscale, *data = [
            int(x) for x in content
        ]  # type: int, int, int, List[int]
    except ValueError:
        raise InvalidFileError(f"Found invalid values in file contents")
    if m <= 0 or n <= 0 or max_grayscale <= 0:
        raise InvalidFileError(
            f"Neither m, n or max_grayscale can be negative, found {m=}, {n=}, {max_grayscale=}"
        )
    if len(data) != m * n:
        raise InvalidFileError(
            f"Non-matching amount of pixels found, should have {m*n} values, found {len(data)}"
        )
    else:
        # rearranges data as a MxN matrix
        pixel_data: List[List[int]] = [data[i : i + n] for i in range(0, len(data), n)]
        image = Image(header, max_grayscale, m, n, contents=pixel_data)
        return image


def save_file(filepath: str, image: Image) -> None:
    with open(filepath, "w") as f:
        f.write(f"{image.header}\n")
        f.write(f"{image.m} {image.n}\n")
        f.write(f"{image.max_grayscale}\n")
        for line in image.values:
            str_line = " ".join([str(i) for i in line])
            f.writelines(f"{str_line}\n")
