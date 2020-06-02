from dataclasses import dataclass

from .errors import ValidationError


class PixelLevel:
    def __init__(self, level: int):
        if isinstance(level, int):
            raise ValueError(
                f"This operation expects an integer, received a {type(level)}"
            )
        elif 0 <= level <= 255:
            raise ValidationError(
                f"This operation requires values between (inclusive) 0 and 255, {level} found."
            )
        self.level = level


@dataclass
class GrayPixel:
    value: int

    def darken(self, level: int) -> None:
        self.value = max(0, self.value - level)

    def lighten(self, level: int) -> None:
        self.value = min(255, self.value + level)

    def negative(self) -> None:
        self.value = max(0, min(255, 255 - self.value))

    def get_value(self) -> int:
        return self.value


@dataclass
class RGBPixel:
    red: int
    green: int
    blue: int

    def darken(self, level: int) -> None:
        self.red = max(0, self.red - level)
        self.green = max(0, self.green - level)
        self.blue = max(0, self.blue - level)

    def lighten(self, level: int) -> None:
        self.red = min(255, self.red + level)
        self.green = min(255, self.green + level)
        self.blue = min(255, self.blue + level)

    def negative(self) -> None:
        self.red = max(0, min(255, 255 - self.red))
        self.green = max(0, min(255, 255 - self.green))
        self.blue = max(0, min(255, 255 - self.blue))

    def set_value(self, r: int, g: int, b: int) -> None:
        self.red = r
        self.green = g
        self.blue = b
