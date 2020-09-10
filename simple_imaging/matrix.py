from __future__ import annotations

from .errors import ValidationError


class Matrix:
    def __init__(self, m: int, n: int) -> None:
        if m <= 0:
            raise ValidationError(
                f"A {type(self).__name__} must have more than 0 columns, {m} found."
            )
        if n <= 0:
            raise ValidationError(
                f"A {type(self).__name__} must have more than 0 lines, {n} found."
            )
        self.m = m
        self.n = n
        self.values = self._initialize_null_matrix()

    def _initialize_null_matrix(self) -> list:
        """Initialize a null matrix (list of lists)
        with given dimensions.

        Returns:
            list -- Null matrix MxN
        """
        return [[0 for _ in range(self.m)] for _ in range(self.n)]

    def sum(self, other: Matrix) -> Matrix:
        """Sums this Matrix object to another and
        returns the result as a new matrix object

        Arguments:
            other {Matrix} -- Another matrix object with same MxN dimensions

        Raises:
            ValidationError: Matrices with different dimensions

        Returns:
            Matrix -- Resulting Matrix
        """
        if not (self.m == other.m and self.n == other.n):
            raise ValidationError(
                f"Matrices with different dimensions found. ({self.m}, {self.n}) != ({other.m}, {other.n})."
            )

        result = Matrix(self.m, self.n)
        for i, (row1, row2) in enumerate(zip(self.values, other.values)):
            for j, (a, b) in enumerate(zip(row1, row2)):
                element_sum = max(0, min(255, a + b))
                result.values[i][j] = element_sum
        return result

    def __str__(self) -> str:
        return "\n".join([str(line) for line in self.values])
