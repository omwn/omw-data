#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the Persian Wordnet
#

import sys
import codecs
wndata= "/home/bond/work/wns/persian/"
wnname = "Persian Wordnet" 
wnurl = "http://www.pwn.ir"
wnlang = "fas"
wnlicense = "Free to use"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))

#
# Data is in the file Word.txt
# سرزمین عجایب;Noun:5632175;wonderland#n#2

f = codecs.open(wndata + "Word.txt", "r", "utf-8" )

posmap = {'Noun':'n', 'Adjective':'a', 'Adverb':'r', 'Verb':'v'}

for l in f:
    (lemma, synset, eng) = l.split(';')
    (pos, offset) = synset.split(':')
    o.write("%08d-%s\tlemma\t%s\n" % (int(offset), posmap[pos], lemma))
