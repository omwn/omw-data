#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Extract synset-word pairs from the Princeton Wordnet
# Replace '_' with ' '

import nltk, codecs
from nltk.corpus import wordnet as w
#wndata="/home/bond/svn/wnja/tab/"
wnname = "Princeton WordNet" 
wnlang = "eng"
wnurl = "http://wordnet.princeton.edu/"
wnlicense = "wordnet"

#
# header
#
outfile = "wn-data-%s.tab" % wnlang
o = codecs.open(outfile, "w", "utf-8" )
log = codecs.open("log",  "w", "utf-8")

o.write("# %s\t%s\t%s\t%s \n" % (wnname, wnlang, wnurl, wnlicense))

for s in w.all_synsets():
    for l in s.lemmas:
        synset = "%08d-%s" % (s.offset, s.pos)
        if synset.endswith('s'):
            synset = synset[:-1] + 'a'
            log.write('Satellite changed to:\t%s\n' % synset)
        elif synset.endswith('a'):
            log.write('Focal adjective:\t%s\n' % synset)
        o.write("%s\tlemma\t%s\n" %  (synset, l.name.replace('_', ' ')))
