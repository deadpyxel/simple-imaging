from itertools import chain
from typing import Any, Dict, List, TextIO, Tuple, TypeVar, Union

from .errors import InvalidConfigsError, InvalidFileError, InvalidHeaderError


def get_split_strings(file_contents: TextIO) -> List[str]:
    """Utility function to read file contents

    Given a filepath as string, this function will read it's contents
    and split out the values by newlines and spaces. Returns a non-agnostic
    representation of its contents as a list fo strings

    Arguments:
        filepath {str} -- path to the desired file for processing

    Returns:
        List[str] -- representation of file contents as a list fo strings 
    """
    return list(chain.from_iterable(x.strip().split() for x in file_contents))


def _extract_header(file_contents: List[str]) -> Tuple[str, List[str]]:
    header, *contents = file_contents  # type: str, List[str]
    acceptable_headers = ("P1", "P2", "P3")
    if header not in acceptable_headers:
        raise InvalidHeaderError(f"Header {header} is not allowed or invalid")
    return header, contents


def _extract_dimensions(file_contents: List[str]) -> Tuple[int, int, List[int]]:
    try:
        # All remaining values should be integers
        m, n, *contents = [int(x) for x in file_contents]  # type: int, int, List[int]
    except ValueError:
        raise InvalidFileError(f"Found invalid values (non-numerical) in file contents")
    return m, n, contents


T = TypeVar("T")


def _extract_max_level(file_contents: List[T]) -> Tuple[T, List[T]]:
    max_level, *pixel_data = file_contents
    return max_level, pixel_data


def _convert_into_tuples(value_list: List[int]) -> List[Tuple[int, int, int]]:
    return [
        (value_list[i], value_list[i + 1], value_list[i + 2])
        for i in range(0, len(value_list), 3)
    ]


def _format_pixel_data(data: List[T], m: int) -> List[List[T]]:
    return [data[i : i + m] for i in range(0, len(data), m)]


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
    m, n, value_contents = _extract_dimensions(contents)  # type: int, int, List[int]
    max_level, data = _extract_max_level(value_contents)  # type: int, List[int]
    if m <= 0 or n <= 0 or max_level <= 0:
        raise InvalidConfigsError(
            f"Neither m, n or max_level can be negative or zero, found {m=}, {n=}, {max_level=}"
        )
    if len(data) != m * n:
        raise InvalidFileError(
            f"Non-matching amount of pixels found, should have {m*n} values, found {len(data)}"
        )
    pixel_data: List[List[int]] = _format_pixel_data(data, m)
    return {
        "header": header,
        "dimensions": (m, n),
        "max_level": max_level,
        "contents": pixel_data,
    }
