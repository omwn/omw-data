#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the MultiLingual Central Repository
# Script updated by Eric Kafe (2022) for MCR-2016
#
# Creates four wordnets 
# cat Catalan
# eus Basque
# glg Galician
# spa Spanish

import sys
import codecs
import re

wndata= "/home/bond/svn/wn-msa/tab/"

wnname = "Multilingual Central Repository" 
wnurl = "http://adimen.si.ehu.es/web/MCR/"

wnlicense = "CC BY 3.0"

### Done to here!

wns_dir = "/tmp/wns"
mcr_version = "mcr30-2016"

#Some locales use comma as float separator:
commafloat=re.compile("\d,\d")

logf = codecs.open("MCR-log.txt", "w", "utf-8" )

for wnlang in ["cat", "glg", "spa", "eus"]:
    #
    # header
    #
    outfile = "wn-data-%s.tab" % wnlang
    om = codecs.open(outfile, "w", "utf-8" )
    om.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))

    ## Data is in the file
    ## synset\tlang\tgoodness\tlemma

    f = codecs.open("%s/%s/%sWN/wei_%s-30_variant.tsv" % (wns_dir, mcr_version, wnlang, wnlang),
    "rb", "utf-8")

    for l in f:
#        (lemma, rank, offset, pos, conf, src, note)
        attrs = l.strip().split("\t")
        offset = attrs[2]
        synset = offset[-10:]
        if int(synset[0]) < 8:  ### ignore new synsets
            lemma = attrs[0].replace("_", " ")
            if "," in lemma and not commafloat.match(lemma):
                logf.write(f"{offset}: truncating lemma '{lemma}'\n")
                lemma=lemma[:lemma.find(",")]  ### discard anything after a comma
            om.write("%s\tlemma\t%s\n" % (synset, lemma))
    f.close()


    ### FIXED also add gloss and examples:

    f = codecs.open("%s/%s/%sWN/wei_%s-30_synset.tsv" % (wns_dir, mcr_version, wnlang, wnlang),
    "rb", "utf-8")

    for l in f:
        attrs = l.strip().split("\t")
        if len(attrs)>6 and attrs[6] not in ["", "0", "None","NULL"]:
            offset = attrs[0]
            synset = offset[-10:]
            if int(synset[0]) < 8:  ### ignore new synsets
                om.write("%s\t%s:def\t0\t%s\n" % (synset, wnlang, attrs[6]))
    f.close()


    ### MCR links the examples to specific lemma ranks, which are not yet supported by OMW.
    ### So we can only attach the examples at the synset level, like in PWN:

    f = codecs.open("%s/%s/%sWN/wei_%s-30_examples.tsv" % (wns_dir, mcr_version, wnlang, wnlang),
    "rb", "utf-8")

    for l in f:
        attrs = l.strip().split("\t")
        if len(attrs)>4 and attrs[2] not in ["", "0", "None","NULL"]:
            offset = attrs[4]
            synset = offset[-10:]
            if int(synset[0]) < 8:  ### ignore new synsets
                om.write("%s\t%s:exe\t0\t%s\n" % (synset, wnlang, attrs[2]))
    f.close()

    om.close()
logf.close()
