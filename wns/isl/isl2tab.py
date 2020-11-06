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

wnname = "IceWordNet" 
wnurl = "http://www.malfong.is/index.php?lang=en&pg=icewordnet"
wnlicense = "CC BY 3.0"
wnlang= 'isl'

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
out = codecs.open(outfile, "w", "utf-8" )
out.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))
    
##
## Data is in the file core-isl.txt
## pos [key] [lemma0] lemma1, lemma2, ...

f = codecs.open(os.path.join(wndata, "core-isl.txt"),  "rb", "iso-8859-1")
log = codecs.open("log",  "w", "utf-8")

pattern = re.compile(r'[avnr]\s+\[(.*?)\]\s+\[(.*?)\](.*)?')

senses = set()

for l in f:
    m = pattern.match(l.strip())
    if m:
        lems = []
        key = m.group(1)
        try:
            ss = wn.lemma_from_key(key).synset #() for python 3
            of = "{:08d}-{}".format(ss.offset, ss.pos).replace('-s','-a')
        except:
            keys = [l.key for l in wn.lemmas(key.split('%')[0])]
            log.write("Can't find synset for '%s'\nTry: %s\n\n" % (key, keys))
        lems.append(m.group(2))
        if m.group(3):
            for ll in m.group(3).split(','):
                if ll.strip():
                    lems.append(ll.strip())
        ##print ss, lems
        for ll in lems:
            if '?' in ll:
                log.write("Ignore lemmas with '?': '%s' (%s)\n\n" % (ll, key))
            else:
                if (of, ll) in senses:
                    log.write("Duplicate Entry for %s %s\n\n" % (key,ll))
                else:
                    senses.add((of, ll))
    else:
        log.write("Unknown '%s'\n\n" % l.strip())

for (of, ll) in senses:
    out.write("%s\t%s:lemma\t%s\n" % (of, wnlang,ll))
