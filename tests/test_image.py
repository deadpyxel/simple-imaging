import pytest

from simple_imaging.errors import ValidationError
from simple_imaging.image import Image


@pytest.fixture
def dummy_image() -> Image:
    return Image(header="P2", max_grayscale=255, m=1, n=1)


@pytest.fixture
def blank_image(x: int, y: int) -> Image:
    img = Image(header="P2", max_grayscale=255, m=x, n=y)
    # sets 100 as value for each pixel in the image
    img.values = [[100 for _ in range(x)] for _ in range(y)]
    return img


invalid_level_types = ["a", [], 0.01, {}, object]


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


@pytest.mark.parametrize("level", invalid_level_types)
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


@pytest.mark.parametrize("level", invalid_level_types)
def test_raises_valueerror_when_attempting_lighten_with_invalid_type(
    dummy_image: Image, level: int
):
    with pytest.raises(ValueError):
        dummy_image.lighten(level=level)


@pytest.mark.parametrize("level", invalid_level_types)
def test_level_validation_correctly_validates_type(dummy_image: Image, level):
    assert dummy_image.validate_operation_level(level) == (False, "type")


@pytest.mark.parametrize("level", [-1, 256])
def test_level_validation_correctly_validates_range(dummy_image: Image, level):
    assert dummy_image.validate_operation_level(level) == (False, "range")


@pytest.mark.parametrize("level", [0, 1, 100, 255])
def test_level_validation_correctly_validates_valid_level(dummy_image: Image, level):
    assert dummy_image.validate_operation_level(level) == (True, "")


def test_can_copy_current_image(dummy_image: Image):
    copy_image = dummy_image.copy_current_image()
    assert copy_image.m == dummy_image.m
    assert copy_image.m == dummy_image.n
    assert copy_image.values == dummy_image.values
    assert copy_image.header == dummy_image.header


def test_can_set_pixel_at_coordinate(dummy_image: Image):
    dummy_image.set_pixel(0, 0, 1)
    assert dummy_image.get_pixel_at(0, 0) == 1


def test_lighten_operation_respects_maximum_grayscale(dummy_image: Image):
    dummy_image.set_pixel(0, 0, 100)
    ligthen_img = dummy_image.lighten(200)
    assert not any(val > 255 for row in ligthen_img.values for val in row)


def test_darken_operation_respects_maximum_grayscale(dummy_image: Image):
    dummy_image.set_pixel(0, 0, 100)
    darken_img = dummy_image.darken(200)
    assert not any(val > 0 for row in darken_img.values for val in row)


@pytest.mark.parametrize("x, y", [(1, 1), (3, 2), (3, 5), (3, 3)])
def test_darken_operation_returns_correct_result(blank_image):
    dk_img = blank_image.darken(level=50)
    assert all(
        dk_img.get_pixel_at(x, y) == 50
        for x in range(blank_image.m)
        for y in range(blank_image.n)
    )


@pytest.mark.parametrize("x, y", [(1, 1), (3, 2), (3, 5), (3, 3)])
def test_lighten_operation_returns_correct_result(blank_image):
    dk_img = blank_image.lighten(level=50)
    assert all(
        dk_img.get_pixel_at(x, y) == 150
        for x in range(blank_image.m)
        for y in range(blank_image.n)
    )


@pytest.mark.parametrize("x, y", [(3, 2)])
def test_darken_operation_returns_respects_image_orientation(blank_image):
    image_values = [[i * 10 for i in range(1, 4)] for _ in range(2)]
    blank_image.values = image_values
    image_values = [[i - 10 for i in row] for row in image_values]

    dk_img = blank_image.darken(level=10)
    assert (
        dk_img.values == image_values
    ), f"Orientation not respected: {dk_img.values} != {image_values}"


@pytest.mark.parametrize("x, y", [(3, 2)])
def test_lighten_operation_returns_respects_image_orientation(blank_image):
    image_values = [[i * 10 for i in range(1, 4)] for _ in range(2)]
    blank_image.values = image_values
    image_values = [[i + 10 for i in row] for row in image_values]

    dk_img = blank_image.lighten(level=10)
    assert (
        dk_img.values == image_values
    ), f"Orientation not respected: {dk_img.values} != {image_values}"
