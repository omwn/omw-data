#!/usr/share/python  
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the Hebrew WordNet
# map from 16 to 30
# Omits orthographic variants or pronunciation
# Omits new synsets (103)
# Omits gloss 

import sys, re
import codecs, collections

### Change this!
wndata = "/home/bond/work/wns/HWN/hebrew_xml_cgirardi1180700635/"

wnname = "Hebrew Wordnet" 
wnurl =  "http://cl.haifa.ac.il/projects/mwn/index.shtml"
wnlang = "heb"
wnlicense = "wordnet"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )
log = codecs.open(outfile + '.log', "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s\n" % (wnname, wnlang, wnurl, wnlicense))

### mappings
###
mapdir = "/home/bond/work/wn/mapps/mapping-16-30/"
maps = ["wn16-30.adj", "wn16-30.adv", "wn16-30.noun", "wn16-30.verb"]
pos = {"wn16-30.adj" : "a", "wn16-30.adv" : "r", 
       "wn16-30.noun" : "n", "wn16-30.verb" : "v", }
map1630 = collections.defaultdict(lambda: 'unknown');
for m in maps:
    mf = codecs.open(mapdir + m, "r", "utf-8" )
    p = pos[m]
    for l in mf:
        lst = l.strip().split()
        fsfrom = lst[0] + "-" + p
        fsto = sorted([(lst[i+1], lst[i]) for i in range(1,len(lst),2)])[-1][1]
        ##print "%s-%s\t%s-%s" % (fsfrom, p, fsto, p)
        map1630[fsfrom] = "%s-%s" % (fsto, p)
#
# Data is in the file hebrew_synsets.xml  
# 
# 
# <synset id="06867794" pos="n">
#   <gloss>אלת השמיים המצרית</gloss>
#   <domains>Religion</domains>
#   <sumo type="@">CognitiveAgent</sumo>
#   <synonyms belongs="synset">
#     <lemma>נוּת</lemma>
#   </synonyms>
# </synset>
#
# New synsets have an id starting with 'H', we ignore them
# Get the gloss (just for fun)
#
synset = str()
lemma = str()
### need to do some cleanup, so store once to remove duplicate
wn = collections.defaultdict(lambda: collections.defaultdict(set))

f  = codecs.open(wndata + 'hebrew_synsets.xml', 'rb', encoding='utf-8')
for l in f:
    m = re.search(r'<synset id="([0-9H]\d{7})" pos="([avnr])"',l)
    if(m):
        ss = "%s-%s" % (m.group(1), m.group(2))
        synset = map1630[ss]
    i = re.finditer(r"<lemma>([^<]+)<",l)
    for m in i:
        lemma = m.group(1).strip()   
        #lemma = re.sub(r'[ _]\(.*\)', ' ', lemma).strip()
        lemma = re.sub(r'&quot;', '"', lemma).strip()
        if not ('&' in lemma or synset == 'unknown'):  ### reject bad entities
            wn[synset]["lemma"].add(lemma)
        else:
            log.write("Rejected lemma %s (%s %s)\n" % (lemma, synset, ss))
    i = re.finditer(r"<gloss>([^<]+)<",l)
    for m in i:
        gloss = m.group(1).strip()   
        gloss = re.sub(r'&amp;quot;', '"', gloss).strip()
        if not ('&' in gloss or synset == 'unknown'):  ### reject bad entities
            wn[synset]["def"].add(gloss)
        else:
            log.write("Rejected def %s (%s %s)\n" % (gloss, synset, ss))


for synset in sorted(wn):
    for attr in wn[synset]:
        sid = {attr:0}
        for val in wn[synset][attr]:
            if attr=='lemma':
                o.write("%s\t%s:%s\t%s\n" % (synset, wnlang,attr, val))
            elif attr == 'def':
                val = val.replace('"','')
                for v in val.split(";"):
                    o.write("%s\t%s:%s\t%s\t%s\n" % (synset, wnlang, attr, sid[attr], v.strip()))
                    sid[attr]+=1
