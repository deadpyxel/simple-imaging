from __future__ import annotations

from typing import Tuple

from .errors import ValidationError
from .matrix import Matrix


class Image(Matrix):
    def __init__(self, header: str, max_grayscale: int, m: int, n: int):
        self.header = header
        self.max_grayscale = max_grayscale
        super().__init__(m=m, n=n)

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
        return Image(self.header, self.max_grayscale, self.m, self.n)

    def set_pixel(self, x: int, y: int, pixel_value: int) -> None:
        self.validate_value_and_raise(pixel_value)
        self.values[y][x] = pixel_value

    def get_pixel_at(self, x: int, y: int) -> int:
        return self.values[y][x]

    def negative(self) -> Image:
        copy_image = self.copy_current_image()
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                negative_value = max(0, min(255, 255 - pixel_value))
                copy_image.values[i][j] = negative_value
        return copy_image

    def darken(self, level: int) -> Image:
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
        copy_image = self.copy_current_image()
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                darken_value = max(0, pixel_value - level)
                copy_image.values[i][j] = darken_value
        return copy_image

    def lighten(self, level: int) -> Image:
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
        copy_image = self.copy_current_image()
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                lighten_value = min(255, pixel_value + level)
                copy_image.values[i][j] = lighten_value
        return copy_image

    def rotate_90(self, clockwise: bool = True) -> Image:
        # This image MxN has to become NxM
        copy_image = self.copy_current_image()
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                if clockwise:
                    copy_image.values[j][copy_image.m - i - 1] = pixel_value
                else:
                    copy_image.values[copy_image.n - j - 1][i] = pixel_value
        return copy_image

    def rotate_180(self) -> Image:
        copy_image = self.copy_current_image()
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                copy_image.values[copy_image.m - i - 1][
                    copy_image.n - j - 1
                ] = pixel_value
        return copy_image

    def vertical_mirror(self) -> Image:
        copy_image = self.copy_current_image()
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                copy_image.values[i][copy_image.n - j - 1] = pixel_value
        return copy_image

    def horizontal_mirror(self) -> Image:
        copy_image = self.copy_current_image()
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                copy_image.values[copy_image.m - i - 1][j] = pixel_value
        return copy_image

    def __str__(self):
        return f"Header={self.header}\nDimensions=({self.m}x{self.n})\nValues:\n{self.values}"
