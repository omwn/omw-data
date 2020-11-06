#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Get synset-word pairs for Danish, Nynorsk and Bokmal
#
# Core synsets courtesy of Lars Nygaard

import sys, re
import codecs

### Change this if you aren't me!
wndata = "/home/bond/work/wns/nor/"


wnname = "DanNet" 
wnurl = "http://wordnet.dk/lang"
wnlicense = "wordnet"


#
# Data is in the files 
# wn.nno, wn.non
# ID<TAB>WN20<TAB>WN30<TAB>lemma
# 

log = codecs.open("log", "w", "utf-8" )

# I# IDs id2ss = dict()
for wnlang in ['dan']:
    ### output file
    outfile = "wn-data-%s.tab" % wnlang
    out = codecs.open(outfile, "w", "utf-8" )
    ### header
    out.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))
    f = codecs.open(wndata + 'wn.' +wnlang,  'r', "utf-8")
    for l in f:
        ##print l
        lst = l.strip().split('\t')
        synset = lst[2][-10:]
        if synset.endswith('s'):
            synset = synset[:-1] + 'a'
            log.write('Satellite changed to:\tsynset\n')
        for lemma in lst[3:]:
            out.write("%s\tlemma\t%s\n" % (synset, lemma))
