from .errors import ValidationError
from .matrix import Matrix


class Image(Matrix):
    def __init__(self, header: str, max_grayscale: int, m: int, n: int):
        self.header = header
        self.max_grayscale = max_grayscale
        super().__init__(m=m, n=n)

    def negative(self):
        copy_image = Image(self.header, self.max_grayscale, self.m, self.n)
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                negative_value = max(0, min(255, 255 - pixel_value))
                copy_image.values[i][j] = negative_value
        return copy_image

    def darken(self, level: int):
        if not (0 <= level <= 255):
            raise ValidationError(
                f"Darken operation requires values between (inclusive) 0 and 255, {level} found."
            )
        copy_image = Image(self.header, self.max_grayscale, self.m, self.n)
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                darken_value = max(0, pixel_value - level)
                copy_image.values[i][j] = darken_value
        return copy_image

    def lighten(self, level: int):
        if not (0 <= level <= 255):
            raise ValidationError(
                f"Lighten operation requires values between (inclusive) 0 and 255, {level} found."
            )
        copy_image = Image(self.header, self.max_grayscale, self.m, self.n)
        for i, row in enumerate(self.values):
            for j, pixel_value in enumerate(row):
                darken_value = min(255, pixel_value + level)
                copy_image.values[i][j] = darken_value
        return copy_image

    def rotate_90(self, clockwise=True):
        # This image MxN has to become NxM
        copy_image = Image(self.header, self.max_grayscale, self.n, self.m)
        copy_image.values = self.values
        for i, row in enumerate(copy_image.values):
            for j, pixel_value in enumerate(row):
                copy_image.values[i][j] = copy_image.values[j][i]
        return copy_image
