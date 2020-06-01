import pytest

from simple_imaging.image import Image


@pytest.fixture
def blank_image(x: int, y: int, grayscale_level: int = 100) -> Image:
    img = Image(header="P2", max_grayscale=255, m=x, n=y)
    # sets 100 as value for each pixel in the image
    img.values = [[grayscale_level for _ in range(x)] for _ in range(y)]
    return img
