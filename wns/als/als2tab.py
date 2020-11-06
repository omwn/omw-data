#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs, definitions and others from the Albanian Wordnet
#
#

import sys
import codecs
import re, collections


wndata="/home/bond/work/wns/albanian/"
wnname = "Albanet" 
wnlang = "als"
wnurl = "http://fjalnet.com/"
wnlicense = "CC BY 3.0"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )
log = codecs.open("log", "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))

###
### mappings
###
mapdir = "/home/bond/work/wn/mapps/mapping-20-30/"
maps = ["wn20-30.adj", "wn20-30.adv", "wn20-30.noun", "wn20-30.verb"]
pos = {"wn20-30.adj" : "a", "wn20-30.adv" : "r", 
       "wn20-30.noun" : "n", "wn20-30.verb" : "v", }
map2030 = collections.defaultdict(lambda: 'unknown');
for m in maps:
    mf = codecs.open(mapdir + m, "r", "utf-8" )
    p = pos[m]
    for l in mf:
        lst = l.strip().split()
        fsfrom = lst[0] + "-" + p
        fsto = sorted([(lst[i+1], lst[i]) for i in range(1,len(lst),2)])[-1][1]
        ##print "%s-%s\t%s-%s" % (fsfrom, p, fsto, p)
        map2030[fsfrom] = "%s-%s" % (fsto, p)


#
# Data is in the file shqip.xml
#
# But xml parser complains :-)  so back to regexp
#


f = codecs.open(wndata + "shqip.xml", "r", "utf-8" )

synset = unicode()
lemma = unicode()
#of20 = unicode()
defid = 0
exid = 0

for l in f:
    ##print l, "EOS"
    ### synset
    m = re.search(r"<ID>(.*)</ID>",l.strip())
    if (m):
        synset20 = m.group(1).strip()[6:]
        synset = map2030[synset20]
        defid = 0
        exid = 0
    ### lemma
    m = re.search(r"<LITERAL>(.+)<SENSE>(.*)</SENSE>",l.strip())
    if(m):
        lemma = m.group(1).strip()  
        sense = m.group(2).strip()  
        if lemma == '' or synset=='unknown':
            log.write("Problem with synset/lemma:  {} ({}) {}\n".format(synset20, synset, sense))
        else:
            o.write("%s\t%s:%s\t%s\n" % (synset, wnlang, 'lemma', lemma))
    ### Definition
    m = re.search(r"<DEF>(.+)</DEF>",l.strip())
    if(m):
        df = m.group(1).strip()  
        if df == '' or synset=='unknown':
            log.write("Problem with synset/def:  {} ({})\n".format(synset20, synset))
        else:
            o.write("%s\t%s:%s\t%d\t%s\n" % (synset, wnlang, 'def', defid, df))
            defid += 1
    ### Example
    m = re.search(r"<USAGE>(.+)</USAGE>",l.strip())
    if(m):
        ex = m.group(1).strip()  
        if ex == '' or synset=='unknown':
            log.write("Problem with synset/exe:  {} ({})\n".format(synset20, synset))
        else:
            o.write("%s\t%s:%s\t%d\t%s\n" % (synset, wnlang, 'exe', exid, ex))
            exid += 1
