import numpy as np
import string
import os
from global_alignment import align_strings_globally
# from functools import lru_cache

def get_stop_words():
    stop_words = []
    with open(os.path.abspath('../../disambiguation/company_name_stop_words.txt'), 'r') as f:
        stop_words = f.read().split()
    return stop_words

# globally initialized to prevent IO overhead each time
stop_words = get_stop_words()


def preprocess(s, min_length=2, remove_punctuation=False, remove_stop_words=True):
    mod_s = s
    if remove_punctuation:
        mod_s = mod_s.translate(None, string.punctuation)
    if remove_stop_words:
        words = [x for x in mod_s.split() if len(x) >= min_length and x.lower() not in stop_words]
        mod_s = ' '.join(words)
    return mod_s

# @lru_cache(maxsize=128)
def get_matching_score(a, b, match=5, similar=4, mismatch=-4):
    delimiters = string.punctuation + ' '
    if a == b:
        return match
    elif a.lower() == b.lower():
        return similar
    elif a in delimiters and b in delimiters:
        return similar
    else:
        return mismatch


def fraction_of_identities(aligned_str1, aligned_str2):
    '''Returns the fraction of matches which are identical'''
    min_len, max_len = len(aligned_str1), len(aligned_str2)
    min_len, max_len = (min_len, max_len) if min_len < max_len else (max_len, min_len)
    num_identities = 0
    for i in range(min_len):
        if aligned_str1[i] == aligned_str2[i]:
            num_identities += 1
    return float(num_identities) / max_len


def align_strings(str1, str2, gap=-1, gap_char=' ', remove_stop_words=True, min_length=2, remove_punctuation=True, to_lower=False):
    str1_mod = preprocess(str1, min_length=min_length, remove_punctuation=remove_punctuation, remove_stop_words=remove_stop_words)
    str2_mod = preprocess(str2, min_length=min_length, remove_punctuation=remove_punctuation, remove_stop_words=remove_stop_words)
    if not str1_mod or not str2_mod: # only stop words in string
        return (0, '', '')
    return align_strings_globally(str1_mod, str2_mod, gap=gap, gap_char=gap_char, score_function=get_matching_score, to_lower=to_lower)
