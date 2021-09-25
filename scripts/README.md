
# omw-data scripts

This directory contains scripts and some related data for the
building, packaging, and inspection of the OMW wordnets.

## sum-rel.py -- Summarize a release

* `wn-core-ili.tab` is made by converting the original list of core
  synsets from wn2.0 to wn3.0 using the mapppings from TALP (which
  loses 40 synsets), and then mapping to ili ids.  It is the same set
  of synsets used in OMW 1.0 to show core.

## tsv2lmf.py -- Create a WN-LMF file from OMW 1.0 TSV files

Usage: `python3 tsv2lmf.py WNID LANG ILIMAP TSVFILE [--version=VER] [--citation=...]`

## wndb2lmf.py -- Create a WN-LMF file from a WNDB database

This script exports the data from a WNDB database into a WN-LMF
file. It is intended to be used with the WordNet 3.0 and 3.1 data. To
use it, first install some requirements:

```console
$ pip install pe==0.2.0 wn=0.8.0
```

Then download the [Princeton WordNet
data](https://wordnet.princeton.edu/download/current-version) and
[CILI](https://github.com/globalwordnet/cili/) data. Note that for 3.0
you should *not* just get the "database files" as it doesn't have the
`*.exc` (exception lists) or `verb.Framestext` files.

* WordNet 3.0

  ```console
  $ wget http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.bz2
  $ tar xf WordNet-3.0.tar.bz2
  ```

* WordNet 3.1

  ```console
  $ wget http://wordnetcode.princeton.edu/wn3.1.dict.tar.gz
  $ mkdir -p WordNet-3.1 && tar x -C WordNet-3.1 -f wn3.1.dict.tar.gz
  ```

* CILI

  ```console
  $ git clone https://github.com/globalwordnet/cili.git
  ```

Then run the script as follows (for example):

```console
$ python scripts/wndb2lmf.py \
         WordNet-3.0/dict/ \
         wn30.xml \
         --id='wn30' \
         --version='1.4+omw' \
         --label='The OMW English Wordnet based on the Princeton WordNet 3.0' \
         --language='en' \
         --email='maintainer@example.com' \
         --license='https://...' \
         --ili-map=cili/ili-map-pwn30.tab
```
