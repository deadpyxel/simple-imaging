from __future__ import annotations

import copy
from typing import Tuple

from .errors import ValidationError
from .matrix import Matrix
from .utils import get_split_strings, parse_file_contents


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
        f.write(f"{image.m} {image.n}\n")
        f.write(f"{image.max_level}\n")
        for line in image.values:
            str_line = " ".join([str(i) for i in line])
            f.writelines(f"{str_line}\n")


class Image(Matrix):
    def __init__(
        self,
        header: str,
        max_level: int,
        dimensions: Tuple[int, int],
        contents: list = None,
    ):
        self.header = header
        self.max_level = max_level
        m, n = dimensions
        super().__init__(m=m, n=n)
        if contents is not None and isinstance(contents, list):
            self.values = contents

    @classmethod
    def from_file(cls, filepath: str) -> Image:
        image_data = parse_file_contents(get_split_strings(filepath))
        image = cls(**image_data)
        return image

    @staticmethod
    def validate_operation_level(level: int) -> Tuple[bool, str]:
        validity = (True, "")
        if not isinstance(level, int):
            validity = (False, "type")
        elif not (0 <= level <= 255):
            validity = (False, "range")
        return validity

    @staticmethod
    def validate_value_and_raise(value: int) -> None:
        validity, err_type = Image.validate_operation_level(value)
        if validity is False:
            if err_type == "type":
                raise ValueError(
                    f"This operation expects an integer, received a {type(value)}"
                )
            elif err_type == "range":
                raise ValidationError(
                    f"This operation requires values between (inclusive) 0 and 255, {value} found."
                )
            raise Exception(f"An unkown exception has occurred")

    def copy_current_image(self) -> Image:
        return copy.deepcopy(self)

    def set_pixel(self, x: int, y: int, pixel_value: int) -> None:
        self.validate_value_and_raise(pixel_value)
        self.values[y][x] = pixel_value

    def get_pixel_at(self, x: int, y: int) -> int:
        return self.values[y][x]

    def negative(self, inplace: bool = True) -> Image:
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                negative_value = max(0, min(255, 255 - pixel_value))
                self.values[i][j] = negative_value
        return self if inplace else self.copy_current_image()

    def darken(self, level: int, inplace: bool = True) -> Image:
        """Darken image method

        Given a level in pixel value, this will darken the image by that much.
        The value must obey the criteria (0<=level<=255), else an Exception is raised

        Arguments:
            level {int} -- Pixel value (as in how much) for image darkening

        Raises:
            ValueError: If provided value is not an integer
            ValidationError: If `level`does not obey `(0<=level<=255)`

        Returns:
            Image -- A new image that has been processed by the darken operation
        """
        self.validate_value_and_raise(level)
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                darken_value = max(0, pixel_value - level)
                self.values[i][j] = darken_value
        return self if inplace else self.copy_current_image()

    def lighten(self, level: int, inplace: bool = True) -> Image:
        """Lighten image method

        Given a level in pixel value, this will enlighten the image by that much.
        The value must obey the criteria (0<=level<=255), else an Exception is raised

        Arguments:
            level {int} -- Pixel value (as in how much) for image enlightening

        Raises:
            ValueError: If provided value is not an integer
            ValidationError: If `level`does not obey `(0<=level<=255)`

        Returns:
            Image -- A new image that has been processed by the lighten operation
        """
        self.validate_value_and_raise(level)
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                lighten_value = min(255, pixel_value + level)
                self.values[i][j] = lighten_value
        return self if inplace else self.copy_current_image()

    def rotate_90(self, clockwise: bool = True, inplace: bool = True) -> Image:
        # This image MxN has to become NxM
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                if clockwise:
                    self.values[j][self.m - i - 1] = pixel_value
                else:
                    self.values[self.n - j - 1][i] = pixel_value
        return self if inplace else self.copy_current_image()

    def rotate_180(self, inplace: bool = True) -> Image:
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                self.values[self.m - i - 1][self.n - j - 1] = pixel_value
        return self if inplace else self.copy_current_image()

    def vertical_mirror(self, inplace: bool = True) -> Image:
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                self.values[i][self.n - j - 1] = pixel_value
        return self if inplace else self.copy_current_image()

    def horizontal_mirror(self, inplace: bool = True) -> Image:
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                self.values[self.m - i - 1][j] = pixel_value
        return self if inplace else self.copy_current_image()

    def __str__(self):
        return f"Header={self.header}\nDimensions=({self.m}x{self.n})\nValues:\n{self.values}"
