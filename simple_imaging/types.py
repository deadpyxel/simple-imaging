from dataclasses import dataclass
from typing import Protocol
from typing import Tuple
from typing import Union

from .errors import UnkownError
from .errors import ValidationError


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
        raise UnkownError("An unknown exception has occurred")


class Pixel(Protocol):
    """Abstract Pixel class

    This class holds the abstractions to the pixel operation methods
    """    
    # @property
    # def value(self):
    #     return None

    def darken(self, level: int):
        return NotImplemented

    def lighten(self, level: int):
        return NotImplemented

    def negative(self) -> None:
        return NotImplemented

    def __add__(self, other):
        return NotImplemented

    def __sub__(self, other):
        return NotImplemented

    def __mul__(self, val: Union[int, float]):
        return NotImplemented

    def __eq__(self, other):
        return NotImplemented


class GrayPixel(Pixel):
    def __init__(self, value: int = 0):
        """Grayscale Pixel

        Args:
            value (int, optional): value for this pixel. Defaults to 0.
        """        
        self.value = value

    def darken(self, level: int) -> None:
        """Darkens the current pixel

        Args:
            level (int): amount to subtract from current value
        """        
        validate_value_and_raise(level)
        self.value = max(0, self.value - level)

    def lighten(self, level: int) -> None:
        """lightens the current pixel

        Args:
            level (int): amount to add to current value
        """        
        validate_value_and_raise(level)
        self.value = min(255, self.value + level)

    def negative(self) -> None:
        """Negative operation

        Sets the pixel value to 255-current_value obeying the 0~255 interval
        """        
        self.value = max(0, min(255, 255 - self.value))

    def __add__(self, other):
        # Custom `+` operator override, clamps values between 0-255
        return GrayPixel(min(255, self.value + other.value))

    def __sub__(self, other):
        # Custom `-` operator override, clamps values between 0-255
        return GrayPixel(max(0, self.value - other.value))

    def __mul__(self, val: Union[int, float]):
        # Custom `*` operator override, clamps values between 0-255
        return GrayPixel(min(255, max(0, round(self.value * val))))

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return f"{type(self).__name__}(value={self.value})"


@dataclass
class RGBPixel(Pixel):
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
