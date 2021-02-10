import io
from typing import Any
from typing import Dict
from typing import List

import pytest

from .fixtures import blank_image
from simple_imaging.errors import InvalidConfigsError
from simple_imaging.errors import InvalidFileError
from simple_imaging.errors import InvalidHeaderError
from simple_imaging.errors import ValidationError
from simple_imaging.image import Image
from simple_imaging.image import read_file
from simple_imaging.image import save_file
from simple_imaging.types import GrayPixel
from simple_imaging.utils import get_split_strings
from simple_imaging.utils import parse_file_contents


@pytest.fixture
def expected_file_data(x: int, y: int) -> Dict[str, Any]:
    return {
        "header": "P2",
        "dimensions": (x, y),
        "max_level": 255,
        "contents": [[GrayPixel(1) for _ in range(x)] for _ in range(y)],
    }


@pytest.fixture
def good_file_content(x: int, y: int) -> List[str]:
    f_contents = ["P2", str(x), str(y), "255"]
    f_contents.extend(["1" for _ in range(x * y)])
    return f_contents


def test_raise_exception_when_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_file("not_found_file")


def test_raises_valueerror_exception_when_parsing_empty_list():
    with pytest.raises(ValueError):
        parse_file_contents(file_contents=[])


@pytest.mark.parametrize("bad_contents", [["A"], [""], [1], ["P50"], [" "]])
def test_raises_invalidheader_exception_when_parsing_bad_header(bad_contents):
    with pytest.raises(InvalidHeaderError):
        parse_file_contents(file_contents=bad_contents)


@pytest.mark.parametrize("bad_contents", [["A"], [""], [1], ["P50"], [" "]])
def test_raises_invalidfile_exception_when_parsing_bad_header(bad_contents):
    with pytest.raises(InvalidHeaderError):
        parse_file_contents(file_contents=bad_contents)


@pytest.mark.parametrize(
    "bad_contents",
    [
        ["P2", "A"],
        ["P2", "1", ""],
        ["P2", "1", "1", ""],
        ["P2", "1", "1", "1"],
        ["P2", " "],
    ],
)
def test_raises_invalidfile_exception_when_parsing_missing_values(bad_contents):
    with pytest.raises(InvalidFileError):
        parse_file_contents(file_contents=bad_contents)


@pytest.mark.parametrize(
    "bad_contents",
    [
        ["P2", "-1", "1", "1"],
        ["P2", "1", "-1", "1"],
        ["P2", "1", "1", "-1"],
    ],
)
def test_raises_invalidconfig_exception_when_parsing_non_positive_values(bad_contents):
    with pytest.raises(InvalidConfigsError):
        parse_file_contents(file_contents=bad_contents)


@pytest.mark.parametrize(
    "bad_contents",
    [
        ["P2", "1", "1", "1"],
        ["P2", "1", "1", "1", "1", "1"],
    ],
)
def test_raises_invalidfile_exception_when_parsing_non_matching_dimensions(
    bad_contents,
):
    with pytest.raises(InvalidFileError):
        parse_file_contents(file_contents=bad_contents)


# @pytest.mark.parametrize("x, y", [(1, 1), (3, 2), (3, 5), (3, 3)])
# def test_parser_returns_expected_results_from_valid_contents(
#     good_file_content, expected_file_data
# ):
#     assert (
#         parse_file_contents(file_contents=good_file_content) == expected_file_data
#     ), "non-matching file parsing"


@pytest.mark.parametrize(
    "file_contents",
    [
        "1 2 3 4 5 6 7 8 9 0",
        "1\n2\n3\n4\n5\n6\n7\n8\n9\n0\n",
        "1\n2 3 4\n5\n6 7\n8\n9 0\n",
        "1  2  3  4  5  6  7  8  9  0",
        "1\n\n2\n3\n\n\n4\n5\n6\n\n\n\n7\n8\n9\n\n0\n",
    ],
)
def test_can_split_any_formatted_content(file_contents):
    expected_output = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    results = get_split_strings(file_contents=io.StringIO(file_contents))
    assert results == expected_output
