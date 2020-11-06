#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# By Francis Bond


import os
import codecs
import re
import nltk
from nltk.corpus import wordnet as wn

wndata= "data"

wnname = "Slovak WordNet" 
wnurl = "http://korpus.juls.savba.sk/WordNet_en.html"
wnlicense = "CC BY SA 3.0"
wnlang= 'slk'

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
out = codecs.open(outfile, "w", "utf-8" )
out.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))
    
##
## Data is in the file sk-wn-2013-01-23.txt
## id pos lemmas gloss ␞ offset lf pos

f = codecs.open(os.path.join(wndata, "sk-wn-2013-01-23.txt"),  "rb", "utf-8")
log = codecs.open("%s.log" % wnlang,  "w", "utf-8")

senses = set()

for l in f:
    (slv, eng) = l.strip().split(u'␞')
    engs = eng.strip().split()
    of = "{}-{}".format(engs[0],engs[2])
    (num, pos, lems, gloss) = slv.split('\t')
    # if gloss:
    #     print of, gloss
    for lll in lems.split(';'):
        ll= lll.strip()
        if ll.startswith('+'):
            ll = ll[1:]
        elif ll.startswith('-'):
            log.write("No Entry for %s %s\n" % (of,ll))
        elif '?' in ll:
            log.write("Dubious Entry for %s %s\n" % (of,ll))
        elif (of, ll) in senses:
            log.write("Duplicate Entry for %s %s\n" % (of,ll))
        else:
            senses.add((of, ll))
        #print of, ll.strip()
    # if m:
    #     lems = []
    #     key = m.group(1)
    #     try:
    #         ss = wn.lemma_from_key(key).synset #() for python 3
    #         of = "{:08d}-{}".format(ss.offset, ss.pos).replace('-s','-a')
    #     except:
    #         keys = [l.key for l in wn.lemmas(key.split('%')[0])]
    #         log.write("Can't find synset for '%s'\nTry: %s\n\n" % (key, keys))
    #     lems.append(m.group(2))
    #     if m.group(3):
    #         for ll in m.group(3).split(','):
    #             if ll.strip():
    #                 lems.append(ll.strip())
    #     ##print ss, lems
    #     for ll in lems:
    #         if '?' in ll:
    #             log.write("Ignore lemmas with '?': '%s' (%s)\n\n" % (ll, key))
    #         else:
    #             if (of, ll) in senses:
    #                 log.write("Duplicate Entry for %s %s\n\n" % (key,ll))
    #             else:
    #                 senses.add((of, ll))
    # else:
    #     log.write("Unknown '%s'\n\n" % l.strip())

for (of, ll) in senses:
    out.write("%s\t%s:lemma\t%s\n" % (of, wnlang,ll))



