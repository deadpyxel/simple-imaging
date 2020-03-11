def init_matrix(m: int, n: int) -> list:
    return [[0 for _ in range(m)] for _ in range(n)]


def matrix_sum(m1: list, m2: list) -> list:
    assert len(m1) > 0
    assert len(m2) > 0
    assert len(m1) == len(m2)
    result = init_matrix(m=len(m1[0]), n=len(m1))
    for i, (row1, row2) in enumerate(zip(m1, m2)):
        for j, (a, b) in enumerate(zip(row1, row2)):
            element_sum = a + b
            if element_sum > 100:
                element_sum = 100
            elif element_sum < 0:
                element_sum = 0
            result[i][j] = element_sum

    return result


m1 = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
m2 = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]


print(matrix_sum(m1, m2))
