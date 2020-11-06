#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the Finnish Wordnet
#

import sys
import codecs
import re

wndata="/home/bond/work/wns/fiwn-1.1.2/lists/"
wnname = "FinnWordNet" 
wnlang = "fin"
wnurl = "http://www.ling.helsinki.fi/en/lt/research/finnwordnet/"
wnlicense = "CC BY 3.0"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))

#
# Data is in the file fiwn-synsets.tsv
# offset<TAB>POS<TAB>SYN | SYN |SYN <TAB>...

f = codecs.open(wndata + "fiwn-synsets.tsv", "rb", "utf-8" )
posmap = {'N':'n', 'V':'v','A':'a','Adv':'r',}

sysnset = str()
lemma = str()
for l in f:
    (synset, pos, lemmas, gloss, engs, hypers, lfile) = l.strip().split("\t")
    for lemma in lemmas.split(" | "):
        ## delete mysterious tags and tagged text
        if "<huom>" in lemma:
            continue
        else:
              lemma = re.sub(r'<[^>]+/>', ' ', lemma).strip()
        o.write("%s-%s\tlemma\t%s\n" % (synset[1:], posmap[pos], lemma))
        ##print "%s\t%s\n" % (synset, lemma)
