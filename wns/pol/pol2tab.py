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
import nltk
from nltk.corpus import wordnet as pwn
import HTMLParser
h = HTMLParser.HTMLParser()


### Change this!
wndata = "/home/bond/work/wns/plwordnet_2_3/"    # is run on the same folder

wnname = "plWordNet" 
wnurl =  "http://plwordnet.pwr.wroc.pl/wordnet/"
wnlang = "pol"
wnlicense = "wordnet"
wnversion = "2.3"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )
log = codecs.open(outfile + '.log', "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s\n" % (wnname, wnlang, wnurl, wnlicense))


#
# Data is in the file plwordnet_2_3_visdic.xml 
#
# PWN synsets look like this
# extract lemma, pos, sense to get PWN synset
# link is <ILR>PLWN-00013781-n<TYPE>Syn_plWN-PWN</TYPE></ILR>
#
# <SYNSET>
#   <ID>PLWN-00153273-n_pwn</ID>
#   <POS>n_pwn</POS>
#   <SYNONYM>
#     <LITERAL>wheelchair<SENSE>1</SENSE></LITERAL>
#   </SYNONYM>
#   <ILR>PLWN-00143920-n_pwn<TYPE>Hypernym</TYPE></ILR>
#   <ILR>PLWN-00142725-n_pwn<TYPE>Hyponym</TYPE></ILR>
#   <ILR>PLWN-00148573-n_pwn<TYPE>Hyponym</TYPE></ILR>
#   <ILR>PLWN-00013781-n<TYPE>Syn_plWN-PWN</TYPE></ILR>
#   <DEF></DEF>
#   <USAGE></USAGE>
#   <DOMAIN>wytw =&gt; EN -&gt; wytwory ludzkie(nazwy)</DOMAIN>
# </SYNSET> 
#
# We get the actual Polish data from a synset that looks like this:
#
# <SYNSET>
#   <ID>PLWN-00013781-n</ID>
#   <POS>n</POS>
#   <SYNONYM>
#     <LITERAL>wózek inwalidzki<SENSE>1</SENSE></LITERAL>
#   </SYNONYM>
#   <ILR>PLWN-00007389-n<TYPE>hypernym</TYPE></ILR>
#   <ILR>PLWN-00073909-n<TYPE>element kolekcji</TYPE></ILR>
#   <ILR>PLWN-00153273-n_pwn<TYPE>Syn_PWN-plWN</TYPE></ILR>
#   <DEF></DEF>
#   <USAGE></USAGE>
#   <DOMAIN>wytw =&gt; EN -&gt; wytwory ludzkie(nazwy)</DOMAIN>
# </SYNSET>
# 
synset = str()
lemma = str()
### need to do some cleanup, so store once to remove duplicate

## wn[id] set of lemmas
wn = collections.defaultdict(set)
## lnk[pid] = pwnid
lnk = collections.defaultdict(set)
id = ''
pos = ''

f  = codecs.open(wndata + 'plwordnet_2_3_visdic.xml', 'rb', encoding='utf-8')
for l in f:
    ## ID
    m = re.search(r'<ID>(.*)</ID>',l)
    if(m):  
        id = m.group(1)
    ## POS (actually in ID, but just in case).
    m = re.search(r'<POS>(.)',l)
    if(m):
        pos = m.group(1)  ## why oh why can't we all use the same pos
        if pos == 'a':
            pos = 'r'
        elif pos == 'j':
            pos = 'a'

    ## LINK (only ever one, but make it a list just in case)
    ## 228 międzyjęzykowa_synonimia_międzyrejestrowa_plWN-PWN: 
    ##  interlingual inter-register synonymy
    ## 225 międzyjęzykowa_synonimia_częściowa_plWN-PWN: interlingual near-synonymy
    ## 208  Syn_plWN-PWN: interlingual synonymy
    m = re.search(ur'<ILR>([^<]+)<TYPE>(międzyjęzykowa_synonimia_międzyrejestrowa_plWN-PWN|międzyjęzykowa_synonimia_częściowa_plWN-PWN|Syn_plWN-PWN)</TYPE></ILR>',l)
    if(m):
        lnk[id].add(m.group(1))
    ## Lemmas
    i = re.finditer(r"<LITERAL>([^<]+)<SENSE>([^<]+)</SENSE></LITERAL>",l)
    for m in i:
        lemma = h.unescape(m.group(1))
        if id.endswith('pwn'):
            mm = re.search(r'(.*)(\([^)]+\))$', lemma)
            if mm:
                log.write("Strip %s from '%s'\n" % (mm.group(2), lemma))
                lemma = mm.group(1)
        wn[id].add((lemma, pos, m.group(2)))

        # if not ('&' in lemma or synset == 'unknown'):  ### reject bad entities
        #     wn[synset]["lemma"].add(lemma)
        # else:
        #     log.write("Rejected lemma %s (%s %s)\n" % (lemma, synset, ss))

def getoffset (lemma, pos, sense):
    try:
        return "%08d-%s" % \
            (pwn.synset('%s.%s.%s' % (lemma.replace(' ', '_'), pos, sense)).offset,
             pos)
    except:
        log.write("No offset found for %s.%s.%s\n" % (lemma.replace(' ', '_'), pos, sense))
        return ""

for id in sorted(wn):
    if id.endswith('pwn'):
        off = ""
        while (wn[id] and not off):
             (lemma, pos, sense) = wn[id].pop()
             off = getoffset(lemma, pos, sense)
        if off and lnk[id]:
            ln = lnk[id].pop()
            for (lemma, pos, sense) in wn[ln]:
                o.write("%s\t%s\t%s\n" % (off, 'pol:lemma', lemma))
