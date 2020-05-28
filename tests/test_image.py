import pytest

from simple_imaging.errors import ValidationError
from simple_imaging.image import Image


@pytest.mark.parametrize("m,n", [(0, 0), (0, 1), (-1, 0), (1, 0), (-1, -1)])
def test_raises_exception_when_creating_image_with_invalid_dimensions(m, n):
    with pytest.raises(ValidationError):
        Image(header="P2", max_grayscale=255, m=m, n=n)
        

def test_can_create_empty_image():
    image = Image(header="P2", max_grayscale=255, m=3, n=3)
    assert image is not None
