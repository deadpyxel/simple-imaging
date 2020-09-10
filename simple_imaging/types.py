from dataclasses import dataclass
from typing import Tuple

from .errors import UnkownError, ValidationError


def validate_operation_level(level: int) -> Tuple[bool, str]:
    validity = (True, "")
    if not isinstance(level, int):
        validity = (False, "type")
    elif not (0 <= level <= 255):
        validity = (False, "range")
    return validity


def validate_value_and_raise(value: int) -> None:
    validity, err_type = validate_operation_level(value)
    if validity is False:
        if err_type == "type":
            raise ValueError(
                f"This operation expects an integer, received a {type(value)}"
            )
        elif err_type == "range":
            raise ValidationError(
                f"This operation requires a value in [0, 255] interval, {value} found."
            )
        raise UnkownError("An unkown exception has occurred")


@dataclass
class GrayPixel:
    value: int = 0

    def darken(self, level: int) -> None:
        validate_value_and_raise(level)
        self.value = max(0, self.value - level)

    def lighten(self, level: int) -> None:
        validate_value_and_raise(level)
        self.value = min(255, self.value + level)

    def negative(self) -> None:
        self.value = max(0, min(255, 255 - self.value))


@dataclass
class RGBPixel:
    red: int = 0
    green: int = 0
    blue: int = 0

    def darken(self, level: int) -> None:
        validate_value_and_raise(level)
        self.red = max(0, self.red - level)
        self.green = max(0, self.green - level)
        self.blue = max(0, self.blue - level)

    def lighten(self, level: int) -> None:
        validate_value_and_raise(level)
        self.red = min(255, self.red + level)
        self.green = min(255, self.green + level)
        self.blue = min(255, self.blue + level)

    def negative(self) -> None:
        self.red = max(0, min(255, 255 - self.red))
        self.green = max(0, min(255, 255 - self.green))
        self.blue = max(0, min(255, 255 - self.blue))

