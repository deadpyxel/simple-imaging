import pytest

from .fixtures import invalid_level_types
from simple_imaging.types import validate_operation_level


@pytest.mark.parametrize("level", invalid_level_types)
def test_level_validation_correctly_validates_type(level):
    assert validate_operation_level(level) == (False, "type")


@pytest.mark.parametrize("level", [-1, 256])
def test_level_validation_correctly_validates_range(level):
    assert validate_operation_level(level) == (False, "range")


@pytest.mark.parametrize("level", [0, 1, 100, 255])
def test_level_validation_correctly_validates_valid_level(level):
    assert validate_operation_level(level) == (True, "")
