import numpy as np

def needleman_wunsch(str1, str2, scores, gap):
    n1, n2 = len(str1), len(str2)
    alignment_matrix = np.zeros((n1+1,n2+1))
    for i in range(n1+1):
        alignment_matrix[i][0] = gap * i
    for j in range(n2+1):
        alignment_matrix[0][j] = gap * j
    for i in range(1,n1+1):
        for j in range(1,n2+1):
            from_above = alignment_matrix[i-1][j] + gap
            from_left = alignment_matrix[i][j-1] + gap
            from_diag = alignment_matrix[i-1][j-1] + scores[(str1[i-1][j-1])]
            alignment_matrix[i][j] = max(from_above, from_left, from_diag)
    return alignment_matrix
