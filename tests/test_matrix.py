from itertools import permutations

import pytest

from simple_imaging.errors import ValidationError
from simple_imaging.matrix import Matrix


@pytest.fixture()
def null_matrix_list():
    matrix_list = [Matrix(m, n) for m, n in permutations([1, 2])]

    return matrix_list


@pytest.mark.parametrize("m,n", [(0, 0), (0, 1), (-1, 0), (1, 0), (-1, -1)])
def test_raises_exception_when_creating_matrix_with_invalid_dimensions(m, n):
    with pytest.raises(ValidationError):
        Matrix(m=m, n=n)


def test_can_initialize_null_matrix():
    matrix = Matrix(m=3, n=3)
    assert all(matrix.values)


def test_can_sum_two_valid_matrices():
    m1 = Matrix(m=3, n=3)
    m2 = Matrix(m=3, n=3)
    assert m1.sum(m2)


@pytest.mark.parametrize(
    "m1, m2",
    [
        (Matrix(m=1, n=1), Matrix(m=2, n=1)),
        (Matrix(m=1, n=1), Matrix(m=1, n=2)),
        (Matrix(m=1, n=2), Matrix(m=2, n=1)),
    ],
)
def test_raises_exception_on_invalid_combination_for_sum(m1, m2):
    with pytest.raises(ValidationError):
        m1.sum(m2)


@pytest.mark.parametrize("m, n", [(1, 1), (1, 2), (2, 1), (2, 2), (1, 99)])
def test_can_create_matrix_of_any_valid_dimension(m, n):
    assert Matrix(m=m, n=n)


def test_has_matrix_representation_for_any_dimensions(null_matrix_list):
    for mat in null_matrix_list:
        assert mat.__str__() not in [
            "",
            "[]",
            "[",
            "]",
            "\n",
        ], f"Matrix object with dimensions {mat.m=}, {mat.n=} has no valid representation"
