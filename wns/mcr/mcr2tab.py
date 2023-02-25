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

from collections import defaultdict

wndata= "/home/bond/svn/wn-msa/tab/"

wnname = "Multilingual Central Repository" 
wnurl = "http://adimen.si.ehu.es/web/MCR/"

wnlicense = "CC BY 3.0"

### Done to here!

wns_dir = "/tmp/wns"
mcr_version = "mcr30-2016"

# Some locales use comma as float separator:
commafloat = re.compile("\d,\d")

# Recognize space before punctuation:
spacepunct = re.compile(" [,.:;!?]")

# Space at the end of string:
endspace = re.compile(" $")

logf = codecs.open("MCR-log.txt", "w", "utf-8" )

def normalize(text0, context='string', where=None):
    """Normalize space around punctuation and at end of string"""
    text = text0.replace('??', ' ').replace('_', ' ')
    while spacepunct.search(text):
        i = spacepunct.search(text).start()
        text = text[:i] + text[i+1] + ' ' + text[i+2:]
    text = text.replace('  ', ' ')
    e = endspace.search(text)
    if e:
        text = text[:e.start()]
    if text != text0:
        logf.write(f"{where}, normalize space in {context}: '{text0}'\n -> '{text}'\n")
    return text

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

    tmpdict = defaultdict(set)    # Filter, to avoid duplicates

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
            tmpdict[synset].add(lemma)
    f.close()

    for synset in sorted(tmpdict.keys()):
        for lemma in sorted(list(tmpdict[synset])):
            om.write("%s\t%s:lemma\t%s\n" % (synset, wnlang, lemma))


    ### FIXED also add gloss and examples:

    f = codecs.open("%s/%s/%sWN/wei_%s-30_synset.tsv" % (wns_dir, mcr_version, wnlang, wnlang),
    "rb", "utf-8")

    tmpdict = defaultdict(set)

    for l in f:
        attrs = l.strip().split("\t")
        if len(attrs)>6 and attrs[6] not in ["", "0", "None","NULL"]:
            offset = attrs[0]
            synset = offset[-10:]
            if int(synset[0]) < 8:  ### ignore new synsets
                tmpdict[synset].add(normalize(attrs[6], 'definition', offset))
    f.close()

    for synset in sorted(tmpdict.keys()):
        for definition in sorted(list(tmpdict[synset])):
            om.write("%s\t%s:def\t0\t%s\n" % (synset, wnlang, definition))


    ### MCR links the examples to specific lemma ranks, which are not yet supported by OMW.
    ### So we can only attach the examples at the synset level, like in PWN:

    f = codecs.open("%s/%s/%sWN/wei_%s-30_examples.tsv" % (wns_dir, mcr_version, wnlang, wnlang),
    "rb", "utf-8")

    tmpdict = defaultdict(set)

    for l in f:
        attrs = l.strip().split("\t")
        if len(attrs)>4 and attrs[2] not in ["", "0", "None","NULL"]:
            offset = attrs[4]
            synset = offset[-10:]
            if int(synset[0]) < 8:  ### ignore new synsets
                tmpdict[synset].add(normalize(attrs[2], 'example', offset))
    f.close()

    for synset in sorted(tmpdict.keys()):
        for example in sorted(list(tmpdict[synset])):
            om.write("%s\t%s:exe\t0\t%s\n" % (synset, wnlang, example))


    om.close()
logf.close()
