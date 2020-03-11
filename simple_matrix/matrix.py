class Matrix:
    def __init__(self, m: int, n: int):
        assert m > 0, f"A matrix must have more than 0 columns, {m} found."
        assert n > 0, f"A matrix must have more than 0 lines, {n} found."
        self.m = m
        self.n = n
        self.values = self.initialize_null_matrix()

    def initialize_null_matrix(self) -> list:
        return [[0 for _ in range(self.m)] for _ in range(self.n)]

    def sum(self, other):

        assert (
            self.m > 0 and self.n > 0
        ), f"A Matrix with ({self.m}, {self.n}) dimensions found, must have be grater than 0."
        assert (
            other.m > 0 and other.n > 0
        ), f"A Matrix with ({other.m}, {other.n}) dimensions found, must have be grater than 0."
        assert (
            self.m == other.m and self.n == other.n
        ), f"Matrices with different dimensions found. ({self.m}, {self.n}) != ({other.m}, {other.n})."

        result = Matrix(self.m, self.n)
        for i, (row1, row2) in enumerate(zip(self.values, other.values)):
            for j, (a, b) in enumerate(zip(row1, row2)):
                element_sum = a + b
                if element_sum > 100:
                    element_sum = 100
                elif element_sum < 0:
                    element_sum = 0
                result.values[i][j] = element_sum
        return result

    def __str__(self):
        return "\n".join([str(line) for line in self.values])


def read_file(filepath) -> list:
    with open(filepath) as f:
        lines = f.readlines()
        lines = [[int(el) for el in line.split(" ")] for line in lines]
        m, n = lines[0]
        matrix = Matrix(m, n)
        for i, values in enumerate(lines[1:]):
            for j, value in enumerate(values):
                matrix.values[i][j] = value
        return matrix


def save_file(filepath, matrix):
    with open(filepath, "w") as f:
        f.write(f"{matrix.m} {matrix.n}\n")
        for line in matrix:
            str_line = " ".join([str(i) for i in line])
            f.writelines(f"{str_line}\n")
