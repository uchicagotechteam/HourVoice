import re
import string
import csv
from collections import Counter
from collections import defaultdict
import sys

columns = defaultdict(list)
csv_file = 'Business_Licenses.csv'

#expanding max size for csv rows
maxInt = sys.maxsize
decrement = True

while decrement:
    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/10)
        decrement = True

#make dictionary of columns
with open(csv_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        for (k,v) in enumerate(row):
            columns[k].append(v)
    f.close()

names = (' '.join(columns[4][1:] + columns[5][1:])).lower().split()
c = Counter(names)

with open('name_freqs.txt', 'w') as f:
    for (word, freq) in c.most_common(300):
        f.write(word + ' ' + str(freq) + '\n')
