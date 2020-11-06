#!/usr/share/python
# -*- encoding: utf-8 -*-
#
# Download the portuguese wordnet
# Clean it up a little
#
#import codecs
import urllib
wnlang = "por"
url  =  "https://github.com/arademaker/openWordnet-PT/raw/master/"

outfile = "wn-data-%s.tab" % wnlang

urllib.urlretrieve(url + 'openMLWN/' + outfile, filename=outfile)
urllib.urlretrieve(url + 'LICENSE', filename='LICENSE')
