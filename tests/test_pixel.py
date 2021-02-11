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
