#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# By Francis Bond and Giulia Bonansinga
#
# Extract synset-word pairs from the MultiWordNet
#
# Creates one wordnet (Italian) linked from PWN 1.6 


import os
import codecs
#import re

wndata= "data"

wnname = "ItalWordnet" 
wnurl = "http://datahub.io/dataset/iwn/"
wnlicense = "ODC-BY 1.0"
wnlang= 'ita'

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
out = codecs.open(outfile, "w", "utf-8" )
out.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))
    
##
## Data is in the file italian_synset.sql  wn-data-itl-corrected.tab
## synset\tlang\tgoodness\tlemma

f = codecs.open(os.path.join(wndata, "wn-data-itl-corrected.tab"),  "rb", "utf-8")
log = codecs.open("log",  "w", "utf-8")

for l in f:
    things = l.strip().split('\t')
    if len(things) != 3:
        log.write("Not 3 things '%s'\n" % l.strip())
        continue
    (synset, typ, thing) = l.strip().split('\t')
    if typ == 'itl:lemma':
        lemma = thing.replace("_", " ").strip()
        if lemma:
            out.write("%s\t%s:lemma\t%s\n" % (synset, wnlang,lemma))
    elif typ == 'itl:def':
        did =0
        for df in thing.split(';'):
            d = df.strip().strip('.')
            if d:
                out.write("%s\t%s\t%d\t%s\n" % (synset, "ita:def", did, d))
                did +=1
    else:
        log.write("Unknown '%s'\n" % l.strip())

    ### FIXME also add gloss and examples

