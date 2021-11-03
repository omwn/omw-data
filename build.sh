#!/bin/bash

###
### Build the English Wordnets based on Princeton WordNet and the
### other OMW wordnets.
###
### WordNet 3.0 has a loop in the verb taxonomy that is patched here.
### The build wordnets should not be tracked by Git.
###

# Configuration ########################################################

VER=1.4  # local (OMW) version to use for the WN-LMF lexicon

BUILD="build/omw-${VER}"
DTD="WN-LMF-1.1.dtd"

WN30_LABEL="OMW English Wordnet based on WordNet 3.0"
WN31_LABEL="OMW English Wordnet based on WordNet 3.1"
WN_CITATION="Christiane Fellbaum (1998, ed.) *WordNet: An Electronic Lexical Database*. MIT Press."
WN_LICENSE="https://wordnet.princeton.edu/license-and-commercial-use"
WN_EMAIL="bond@ieee.org"

mkdir -p "${BUILD}"
mkdir -p etc


# Auxiliary Files ######################################################

echo "Checking auxiliary files in etc/"

if [ ! -d etc/cili ]; then
    git clone https://github.com/globalwordnet/cili.git etc/cili
fi

if [ ! -f etc/"${DTD}" ]; then
    wget "https://globalwordnet.github.io/schemas/${DTD}" -O etc/"$DTD"
fi


# WordNet 3.0: retrieve, unpack, patch, and build ######################

if [ ! -d etc/WordNet-3.0 ]; then
    wget http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.bz2 -O - | tar -C etc/ -xj
    # Patch a simple loop between inhibit and suppress. The original line,
    # abbreviated, has this:
    #   02423762 41 v 03 inhibit ... @ 02422663 v 0000 ... ~ 02422663 v 0000 ...
    sed -i '/^02423762 /{s/@ 02422663 /@ 00612841 /}' etc/WordNet-3.0/dict/data.verb
fi

## make the lexicon
mkdir -p "${BUILD}/omw-en30"
python -m scripts.wndb2lmf \
       etc/WordNet-3.0/dict/ \
       "${BUILD}/omw-en30/omw-en.xml" \
       --id='omw-en' \
       --version="${VER}" \
       --label="${WN30_LABEL}" \
       --language='en' \
       --email="${WN_EMAIL}" \
       --license="${WN_LICENSE}" \
       --citation="${WN_CITATION}" \
       --ili-map=etc/cili/ili-map-pwn30.tab


# WordNet 3.1: retrieve, unpack, and build #############################

if [ ! -d etc/WordNet-3.1 ]; then
    mkdir etc/WordNet-3.1  # WN3.1 is only distributed with the dict/ subdirectory
    wget http://wordnetcode.princeton.edu/wn3.1.dict.tar.gz -O - | tar -C etc/WordNet-3.1 -xz
fi

mkdir -p "${BUILD}/omw-en31"
python -m scripts.wndb2lmf \
       etc/WordNet-3.1/dict/ \
       "${BUILD}/omw-en31/omw-en31.xml" \
       --id='omw-en31' \
       --version="${VER}" \
       --label="${WN31_LABEL}" \
       --language='en' \
       --email="${WN_EMAIL}" \
       --license="${WN_LICENSE}" \
       --citation="${WN_CITATION}" \
       --ili-map=etc/cili/ili-map-pwn31.tab


# Other OMW Lexicons ###################################################

python -m scripts.build --version="${VER}"


# Validate #############################################################

find "${BUILD}" -name \*.xml | sort | xargs xmlstarlet val -d "etc/$DTD"
