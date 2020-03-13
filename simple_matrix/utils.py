from .image import Image


def read_file(filepath: str) -> Image:
    with open(filepath) as f:
        lines = f.readlines()
        header = lines[0].strip()
        lines = [[int(el) for el in line.split(" ")] for line in lines[1:]]
        m, n = lines[0]
        max_grayscale = lines[1][0]
        image = Image(header, max_grayscale, m, n)
        matrix = lines[2]
        matrix = [matrix[i : i + n] for i in range(0, len(matrix), n)]
        image.values = matrix
        return image


def save_file(filepath, matrix):
    with open(filepath, "w") as f:
        f.write(f"{matrix.m} {matrix.n}\n")
        for line in matrix.values:
            str_line = " ".join([str(i) for i in line])
            f.writelines(f"{str_line}\n")