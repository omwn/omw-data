
import sys
import codecs
#import re

wndata= "/home/bond/work/wn/COW/0.9/"

wnname = "Chinese Open Wordnet" 
wnlang = "cmn"
wnurl = "http://compling.hss.ntu.edu.sg/cow/"
wnlicense = "wordnet"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )
o.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))

#
# Data is in the file wn-msa-all.tab
# synset\tlang\tgoodness\tlemma

f = codecs.open(wndata +"cow-not-full.txt", "rb", "utf-8" )

#synset = str()
#lemma = str()
known = set()
for l in f:
    if l.startswith('#') or not l.strip():
        continue
    row = l.strip().split("\t")
    if len(row) ==3:
        (synset, lemma, status) = row
    elif len(row) ==2:
        (synset, lemma) = row 
        status ='Y'
    else:
        print "illformed line: ", l.strip()
    if status in ['Y', 'O' ]:  # can I make this a set
        if not (synset.strip(), lemma.strip()) in known:
            o.write("%s\t%s:lemma\t%s\n" % (synset.strip(), wnlang, lemma.strip()))
            known.add((synset.strip(), lemma.strip()))
