from itertools import chain
from typing import Any, Dict, List

from .errors import InvalidConfigsError, InvalidFileError, InvalidHeaderError


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


def parse_file_contents(file_contents: List[str]) -> Dict[str, Any]:
    """Utility function to validate and parse file contents

    Given the file contents as a list of strings, validates the data and raises 
    any errors. If no problems occur, returns the parsed data as a dictionary.

    Args:
        file_contents (List[str]): File contents as a list of strings

    Raises:
        InvalidHeaderError: [description]
        InvalidFileError: [description]
        InvalidConfigsError: [description]
        InvalidFileError: [description]

    Returns:
        Dict[str, Any]: [description]
    """
    header, *contents = file_contents  # type: str, List[str]
    acceptable_headers = ("P1", "P2", "P3")
    if header not in acceptable_headers:
        raise InvalidHeaderError(f"Header {header} is not allowed or invalid")
    try:
        # All remaining values should be integers
        m, n, max_grayscale, *data = [
            int(x) for x in contents
        ]  # type: int, int, int, List[int]
    except ValueError:
        raise InvalidFileError(f"Found invalid values in file contents")
    if m <= 0 or n <= 0 or max_grayscale <= 0:
        raise InvalidConfigsError(
            f"Neither m, n or max_grayscale can be negative or zero, found {m=}, {n=}, {max_grayscale=}"
        )
    if len(data) != m * n:
        raise InvalidFileError(
            f"Non-matching amount of pixels found, should have {m*n} values, found {len(data)}"
        )
    else:
        pixel_data: List[List[int]] = [data[i : i + n] for i in range(0, len(data), n)]
        return {
            "header": header,
            "dimensions": (m, n),
            "max_level": max_grayscale,
            "contents": pixel_data,
        }
