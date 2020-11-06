#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the MultiLingual Central Repository
#
# Creates four wordnets 
# cat Catalan
# eus Basque
# glg Galician
# spa Spanish

import sys
import codecs
#import re

wndata= "/home/bond/svn/wn-msa/tab/"

wnname = "Multilingual Central Repository" 
wnurl = "http://adimen.si.ehu.es/web/MCR/"

wnlicense = "CC BY 3.0"

### Done to here!

for wnlang in ["cat", "glg", "spa", "eus"]:
    #
    # header
    #
    outfile = "wn-data-%s.tab" % wnlang
    om = codecs.open(outfile, "w", "utf-8" )
    om.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))
    
##
## Data is in the file 
## synset\tlang\tgoodness\tlemma

    f = codecs.open("/home/bond/work/wns/mcr30/%sWN/wei_%s-30_variant.tsv" % (wnlang, wnlang),
    "rb", "utf-8")
    
    for l in f:
        (lemma, rank, offset, pos, conf, src, note) = l.strip().split("\t")
        lemma = lemma.replace("_", " ")
        synset = offset[-10:]
        if int(synset[0]) < 8:  ### ignore new synsets
            om.write("%s\tlemma\t%s\n" % (synset, lemma))
        ##print "%s\t%s\n" % (synset, lemma)

    ### FIXME also add gloss and examples

