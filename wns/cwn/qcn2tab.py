#!/usr/share/python  
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the Academica Sinica Chinese WordNet
# map from 16 to 30
# Omits orthographic variants or pronunciation
# Omits new synsets (103)
# Omits gloss 

import sys, re
import codecs, collections

### Change this!
wndata = "/home/bond/Downloads/"

wnname = "Chinese Wordnet (Taiwan)" 
wnurl =  "http://lope.linguistics.ntu.edu.tw/cwn/"
wnlang = "qcn"
wnlicense = "wordnet"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )
log = codecs.open(outfile + '.log', "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s\n" % (wnname, wnlang, wnurl, wnlicense))

### mappings
###
mapdir = "/home/bond/work/wn/mapps/mapping-16-30/"
maps = ["wn16-30.adj", "wn16-30.adv", "wn16-30.noun", "wn16-30.verb"]
pos = {"wn16-30.adj" : "a", "wn16-30.adv" : "r", 
       "wn16-30.noun" : "n", "wn16-30.verb" : "v", }
map1630 = collections.defaultdict(lambda: 'unknown');
for m in maps:
    mf = codecs.open(mapdir + m, "r", "utf-8" )
    p = pos[m]
    for l in mf:
        lst = l.strip().split()
        fsfrom = lst[0] + "-" + p
        fsto = sorted([(lst[i+1], lst[i]) for i in range(1,len(lst),2)])[-1][1]
        ##print "%s-%s\t%s-%s" % (fsfrom, p, fsto, p)
        map1630[fsfrom] = "%s-%s" % (fsto, p)
synset = str()
lemma = str()
### need to do some cleanup, so store once to remove duplicate
wn = collections.defaultdict(lambda: collections.defaultdict(set))

f  = codecs.open(wndata + 'wn-data-qcn.tab.txt', 'rb', encoding='utf-8')
for l in f:
    if l.startswith('#'):
        continue
    ##print l
    (wnid, kind, lemma) = l.strip().split('\t')
    if  (len(wnid) == 9):
        ss = "%s-%s" % (wnid[:8], wnid[8].lower())
        synset = map1630[ss]
        if synset !=  "unknown":
            o.write("%s\t%s\t%s\n" % (synset, kind, lemma))
        else:
            log.write("Rejected lemma %s (%s) couldn't convert from 1.6\n" % (lemma,wnid))
    else:
        log.write("Rejected lemma %s (%s)\n" % (lemma,wnid))

