#!/usr/share/python
# -*- encoding: utf-8 -*-
import sys
import codecs
#import re, collections
import xml.etree.cElementTree as ET

wndata = "data/"
wnname = "sloWNet" 
wnlang = "slv"
wnurl = "http://lojze.lugos.si/darja/slownet.html"
wnlicense = "CC BY SA 3.0"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )
log = codecs.open("log", "w", "utf-8" )

o.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))


# Data is in the file  slownet-2014-04-02.xml
#
#
sys.stderr.write('Reading XML\n')
tree = ET.parse(wndata + 'slownet-2014-04-02.xml')
root = tree.getroot()

#print root.tag

for synset in root.iter('SYNSET'):
    sid = synset.find('ID').text
    if sid.startswith('eng-30-'):
        ### wierd debvisidc issue
        ss = sid[7:].replace('-b', '-r')
        ## surely there must be a better way to deal with xml:
        lems = []
        for lit in synset.findall("SYNONYM[@{http://www.w3.org/XML/1998/namespace}lang='slv']/LITERAL"):
            if lit.text not in lems:
                lems.append(lit.text)
            else:
                 log.write("Duplicated lemma: %s (%s)\n" % (lit.text, sid))
        for lem in lems:
            o.write("%s\t%s:%s\t%s\n" % (ss, wnlang, 'lemma', lem))

        es = []
        for exe in synset.findall("USAGE[@{http://www.w3.org/XML/1998/namespace}lang='slv']"):
            if exe.text not in es:
                es.append(exe.text)
            else:
                 log.write("Duplicated example: %s (%s)\n" % (exe.text, sid))
        for i, e in enumerate(es):
            o.write("%s\t%s:%s\t%d\t%s\n" % (ss, wnlang, 'exe', i, e))

        ds = []        
        for dff in synset.findall("DEF[@{http://www.w3.org/XML/1998/namespace}lang='slv']"):
            if dff.text not in ds:
                ds.append(dff.text)
            else:
                 log.write("Duplicated definition: %s (%s)\n" % (dff.text, sid))
        for i, d in enumerate(ds):
            o.write("%s\t%s:%s\t%d\t%s\n" % (ss, wnlang, 'def', i, d))
    else:
        log.write("Unknown synset: %s\n" % sid)


sys.stderr.write('All Done\n')
