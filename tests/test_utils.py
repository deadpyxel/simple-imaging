import pytest

from simple_imaging.errors import ValidationError
from simple_imaging.image import Image
from simple_imaging.utils import read_file, save_file

from .fixtures import blank_image


def test_raise_exception_when_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_file("not_found")
