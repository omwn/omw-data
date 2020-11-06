#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the Japanese Wordnet
#

import sys
import codecs
#import re

wndata="data/"
wnname = "Japanese Wordnet" 
wnlang = "jpn"
wnurl = "http://nlpwww.nict.go.jp/wn-ja/"
wnlicense = "wordnet"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))

#
# Data is in the file wnjpn-all.tab
# offset<TAB>Japanese<TAB>Status

f = codecs.open(wndata + "wnjpn-all.tab", "rb", "utf-8" )

sysnset = str()
lemma = str()
for l in f:
    (synset, lemma, status) = l.strip().split("\t")
    lemma = lemma.strip()
    if status in ['hand', 'mlsn', 'mono', 'multi' ] and lemma:
        o.write("%s\t%s:lemma\t%s\n" % (synset, wnlang, lemma))
        ##print "%s\t%s\n" % (synset, lemma)

#
# Definition data is in the file wnjpn-def.tab
# offset<TAB>Japanese<TAB>Status

f = codecs.open(wndata + "wnjpn-def.tab", "rb", "utf-8" )

sysnset = str()
lemma = str()
for l in f:
    (synset, sid, eng, jpn) = l.strip().split("\t")
    sid = int(sid)
    o.write("%s\t%s:def\t%d\t%s\n" % (synset, 'eng', sid, eng))
    o.write("%s\t%s:def\t%d\t%s\n" % (synset, 'jpn', sid, jpn))
        ##print "%s\t%s\n" % (synset, lemma)

f = codecs.open(wndata + "wnjpn-exe.tab", "rb", "utf-8" )
sysnset = str()
lemma = str()
for l in f:
    (synset, sid, eng, jpn) = l.strip().split("\t")
    sid = int(sid)
    o.write("%s\t%s:exe\t%d\t%s\n" % (synset, 'eng', sid, eng))
    o.write("%s\t%s:exe\t%d\t%s\n" % (synset, 'jpn', sid, jpn))
