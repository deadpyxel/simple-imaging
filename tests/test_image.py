import pytest

from simple_imaging.errors import ImcompatibleImages
from simple_imaging.errors import ValidationError
from simple_imaging.image import extract_channels
from simple_imaging.image import Image
from simple_imaging.image import validate_image_compatibility
from simple_imaging.types import GrayPixel
from simple_imaging.types import RGBPixel

INVALID_LEVEL_TYPE_LIST = ["a", [], 0.01, {}, object]


def n_numbers(n: int):
    i = 0
    while i < n:
        yield i
        i += 1


@pytest.fixture
def blank_image(x: int, y: int, max_level: int = 100) -> Image:
    pixel_values = [[GrayPixel(max_level) for _ in range(x)] for _ in range(y)]
    img = Image(
        header="P2", max_level=max_level, dimensions=(x, y), contents=pixel_values
    )
    return img


@pytest.fixture
def p3_image() -> Image:
    pixel_values = [[RGBPixel(0, 1, 2) for _ in range(3)] for _ in range(3)]
    img = Image(header="P3", max_level=255, dimensions=(3, 3), contents=pixel_values)
    return img


@pytest.fixture
def p2_image() -> Image:
    val = n_numbers(3 * 3)
    pixel_values = [[GrayPixel(next(val)) for _ in range(3)] for _ in range(3)]
    img = Image(header="P2", max_level=255, dimensions=(3, 3), contents=pixel_values)
    return img


@pytest.fixture
def dummy_image() -> Image:
    return Image(
        header="P2", max_level=255, dimensions=(1, 1), contents=[[GrayPixel(0)]]
    )


@pytest.mark.parametrize("m, n", [(0, 0), (0, 1), (-1, 0), (1, 0), (-1, -1)])
def test_raises_exception_when_creating_image_with_invalid_dimensions(m, n):
    with pytest.raises(ValidationError):
        Image(header="P2", max_level=255, dimensions=(m, n))


def test_can_create_empty_image():
    image = Image(header="P2", max_level=255, dimensions=(3, 3))
    assert image is not None


def test_can_execute_negative_operation(dummy_image: Image):
    negative_img = dummy_image.negative()
    assert all(val.value == 255 for row in negative_img.values for val in row)


@pytest.mark.parametrize("level", [-1, 256])
def test_raises_validationerror_when_attempting_darken_with_invalid_int(
    dummy_image: Image, level: int
):
    with pytest.raises(ValidationError):
        dummy_image.darken(level=level)


@pytest.mark.parametrize("level", INVALID_LEVEL_TYPE_LIST)
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


@pytest.mark.parametrize("level", INVALID_LEVEL_TYPE_LIST)
def test_raises_valueerror_when_attempting_lighten_with_invalid_type(
    dummy_image: Image, level: int
):
    with pytest.raises(ValueError):
        dummy_image.lighten(level=level)


def test_can_copy_current_image(dummy_image: Image):
    copy_image = dummy_image.copy_current_image()
    assert copy_image.x == dummy_image.x
    assert copy_image.y == dummy_image.y
    assert copy_image.values == dummy_image.values
    assert copy_image.header == dummy_image.header


def test_can_set_pixel_at_valid_coordinate(dummy_image: Image):
    p = GrayPixel(1)
    dummy_image.set_pixel(x=1, y=1, pixel=p)


@pytest.mark.parametrize("x, y", [(0, 0), (0, 1), (2, 2), (2, 1)])
def test_cannot_set_pixel_at_out_of_bounds_coordinates(
    dummy_image: Image, x: int, y: int
):
    p = GrayPixel(1)
    with pytest.raises(ValidationError):
        dummy_image.set_pixel(x=x, y=y, pixel=p)


def test_lighten_operation_respects_maximum_grayscale(dummy_image: Image):
    p = GrayPixel(100)
    dummy_image.set_pixel(1, 1, p)
    ligthen_img = dummy_image.lighten(200)
    assert not any(val.value > 255 for row in ligthen_img.values for val in row)


def test_darken_operation_respects_maximum_grayscale(dummy_image: Image):
    p = GrayPixel(100)
    dummy_image.set_pixel(1, 1, p)
    darken_img = dummy_image.darken(200)
    assert not any(val.value > 0 for row in darken_img.values for val in row)


@pytest.mark.parametrize(
    "x, y",
    [
        pytest.param(1, 1, id="1x1_case"),
        pytest.param(3, 2, id="3x2_case"),
        pytest.param(3, 5, id="3x5_case"),
        pytest.param(3, 3, id="3x3_case"),
    ],
)
def test_darken_operation_returns_correct_result(blank_image):
    dk_img = blank_image.darken(level=50, inplace=False)
    assert all(
        dk_img.get_pixel(j, i).value == 50
        for i in range(1, blank_image.y + 1)
        for j in range(1, blank_image.x + 1)
    )


@pytest.mark.parametrize("x, y", [(1, 1), (3, 2), (3, 5), (3, 3)])
def test_lighten_operation_returns_correct_result(blank_image):
    dk_img = blank_image.lighten(level=50)
    assert all(
        dk_img.get_pixel(j, i).value == 150
        for i in range(1, blank_image.y + 1)
        for j in range(1, blank_image.x + 1)
    )


@pytest.mark.parametrize("x, y", [(3, 2)])
def test_darken_operation_returns_respects_image_orientation(blank_image, x, y):
    image_values = [[GrayPixel(i * 10) for i in range(1, x + 1)] for _ in range(y)]
    blank_image.values = image_values
    expected_values = [[GrayPixel(p.value - 10) for p in row] for row in image_values]

    blank_image.darken(level=10)
    assert (
        blank_image.values == expected_values
    ), f"Orientation not respected: {blank_image.values} != {expected_values}"


@pytest.mark.parametrize("x, y", [(3, 2)])
def test_lighten_operation_returns_respects_image_orientation(blank_image, x, y):
    image_values = [[GrayPixel(i * 10) for i in range(1, x + 1)] for _ in range(y)]
    blank_image.values = image_values
    expected_values = [[GrayPixel(p.value + 10) for p in row] for row in image_values]

    blank_image.lighten(level=10)
    assert (
        blank_image.values == expected_values
    ), f"Orientation not respected: {blank_image.values} != {expected_values}"


def test_can_split_p3_image_into_channels(p3_image):
    img_r, img_g, img_b = extract_channels(p3_image)


def test_can_add_images(p2_image):
    img1 = p2_image.copy_current_image()
    img2 = p2_image.copy_current_image()

    img1.add_image(img2)

    assert img1.values == [
        [GrayPixel(0), GrayPixel(2), GrayPixel(4)],
        [GrayPixel(6), GrayPixel(8), GrayPixel(10)],
        [GrayPixel(12), GrayPixel(14), GrayPixel(16)],
    ]


def test_adding_incompatible_images_raises_error(p2_image):
    img1 = p2_image.copy_current_image()
    img2 = p2_image.copy_current_image()
    img2.header = "P1"

    with pytest.raises(ImcompatibleImages):
        img1.add_image(img2)


def test_can_subtract_images(p2_image):
    img1 = p2_image.copy_current_image()
    img2 = p2_image.copy_current_image()

    img1.subtract_image(img2)

    assert img1.values == [
        [GrayPixel(0), GrayPixel(0), GrayPixel(0)],
        [GrayPixel(0), GrayPixel(0), GrayPixel(0)],
        [GrayPixel(0), GrayPixel(0), GrayPixel(0)],
    ]


def test_incompatible_images_validate_to_false(p2_image):
    img1 = p2_image.copy_current_image()
    img2 = p2_image.copy_current_image()
    img2.header = "P1"

    assert validate_image_compatibility(img1, img2) is False


def test_can_retrieve_histogram(p2_image):
    img = p2_image  # in this case, each pixel has a single value
    img.max_level = 8  # set the image to have at most 8 gray levels
    histogram = img.get_histogram()

    # this should result in a histogram with 1 of each allowed pixel level
    assert histogram == {
        "0": 1,
        "1": 1,
        "2": 1,
        "3": 1,
        "4": 1,
        "5": 1,
        "6": 1,
        "7": 1,
        "8": 1,
    }


def test_cannot_extract_histogram_from_rgb_image(p3_image):
    with pytest.raises(ValidationError):
        p3_image.get_histogram()
