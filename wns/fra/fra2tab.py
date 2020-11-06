#!/usr/share/python  
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the WOLF (Wordnet Libre du Français)
# Remap 'b' to 'r'
# Some clean up (remove ' ()', '|fr.*')

import sys, re
import codecs, collections

### Change this!
wndata = "/home/bond/work/wns/wolf/"

wnname = u"WOLF (Wordnet Libre du Français)" 
wnurl = "http://alpage.inria.fr/~sagot/wolf-en.html"
wnlang = "fra"
wnlicense = "CeCILL-C"
wnversion = "1.0b"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s\n" % (wnname, wnlang, wnurl, wnlicense))

#
# Data is in the file wolf-1.0b.xml  
#<?xml version="1.0" encoding="utf-8"?>
#<!DOCTYPE WN SYSTEM "debvisdic-strict.dtd">
#<WN>
#<SYNSET><ILR type="near_antonym">eng-30-00002098-a</ILR><ILR type="be_in_state">eng-30-05200169-n</ILR><ILR type="be_in_state">eng-30-05616246-n</ILR><ILR type="eng_derivative">eng-30-05200169-n</ILR><ILR type="eng_derivative">eng-30-05616246-n</ILR><ID>eng-30-00001740-a</ID><SYNONYM><LITERAL lnote="2/2:fr.csbgen,fr.csen">comptable</LITERAL></SYNONYM><DEF>(usually followed by `to') having the necessary means or skill or know-how or authority to do something</DEF><USAGE>able to swim</USAGE><USAGE>she was able to program her computer</USAGE><USAGE>we were at last able to buy a car</USAGE><USAGE>able to get a grant for the project</USAGE><BCS>3</BCS><POS>a</POS></SYNSET>

synset = str()
lemma = str()
### need to do some cleanup, so store once to remove duplicates
wn = collections.defaultdict(set)

f  = codecs.open(wndata + 'wolf-1.0b.xml', 'rb', encoding='utf-8')
for l in f:
    m = re.search(r'<ID>eng-30-(.*-[avnrb])<\/ID>',l)
    if(m):
        synset = m.group(1).strip().replace('-b', '-r')
    i = re.finditer(r"<LITERAL[^>]*>([^<]+)<",l)
    for m in i:
        lemma = m.group(1).strip()   
        #lemma = re.sub(r'[ _]\(.*\)', ' ', lemma).strip()
        #lemma = re.sub(r'\|fr.*$', '', lemma).strip()
        if lemma != '_EMPTY_':
            wn[synset].add(lemma)
        

for synset in sorted(wn):
    for lemma in wn[synset]:
        o.write("%s\t%s:%s\t%s\n" % (synset, wnlang, 'lemma', lemma))
