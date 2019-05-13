from itertools import groupby
import sys
# "chunk" our input file, delimited by blank lines

srt_file = sys.argv[1]
srt2txt_file = sys.argv[2]

with open(srt_file) as f:
    res = [list(g) for b,g in groupby(f, lambda x: bool(x.strip())) if b]
    
from collections import namedtuple

Subtitle = namedtuple('Subtitle', 'number start end content')

subs = []

all_text = ''

for sub in res:
    #if len(sub) >= 3: # not strictly necessary, but better safe than sorry
        sub = [x.strip() for x in sub]
        number = sub[0]
        start_end = sub[1]
        start, end = start_end.split(' --> ')
        content = " ".join(sub[2:])
        all_text +="\n"+content
        subs.append(Subtitle(number, start, end, content))

out_file = open(srt2txt_file, "w")

out_file.write(all_text[1:])
out_file.close()