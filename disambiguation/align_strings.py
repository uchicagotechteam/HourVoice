import numpy as np
from functools import lru_cache

@lru_cache(maxsize=128)
def get_matching_score(a, b, match=5, mismatch=-4):
    return match if a == b else mismatch


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


def build_globally_aliged_strings(str1, str2, directions, gap_char='-'):
    x, y = len(directions)-1, len(directions[0])-1
    old_x, old_y = x, y
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


def alignment_score(aligned_str1, aligned_str2):
    # currenly naive, fraction of matches which are identical
    min_len, max_len = len(aligned_str1), len(aligned_str2)
    min_len, max_len = (min_len, max_len) if min_len < max_len else (max_len, min_len)
    num_identities = 0
    for i in range(min_len):
        if aligned_str1[i] == aligned_str2[i]:
            num_identities += 1
    return num_identities / max_len


def align_strings_globally(str1, str2, gap=-1, gap_char='-', to_lower=True):
    aligned1 = str1.lower() if to_lower else str1
    aligned2 = str2.lower() if to_lower else str2
    directions, alignment_matrix = needleman_wunsch(aligned1, aligned2, get_matching_score, gap=gap)
    aligned1, aligned2 = build_globally_aliged_strings(str1, str2, directions, gap_char=gap_char)
    score = alignment_score(aligned1, aligned2)
    return score, aligned1, aligned2
