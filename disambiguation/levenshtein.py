# Levenshtein Distance Calculator

def collapse_delimiters(s, delimiter=' '):
    i, n = 0, len(s)
    res = ''
    while i < n:
        if s[i].isalnum():
            res += s[i]
            i += 1
        else:
            res += delimiter
            while i < n and not s[i].isalnum():
                i += 1
    return res


def levenshtein(s1, s2, preprocess=False):
    if preprocess:
        s1 = s1.lower()
        s2 = s2.lower()
        s1 = collapse_delimiters(s1)
        s2 = collapse_delimiters(s2)

    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
