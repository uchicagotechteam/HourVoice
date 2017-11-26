# String alignment module inspired from the Smith-Waterman algorithm for local sequence alignment

import numpy as np


def smith_waterman(str1, str2, score, gap=-1):
    n1, n2 = len(str1), len(str2)
    alignment_matrix = np.zeros((n1+1,n2+1))
    directions = [[(0,0) for _ in range(n2+1)] for _ in range(n1+1)]
    max_score = 0
    max_index = (0,0)
    for i in range(n1+1):
        alignment_matrix[i][0] = gap * i
        if i:
            directions[i][0] = (i-1, 0)
    for j in range(n2+1):
        alignment_matrix[0][j] = gap * j
        if j:
            directions[0][j] = (0, j-1)

    for i in range(1, n1+1):
        for j in range(1, n2+1):
            from_above = ((i-1,j), alignment_matrix[i-1][j] + gap)
            from_left = ((i,j-1), alignment_matrix[i][j-1] + gap)
            from_diag = ((i-1,j-1), alignment_matrix[i-1][j-1] + score(str1[i-1], str2[j-1]))
            pair = max(from_above, from_left, from_diag, ((0,0), 0), key=lambda x: x[1])
            if pair[1] > max_score:
                max_index = (i,j)
                max_score = pair[1]
            directions[i][j], alignment_matrix[i][j] = pair

    return directions, alignment_matrix, max_index


def build_locally_aligned_strings(str1, str2, directions, alignment_matrix, max_index, gap_char='-'):
    x, y = max_index
    aligned1, aligned2 = '', ''
    while True:
        new_x, new_y = directions[x][y]
        if x == new_x and not y == new_y:
            aligned1 += gap_char
            aligned2 += str2[new_y]
        if not x == new_x and y == new_y:
            aligned1 += str1[new_x]
            aligned2 += gap_char
        if not (x == new_x or y == new_y):
            aligned1 += str1[new_x]
            aligned2 += str2[new_y]
        if alignment_matrix[x][y] == 0:
            break
        x, y = new_x, new_y
    return aligned1[::-1], aligned2[::-1]


def local_alignment_score(alignment_matrix, max_index, match=5):
    n, m = len(alignment_matrix), len(alignment_matrix[0])
    return float(alignment_matrix[max_index[0]][max_index[1]]) / (match * min(n-1, m-1))


def align_strings_locally(str1, str2, score_function, gap=-1, gap_char='-', to_lower=True):
    aligned1 = str1.lower() if to_lower else str1
    aligned2 = str2.lower() if to_lower else str2
    directions, alignment_matrix, max_index = smith_waterman(aligned1, aligned2, score_function, gap=gap)
    aligned1, aligned2 = build_locally_aligned_strings(str1, str2, directions=directions, alignment_matrix=alignment_matrix, max_index=max_index, gap_char=gap_char)
    score = local_alignment_score(alignment_matrix, max_index)
    return score, aligned1, aligned2
