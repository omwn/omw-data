#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the Arabic Wordnet
#

import sys, re
import codecs
import csv
import lxml.etree as ET
from lxml.etree import  SubElement, tostring, fromstring
from collections import defaultdict as dd
### Change this!
wndata = "/home/bond/work/wns/AWN2/"


wnname = "Arabic WordNet (AWN v2)" 
wnurl = "http://www.globalwordnet.org/AWN/"
wnlang = "arb"
wnlicense = "CC BY SA 3.0"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s\n" % (wnname, wnlang, wnurl, wnlicense))

log = codecs.open(outfile + '.log', "w", "utf-8" )



### mappings
###
mapdir = "/home/bond/work/wn/mapps/mapping-20-30/"
maps = ["wn20-30.adj", "wn20-30.adv", "wn20-30.noun", "wn20-30.verb"]
pos = {"wn20-30.adj" : "a", "wn20-30.adv" : "r", 
       "wn20-30.noun" : "n", "wn20-30.verb" : "v", }
map2030 = dict();
for m in maps:
    mf = codecs.open(mapdir + m, "r", "utf-8" )
    p = pos[m]
    for l in mf:
        lst = l.strip().split()
        fsfrom = lst[0] + "-" + p
        fsto = sorted([(lst[i+1], lst[i]) for i in range(1,len(lst),2)])[-1][1]
        ##print "%s-%s\t%s-%s" % (fsfrom, p, fsto, p)
        map2030[fsfrom] = "%s-%s" % (fsto, p)

## Data that links the AWN to PWN is in the original AWN
id2ss = dict()  ### takes arabic synset ID and returns PWN 3.0 ID

linkreader = csv.reader(open('/home/bond/work/wns/AWN/CSV/item.csv', 'rb'), delimiter=',', quotechar='"')
for row in linkreader:
    ## only accept PWN synsets and actual IDs
    if row[3]  and row[3].endswith('AR'):
        ## print row[3], row[6][1:] + "-" + row[7]
        ## only accept synsets we can map
        ss = row[6][1:] + "-" + row[7]
        if  ss in map2030:
            id2ss[row[3]] = map2030[ss]
        else:
            log.write(u"No mapping of AWN ID {} '{}'.\n".format(row[3], 
                                                                   row[1].decode('utf-8')))



# Data is in the file awn_ext_lmf_fusion.xml
#
#
sys.stderr.write('Reading XML\n')
parser = ET.XMLParser(remove_blank_text=True)
# tree = etree.parse(filename, parser)
# remove_blank_text=True
tree = ET.parse(wndata + 'awn_ext_lmf_fusion.xml')
root = tree.getroot()

#
# It should be LMF
#
# Ignoring the root and broken plural for now
#
known = set()
for lexent in root.iter('LexicalEntry'):
    ssid = lexent.find('Sense').get('synset').strip()
    for lemma in lexent.iter('Lemma'):
        lem =lemma.get('writtenForm').strip()
        if ssid in id2ss:
            if (lem, id2ss[ssid]) not in known:
                o.write("%s\t%s:%s\t%s\n" % (id2ss[ssid], 
                                             wnlang, 'lemma', 
                                             lem))
                known.add((lem, id2ss[ssid]))
            else:
                log.write(u"Duplicate entry:  {} {} ({})\n".format(ssid, id2ss[ssid],
                                                              lem))
        else:
            log.write(u"Unknown AWN ID {} ({}).\n".format(ssid,
                                                          lem))
    for wf in lexent.iter('WordForm'):
        lem = ''
        typ = ''
        if wf.get('writtenForm'):
            lem = wf.get('writtenForm').strip()
        if wf.get('formType'):
            typ = wf.get('formType').strip().replace(' ', '')
            if lem and typ:
                if ssid in id2ss:
                    if (lem, id2ss[ssid], typ) not in known:
                        o.write("%s\t%s:%s:%s\t%s\n" % (id2ss[ssid], 
                                                        wnlang, 'lemma', typ,
                                                        lem))
                        known.add((lem, id2ss[ssid], typ))
                    else:
                        log.write(u"Duplicate entry:  {} {} ({} {})\n".format(ssid,id2ss[ssid],
                                                                         lem,
                                                                         typ))
                else:
                    log.write(u"Unknown AWN ID {} ({}).\n".format(ssid,
                                                                  lem))

sys.stderr.write('Writing XML\n')
for synset in root.iter('Synset'):
    ssid = synset.get('id').strip()
    if ssid in id2ss:
        class MonolingualExternalRefs(ET.ElementBase): pass
        class MonolingualExternalRef(ET.ElementBase): pass
        el = MonolingualExternalRefs(MonolingualExternalRef(externalSystem="PWN30", externalReference="{}".format(id2ss[ssid])))
        synset.append(el)

tree.write("arb2-lmf.xml", encoding="UTF-8", pretty_print=True,)

# <MonolingualExternalRefs>
# <MonolingualExternalRef externalSystem="Wordnet1.6" externalReference
# ="eng-16-01234567-n"/>
# <MonolingualExternalRef externalSystem="SUMO" externalReference
# ="superficialPart" relType="at"/>
# </MonolingualExternalRefs>

