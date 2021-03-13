from itertools import chain
from typing import Any
from typing import Dict
from typing import List
from typing import TextIO
from typing import Tuple
from typing import TypeVar

from .errors import InvalidConfigsError
from .errors import InvalidFileError
from .errors import InvalidHeaderError
from .types import GrayPixel
from .types import RGBPixel


def get_split_strings(file_contents: TextIO) -> List[str]:
    """Utility function to read file contents

    Given a filepath as string, this function will read it's contents
    and split out the values by newlines and spaces. Returns a non-agnostic
    representation of its contents as a list of strings

    Arguments:
        filepath {str} -- path to the desired file for processing

    Returns:
        List[str] -- representation of file contents as a list of strings.
    """
    return list(chain.from_iterable(x.strip().split() for x in file_contents))


def _extract_header(file_contents: List[str]) -> Tuple[str, List[str]]:
    header, contents = _extract_first_element(file_contents)  # type: str, List[str]
    acceptable_headers = ("P1", "P2", "P3")
    if header not in acceptable_headers:
        raise InvalidHeaderError(f"Header {header} is not allowed or invalid")
    return header, contents


def _extract_dimensions(file_contents: List[str]) -> Tuple[int, int, List[int]]:
    try:
        # All remaining values should be integers
        x, y, *contents = [int(x) for x in file_contents]  # type: int, int, List[int]
    except ValueError:
        raise InvalidFileError("Found invalid values (non-numerical) in file contents")
    if x <= 0 or y <= 0:
        raise InvalidConfigsError(
            f"Neither of the dimensions can be negative or zero, found {x=}, {y=}"
        )
    return x, y, contents


T = TypeVar("T")


def _extract_first_element(file_contents: List[T]) -> Tuple[T, List[T]]:
    first_element, *remaining_data = file_contents
    return first_element, remaining_data


def _convert_into_tuples(value_list: List[int]) -> List[Tuple[int, int, int]]:
    return [
        (value_list[i], value_list[i + 1], value_list[i + 2])
        for i in range(0, len(value_list), 3)
    ]


def _format_pixel_data(data: List[T], m: int) -> List[List[T]]:
    return [data[i : i + m] for i in range(0, len(data), m)]


def _validate_data_length(data_length: int, desired_length: int) -> bool:
    if data_length != desired_length:
        raise InvalidFileError(
            f"Non-matching amount of pixels found, should have {desired_length} values, found {data_length}"
        )
    return True


def _generate_pixel_matrix_grayscale(
    pixel_data: List[List[int]], x: int, y: int
) -> List[List[GrayPixel]]:
    pixel_matrix = []
    for line in pixel_data:
        pixel_line = [GrayPixel(value) for value in line]
        pixel_matrix.append(pixel_line)
    return pixel_matrix
    # return [[GrayPixel(pixel_data[i][j]) for i in range(y)] for j in range(x)]


def _generate_pixel_matrix_rgb(
    pixel_data: List[List[Tuple[int, int, int]]], x: int, y: int
) -> List[List[RGBPixel]]:
    return [[RGBPixel(**pixel_data[i][j]) for i in range(x)] for j in range(y)]


Pixel = TypeVar("Pixel", int, Tuple[int, int, int])


def _validate_max_value(max_value: Pixel) -> bool:
    if isinstance(max_value, int):
        return max_value > 0
    elif isinstance(max_value, tuple):
        return all(v > 0.0 for v in max_value)
    else:
        raise TypeError(
            f"max_level can only be represented by an integer or a triple of integer (int, int, int), found {type(max_value)}"
        )


def _extract_max_level(value_data: List[Pixel]) -> Tuple[Pixel, List[Pixel]]:
    max_level, data = _extract_first_element(value_data)
    if not _validate_max_value(max_level):
        raise InvalidConfigsError(
            f"max_level cannot be negative or zero, found {max_level=}"
        )
    return max_level, data


def _parse_value_data_grayscale(value_data: List[int], x: int, y: int):
    max_level, data = _extract_max_level(value_data)  # type: int, List[int]
    _validate_data_length(data_length=len(data), desired_length=x * y)
    pixel_data = _format_pixel_data(data, x)
    pixel_matrix = _generate_pixel_matrix_grayscale(pixel_data, x, y)
    return max_level, pixel_matrix


def _parse_value_data_rgb(value_data: List[Tuple[int, int, int]], x: int, y: int):
    max_level, data = _extract_max_level(
        value_data
    )  # type: Tuple[int, int, int], List[Tuple[int, int, int]]
    _validate_data_length(data_length=len(data), desired_length=x * y)
    pixel_data = _format_pixel_data(data, x)
    pixel_matrix = _generate_pixel_matrix_rgb(pixel_data, x, y)
    return max_level, pixel_matrix


def parse_file_contents(file_contents: List[str]) -> Dict[str, Any]:
    """Utility function to validate and parse file contents

    Given the file contents as a list of strings, validates the data and raises
    any errors. If no problems occur, returns the parsed data as a dictionary.

    Args:
        file_contents (List[str]): File contents as a list of strings

    Raises:
        InvalidConfigsError: [description]
        InvalidFileError: [description]

    Returns:
        Dict[str, Any]: [description]
    """
    header, contents = _extract_header(file_contents)  # type: str, List[str]
    x, y, value_data = _extract_dimensions(contents)  # type: int, int, List[int]
    if header in ("P1", "P2"):
        max_level, pixel_data = _parse_value_data_grayscale(value_data, x, y)
    elif header == "P3":
        data_rbg = _convert_into_tuples(value_data)  # type: List[Tuple[int, int, int]]
        max_level, pixel_data = _parse_value_data_rgb(data_rbg, x, y)
    return {
        "header": header,
        "dimensions": (x, y),
        "max_level": max_level,
        "contents": pixel_data,
    }
