import re
import string
import csv
from collections import Counter
from collections import defaultdict
import sys

c=Counter()

columns = defaultdict(list)
csv_file = r'''C:\Users\walsh\Documents\Hour Voice\Business_Licenses.txt'''

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
    #reader.next()
    for row in reader:
        for (k,v) in enumerate(row):  
            columns[k].append(v)
    f.close()

#look at one column, turn it into a string to regex over
col=columns[4]

with open(r'''C:\Users\walsh\Documents\Hour Voice\bl_freq.txt''', 'w') as t:
    for c in columns:
        t.write(str(c))
    t.close()

##col_string=" ".join(col)
##
##lower_col=col_string.lower()
##
##match_pattern = re.findall(r'\b[a-z]{2,15}\b', lower_col)
##
##for word in match_pattern:
##    c[word]+=1
##
###write most common regex finds to file
##with open(r'''C:\Users\walsh\Documents\Hour Voice\bl_freq.txt''', 'w') as h:
##    for k,v in  c.most_common():
##        h.write( "{} {}\n".format(k,v) )
##    h.close()
##
##print("file done")    
