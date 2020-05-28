import pytest

from simple_imaging.errors import ValidationError
from simple_imaging.image import Image


@pytest.fixture
def dummy_image() -> Image:
    return Image(header="P2", max_grayscale=255, m=1, n=1)


@pytest.mark.parametrize("m,n", [(0, 0), (0, 1), (-1, 0), (1, 0), (-1, -1)])
def test_raises_exception_when_creating_image_with_invalid_dimensions(m, n):
    with pytest.raises(ValidationError):
        Image(header="P2", max_grayscale=255, m=m, n=n)


def test_can_create_empty_image():
    image = Image(header="P2", max_grayscale=255, m=3, n=3)
    assert image is not None


def test_can_execute_negative_operation(dummy_image: Image):
    negative_img = dummy_image.negative()
    assert all(val == 255 for row in negative_img.values for val in row)


@pytest.mark.parametrize("level", [-1, 256])
def test_raises_validationerror_when_attempting_darken_with_invalid_int(
    dummy_image: Image, level: int
):
    with pytest.raises(ValidationError):
        dummy_image.darken(level=level)


@pytest.mark.parametrize("level", ["a", [], 0.01, {}, object])
def test_raises_valueerror_when_attempting_darken_with_invalid_type(
    dummy_image: Image, level: int
):
    with pytest.raises(ValueError):
        dummy_image.darken(level=level)


@pytest.mark.parametrize("level", [-1, 256])
def test_raises_validationerror_when_attempting_lighten_with_invalid_int(
    dummy_image: Image, level: int
):
    with pytest.raises(ValidationError):
        dummy_image.lighten(level=level)


@pytest.mark.parametrize("level", ["a", [], 0.01, {}, object])
def test_raises_valueerror_when_attempting_lighten_with_invalid_type(
    dummy_image: Image, level: int
):
    with pytest.raises(ValueError):
        dummy_image.lighten(level=level)
