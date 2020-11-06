#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# By Francis Bond and Giulia Bonansinga
#
# Extract synset-word pairs from the MultiWordNet
#
# Creates one wordnet (Italian) linked from PWN 1.6 


import sys
import codecs
#import re

wndata= "/home/bond//MWN_1.5.0/"

wnname = "MultiWordNet" 
wnurl = "http://multiwordnet.fbk.eu/english/home.php"
wnlicense = "CC BY 3.0"
wnlang= 'ita'

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
out = codecs.open(outfile, "w", "utf-8" )
out.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))

###
### mappings
###
mapdir = "../../data/mapps/mapping-16-30/"
maps = ["wn16-30.adj", "wn16-30.adv", "wn16-30.noun", "wn16-30.verb"]
pos = {"wn16-30.adj" : "a", "wn16-30.adv" : "r", 
       "wn16-30.noun" : "n", "wn16-30.verb" : "v", }
map1630 = dict();
for m in maps:
    mf = codecs.open(mapdir + m, "r", "utf-8" )
    p = pos[m]
    for l in mf:
        lst = l.strip().split()
        fsfrom = lst[0] + "-" + p
        fsto = sorted([(lst[i+1], lst[i]) for i in range(1,len(lst),2)])[-1][1]
        ##print "%s\t%s-%s" % (fsfrom, fsto, p)
        map1630[fsfrom] = "%s-%s" % (fsto, p)


    
##
## Data is in the file italian_synset.sql  
## synset\tlang\tgoodness\tlemma

f = codecs.open(wndata + "italian_synset.sql",  "rb", "utf-8")
log = codecs.open("log",  "w", "utf-8")

for l in f:
    if l.startswith("INSERT INTO italian_synset VALUES"):
        dat = l[35:-3].strip().replace('NULL', "''")[1:-1]
        ##print dat
        (wnid, words, phrases, defex) = dat.split("','")
        ss = '%s-%s' % (wnid[2:], wnid[0])
        if ss in map1630: ## lose new and unmappable synsets
            synset = map1630[ss]
            for lemma in words.strip().split():
                lemma = lemma.replace("_", " ")
                lemma = lemma.replace("\\'", "'")
                if lemma:
                    out.write("%s\t%s:lemma\t%s\n" % (synset, wnlang,lemma))
            for phrase in phrases.strip().split():
                phrase = phrase.replace("_", " ")
                phrase = phrase.replace("\\'", "'")
                if phrase: ### FIXME show these are phrases
                    out.write("%s\t%s:lemma\t%s\n" % (synset, wnlang,phrase))
                    log.write("Phrase: %s\n" % phrase)
            if defex:
                defs=defex.split('; ')
                did =0
                eid =0
                for d in defs:
                    d=d.replace("\\'","'")
                    if d.startswith('"'):
                        e = d.strip('"')
                        out.write("%s\t%s\t%d\t%s\n" % (synset, "ita:exe", eid, e))
                        eid +=1
                    else:
                        out.write("%s\t%s\t%d\t%s\n" % (synset, "ita:def", did, d))
                        did +=1
        else:
            log.write("Unknown synset '%s'\n" % ss)

    ### FIXME also add gloss and examples

