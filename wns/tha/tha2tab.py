#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the Persian Wordnet
#

import sys
import codecs
import re

wnname = "Thai" 
wnlang = "tha"
wnurl = "http://th.asianwordnet.org/"
wnlicense = "wordnet"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))

#
# Data is in the file tha-wn-1.0-lmf.xml
# <Lemma writtenForm=" กระบวนการทรานแอมมิแนชัน " partOfSpeech="n" />
# <Sense id="w1_13567960-n" synset="tha-07-13567960-n" />
# exploit the fact that the synset is the same as wn3.0 offset

f = codecs.open("tha-wn-1.0-lmf.xml", "r", "utf-8" )

sysnset = str()
lemma = str()
for l in f:
    m = re.search(r"<Lemma writtenForm=\"([^\"]*)\" part",l)
    if(m):
        lemma = m.group(1).strip()  
    m = re.search(r"synset=\"tha-07-(.*)\"",l)
    if(m):
        synset = m.group(1)   
        o.write("%s\t%s\n" % (synset, lemma))
        ##print "%s\t%s\n" % (synset, lemma)
