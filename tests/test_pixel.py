import pytest

from simple_imaging.types import GrayPixel
from simple_imaging.types import RGBPixel


def test_can_instantiate_default_graypixel():
    p = GrayPixel()
    assert p.value == 0


def test_can_instantiate_default_rbgpixel():
    p = RGBPixel()
    assert (p.red, p.green, p.blue) == (0, 0, 0)


@pytest.mark.parametrize(
    "pixel_value",
    [
        pytest.param("invalid", id="string"),
        pytest.param(3.14, id="float"),
    ],
)
def test_cannot_create_graypixel_without_proper_types(pixel_value):
    with pytest.raises(TypeError):
        GrayPixel(value=pixel_value)


def test_can_add_two_pixels():
    p1 = GrayPixel(value=1)
    p2 = GrayPixel(value=1)
    assert p1 + p2 == GrayPixel(value=2)


def test_can_subtract_two_pixels():
    p1 = GrayPixel(value=1)
    p2 = GrayPixel(value=1)
    assert p1 - p2 == GrayPixel(value=0)


def test_can_multiply_pixel_by_scalar():
    p1 = GrayPixel(value=1)
    assert p1 * 2 == GrayPixel(value=2)


@pytest.mark.parametrize(
    ("scalar", "expected_result"),
    [
        pytest.param(50, 50, id="positive_integer"),
        pytest.param(-50, 0, id="negative_integer"),
        pytest.param(1.5, 2, id="positive_float"),  # rounds up due to math rules
        pytest.param(-1.5, 0, id="negative_float"),
        pytest.param(1000, 255, id="out_of_bounds_positive_float"),
    ],
)
def test_multiplication_of_pixel_respects_valid_interval(scalar, expected_result):
    p1 = GrayPixel(value=1)
    assert p1 * scalar == GrayPixel(value=expected_result)
