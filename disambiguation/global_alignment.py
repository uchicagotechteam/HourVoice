# String alignment module inspired from the Needleman-Wunsch algorithm for global sequence alignment

import numpy as np


def needleman_wunsch(str1, str2, score, gap=-1):
    n1, n2 = len(str1), len(str2)
    alignment_matrix = np.zeros((n1+1,n2+1))
    directions = [[(0,0) for _ in range(n2+1)] for _ in range(n1+1)]
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
            pair = max(from_above, from_left, from_diag, key=lambda x: x[1])
            directions[i][j], alignment_matrix[i][j] = pair

    return directions, alignment_matrix


def build_globally_aligned_strings(str1, str2, directions, gap_char='-'):
    x, y = len(directions)-1, len(directions[0])-1
    aligned1, aligned2 = '', ''
    while not (x == 0 and y == 0):
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
        x, y = new_x, new_y
    return aligned1[::-1], aligned2[::-1]


def global_alignment_score(alignment_matrix, match=5):
    n, m = len(alignment_matrix), len(alignment_matrix[0])
    # print(alignment_matrix[n-1][m-1])
    return float(alignment_matrix[n-1][m-1]) / (match * max(n-1, m-1))


def align_strings_globally(str1, str2, score_function, gap=-1, gap_char='-', to_lower=False):
    aligned1 = str1.lower() if to_lower else str1
    aligned2 = str2.lower() if to_lower else str2
    directions, alignment_matrix = needleman_wunsch(aligned1, aligned2, score_function, gap=gap)
    aligned1, aligned2 = build_globally_aligned_strings(str1, str2, directions, gap_char=gap_char)
    score = global_alignment_score(alignment_matrix)
    return score, aligned1, aligned2
