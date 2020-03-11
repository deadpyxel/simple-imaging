from .matrix import Matrix

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
        for line in matrix.values:
            str_line = " ".join([str(i) for i in line])
            f.writelines(f"{str_line}\n")