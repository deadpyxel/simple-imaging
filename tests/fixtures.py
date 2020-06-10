from typing import List

import pytest

from simple_imaging.image import Image


@pytest.fixture
def blank_image(x: int, y: int, max_level: int = 100) -> Image:
    pixel_values = [[max_level for _ in range(x)] for _ in range(y)]
    img = Image(header="P2", max_level=255, dimensions=(x, y), contents=pixel_values)
    return img
