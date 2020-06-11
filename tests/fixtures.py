from typing import Any, Dict, List

import pytest

from simple_imaging.image import Image


@pytest.fixture
def blank_image(x: int, y: int, max_level: int = 100) -> Image:
    pixel_values = [[max_level for _ in range(x)] for _ in range(y)]
    img = Image(header="P2", max_level=255, dimensions=(x, y), contents=pixel_values)
    return img


@pytest.fixture
def good_file_content(x: int, y: int) -> List[str]:
    f_contents = ["P2", str(x), str(y), "255"]
    f_contents.extend(["1" for _ in range(x * y)])
    return f_contents


@pytest.fixture
def expected_file_data(x: int, y: int) -> Dict[str, Any]:
    return {
        "header": "P2",
        "dimensions": (x, y),
        "max_level": 255,
        "contents": [[1 for _ in range(x)] for _ in range(y)],
    }
