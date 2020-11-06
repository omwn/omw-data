import sys
import re

pos_to_int = {
        'n' : 1,
        'v' : 2,
        'a' : 3,
        'r' : 4,
        's' : 5,
        'p' : 6
        }

pos_to_int2 = {
        'n' : 1,
        'v' : 2,
        'a' : 3,
        'r' : 4,
        's' : 3,
        'p' : 4
        }

sats = dict()

for file in (sys.argv[1] + "data.noun", sys.argv[1] + "data.verb", sys.argv[1] + "data.adj", sys.argv[1] + "data.adv"):
    if file.endswith(".adj"):
        for line in open(file):
            if not line.startswith(" "):
                elems = line.split(" ")
                if elems[2] == 'a':
                    synsetid = elems[0]
                    nWords = int(elems[3],16)
                    sats[synsetid] = (re.sub('\(i?[nvarsp]\)$','',elems[4]), "%02x" % int(elems[5], 16))

    for line in open(file):
        if not line.startswith(" "):
            elems = line.split(" ")
            synsetid = elems[0]
            lexNo = elems[1]
            posChar = elems[2]
            nWords = int(elems[3],16)
            for i in range(0, nWords):
                lemma = re.sub('\(i?[nvarsp]\)$','',elems[4 + 2 * i])
                lexId = int(elems[5 + 2 * i],16)
                if posChar == 's':
                    head_synsetid = elems[elems.index('&')+1]
                    head_word, head_id = sats[head_synsetid]
                else:
                    head_word, head_id = "", "" 
                print("%s-%s %s%%%s:%s:%02d:%s:%s" % (synsetid, posChar, lemma.lower(), pos_to_int[posChar], lexNo, lexId, head_word, head_id))
