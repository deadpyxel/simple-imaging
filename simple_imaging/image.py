from __future__ import annotations

import copy

from .errors import ImcompatibleImages
from .errors import ValidationError
from .types import GrayPixel
from .types import Pixel
from .types import RGBPixel
from .utils import get_split_strings
from .utils import parse_file_contents


def read_file(filepath: str) -> Image:
    """File reading utility

    Given a file path, attempts to validade file contents,
    if said contents are valid, returns an Image object


    Arguments:
        filepath {str} -- path for desired Netpbm file

    Returns:
        Image -- Image object generated by the file contents
    """
    image = Image.from_file(filepath)
    return image


def save_file(filepath: str, image: Image) -> None:
    with open(filepath, "w") as f:
        f.write(f"{image.header}\n")
        f.write(f"{image.x} {image.y}\n")
        f.write(f"{image.max_level}\n")
        if image.header == "P3":
            pixel_data = []
            for line in image.values:
                pixel_line = []
                for pixel in line:
                    pixel_line.extend(pixel.value)
                pixel_data.extend(pixel_line)
        else:
            pixel_data = [pixel.value for line in image.values for pixel in line]
        str_line = " ".join(str(val) for val in pixel_data)
        f.writelines(f"{str_line}\n")


def extract_channels(img: Image) -> list[Image, Image, Image]:
    # Split each channel into a separated value list.
    red_channel = [[GrayPixel(pixel.red) for pixel in row] for row in img.values]
    green_channel = [[GrayPixel(pixel.green) for pixel in row] for row in img.values]
    blue_channel = [[GrayPixel(pixel.blue) for pixel in row] for row in img.values]
    # Instantiate each channel as a new P2 (Grayscale) Image
    r_channel_image = Image(
        header="P2",
        max_level=img.max_level,
        dimensions=(img.x, img.y),
        contents=red_channel,
    )
    g_channel_image = Image(
        header="P2",
        max_level=img.max_level,
        dimensions=(img.x, img.y),
        contents=blue_channel,
    )
    b_channel_image = Image(
        header="P2",
        max_level=img.max_level,
        dimensions=(img.x, img.y),
        contents=green_channel,
    )

    return [r_channel_image, g_channel_image, b_channel_image]


def merge_channels(channels: list[Image, Image, Image]) -> Image:
    # Grabs only the channel data
    r_channel, g_channel, b_channel = (
        channels[0].values,
        channels[1].values,
        channels[2].values,
    )
    rgb_channels = [
        [RGBPixel(r.value, g.value, b.value) for r, g, b in row]
        for row in zip(r_channel, g_channel, b_channel)
    ]
    for row in zip(r_channel, g_channel, b_channel):
        print(f"{row=}")
        for r, g, b in row:
            print(f"{r=} {g=} {b=}")
    base_image = channels[0]
    return Image(
        header="P3",
        max_level=base_image.max_level,
        dimensions=(base_image.x, base_image.y),
        contents=rgb_channels,
    )


def validate_image_compatibility(image1, image2) -> bool:
    return (
        # same dimensions
        (image1.x, image1.y)
        == (
            image2.x,
            image2.y,
        )
        # same header
        and image1.header == image2.header
        # same max_level for colors
        and image1.max_level == image2.max_level
    )


class Image:
    def __init__(
        self,
        header: str,
        max_level: int,
        dimensions: tuple[int, int],
        contents: list[list[Pixel]] = None,
    ):
        if any(i <= 0 for i in dimensions):
            raise ValidationError(
                "An Image cannot have any dimension negative or null."
            )
        self.header = header
        self.x, self.y = dimensions
        self.max_level = max_level
        self.values = contents

    @classmethod
    def from_file(cls, filepath: str) -> Image:
        """Creates image from file

        Args:
            filepath (str): path to source file
        """
        with open(filepath) as f:
            f_contents = get_split_strings(f)
        image_data = parse_file_contents(f_contents)
        image = cls(**image_data)
        return image

    def copy_current_image(self) -> Image:
        return copy.deepcopy(self)

    def negative(self, inplace: bool = True) -> Image:
        for i, row in enumerate(self.values):
            for j, _ in enumerate(row):
                self.values[i][j].negative()
        return self if inplace else self.copy_current_image()

    def add_image(self, other_image: Image) -> Image:
        if not validate_image_compatibility(self, other_image):
            raise ImcompatibleImages(
                "The images are incompatible for the `add` operation"
            )

        value_list = other_image.values
        for i, line in enumerate(value_list):
            for j, pixel in enumerate(line):
                self.values[i][j] += pixel
        return self

    def subtract_image(self, other_image: Image) -> Image:
        if not validate_image_compatibility(self, other_image):
            raise ImcompatibleImages(
                "The images are incompatible for the `subtract` operation"
            )

        value_list = other_image.values
        for i, line in enumerate(value_list):
            for j, pixel in enumerate(line):
                self.values[i][j] -= pixel
        return self

    def multiply_image(self, value: int) -> Image:
        return NotImplemented

    def avg_filter(self) -> Image:
        return NotImplemented

    def median_filter(self) -> Image:
        return NotImplemented

    def laplacian_filter(self) -> Image:
        return NotImplemented

    def histogram_equalization(self):
        return NotImplemented

    def grayscale_slicing(self):
        return NotImplemented

    def get_histogram(self) -> dict[str, int]:
        """Generates the histogram for the image

        Raises:
            ValidationError: In case he image is not grayscale

        Returns:value
            dict[str, int]: histogram for image as a dictionary,
            where each key is the pixel value and each value is
            the number of courrences in the image
        """
        if self.header not in ("P1", "P2"):
            raise ValidationError("Cannot extract histogram of non-grayscale images")
        pixel_value_list = [p.value for row in self.values for p in row]
        # for each level, get the count of ocurrences in the pixel list
        hist = {str(i): pixel_value_list.count(i) for i in range(self.max_level + 1)}
        return hist

    def darken(self, level: int, inplace: bool = True) -> Image:
        """Darken image method

        Given a level in pixel value, this will darken the image by that much.
        The value must obey the criteria (0<=level<=255), else an Exception is raised

        Arguments:
            level {int} -- Pixel value (as in how much) for image enlightening
            inplace (bool, optional): If the operation should be executed in place.
                    Defaults to True.

        Returns:
            Image: Resulting Image object from operation,
                    returns a copy if `inplace` is False
        """
        for i, row in enumerate(self.values):
            for j, _ in enumerate(row):
                self.values[i][j].darken(level)
        return self if inplace else self.copy_current_image()

    def lighten(self, level: int, inplace: bool = True) -> Image:
        """Lighten image method

        Given a level in pixel value, this will enlighten the image by that much.
        The value must obey the criteria (0<=level<=255), else an Exception is raised

        Arguments:
            level {int} -- Pixel value (as in how much) for image enlightening
            inplace (bool, optional): If the operation should be executed in place.
                    Defaults to True.

        Returns:
            Image: Resulting Image object from operation,
                    returns a copy if `inplace` is False
        """
        for i, row in enumerate(self.values):
            for j, _ in enumerate(row):
                self.values[i][j].lighten(level)
        return self if inplace else self.copy_current_image()

    def rotate_90(self, clockwise: bool = True, inplace: bool = True) -> Image:
        # This image MxN has to become NxM
        working_values = [[0 for _ in range(self.y)] for _ in range(self.x)]
        for i, row in enumerate(self.values):
            for j, pixel in enumerate(row):
                if not clockwise:
                    working_values[j][self.y - i - 1] = pixel
                else:
                    working_values[self.x - j - 1][i] = pixel
        self.x, self.y, self.values = self.y, self.x, working_values
        return self if inplace else self.copy_current_image()

    def rotate_180(self, inplace: bool = True) -> Image:
        for i, row in enumerate(self.values):
            for j, pixel in enumerate(row):
                self.values[self.x - i - 1][self.y - j - 1] = pixel
        return self if inplace else self.copy_current_image()

    def vertical_mirror(self, inplace: bool = True) -> Image:
        for i, row in enumerate(self.values):
            for j, pixel in enumerate(row):
                self.values[i][self.y - j - 1] = pixel
        return self if inplace else self.copy_current_image()

    def horizontal_mirror(self, inplace: bool = True) -> Image:
        for i, row in enumerate(self.values):
            for j, pixel in enumerate(row):
                self.values[self.x - i - 1][j] = pixel
        return self if inplace else self.copy_current_image()

    def set_pixel(self, x: int, y: int, pixel: Pixel) -> None:
        if not (0 < x <= self.x and 0 < y <= self.y):
            raise ValidationError(
                f"Tried to set_pixel on invalid position ({x}, {y}) on image ({self.x} x {self.y})"
            )
            # TODO: Validate pixel type
        self.values[x - 1][y - 1] = pixel

    def get_pixel(self, x: int, y: int) -> Pixel:
        if not (0 < x <= self.x and 0 < y <= self.y):
            raise ValidationError(
                f"Tried to get_pixel on invalid position ({x}, {y}) on image ({self.x} x {self.y})"
            )
        return self.values[x - 1][y - 1]
