#!/bin/bash

### Script to convert the Princeton WordNet to WN-LMF

# Configuration ########################################################

if [ $# -ne 2 ]; then
    echo "usage: build-en.sh OMWVERSION WNVERSION"
    echo "  OMWVERSION: Version of the OMW release (e.g., 2.0)"
    echo "  WNVERSION: Version of the Princeton WordNet (e.g., 3.0)"
    exit 1
fi

OMWVER="$1"
VER="$2"

SHORTVER=$( sed 's/\.//g' <<< "$VER" )

WN="WordNet-${VER}"
LGVER="en${SHORTVER}"

TMPDIR="etc/"
CILIDIR="${TMPDIR}/cili"
METADIR="wns/en/"
BLDDIR="build/omw-${OMWVER}"

WNID="omw-${LGVER}"
WNDIR="${TMPDIR}/${WN}"
LABEL="OMW English Wordnet based on ${WN}"
EMAIL='bond@ieee.org'
URL='https://github.com/omwn/omw-data'

MILLER95='George A. Miller (1995). WordNet: A Lexical Database for English. Communications of the ACM Vol. 38, No. 11: 39-41.'
FELLBAUM98='Christiane Fellbaum (1998, ed.) *WordNet: An Electronic Lexical Database*. MIT Press.'

# Most common defaults
BIBFILE="fellbaum-1998.bib"
CITATION="${FELLBAUM98}"
LICENSE="https://wordnetcode.princeton.edu/${VER}/LICENSE"
ILIMAP="${CILIDIR}/older-wn-mappings/ili-map-pwn${SHORTVER}.tab"


# Data Preparation #####################################################

# Ensure CILI mapping are available
if [ ! -d "${CILIDIR}" ]; then
    git clone https://github.com/globalwordnet/cili.git "${CILIDIR}"
fi

# Version-specific configuration
if [ "$VER" = "1.5" ]; then
    BIBFILE="miller-1995.bib"
    CITATION="${MILLER95}"
    LICENSE="${WN} License"
    if [ ! -d "${WNDIR}" ]; then
        wget -P "${TMPDIR}" https://wordnetcode.princeton.edu/1.5/wn15.zip
        wget -P "${TMPDIR}" https://wordnetcode.princeton.edu/1.5/wn15si.zip
        unzip "${TMPDIR}/wn15.zip" -d "${WNDIR}"
        unzip "${TMPDIR}/wn15si.zip" "SENSE.IDX" -d "${WNDIR}"
        wget -O "${WNDIR}/README" https://wordnetcode.princeton.edu/1.5/README
        # Need to rename files to be compatible with scripts
        mv "${WNDIR}/DICT" "${WNDIR}/dict"
        mv "${WNDIR}/SENSE.IDX" "${WNDIR}/dict/index.sense"
        pushd "${WNDIR}/dict"
        for POS in ADJ ADV NOUN VERB; do
            pos=$( tr A-Z a-z <<< "${POS}" )
            mv "${POS}.DAT" "data.${pos}"
            mv "${POS}.IDX" "index.${pos}"
            mv "${POS}.EXC" "${pos}.exc"
        done
        mv "CNTLIST" "cntlist"
        popd
        # Patch a relation issue on 'animatedly'. The original line,
        # abbreviated, has this:
        #   00175161 02 r 01 animatedly 0 001 \ 00600880 a 0000 | ...
        sed -i '/^00175161 /{s/\\ 00600880 a 0000 /\\ 00600880 a 0102 /}' \
            "${WNDIR}/dict/data.adv"
        # The above issue is fixed from WN 1.7.1, but it would cause a
        # validation error in the WN-LMF XML, so we fix it here.

        # # Rebuild the sense index
        # python -m scripts.build_senseidx \
        #    --use-adjposition \
        #    "${WNDIR}/dict" \
        #    -o "${WNDIR}/dict/index.sense"
        cp "${METADIR}/en15-LICENSE" "${WNDIR}/LICENSE"
    fi

elif [ "$VER" = "1.6" ]; then
    BIBFILE="miller-1995.bib"
    CITATION="${MILLER95}"
    LICENSE="${WN} License"
    if [ ! -d "${WNDIR}" ]; then
        pushd "${TMPDIR}"
        wget https://wordnetcode.princeton.edu/1.6/wn16.unix.tar.gz
        tar xf wn16.unix.tar.gz
        mv wordnet-1.6 WordNet-1.6  # rename for consistency
        chmod -R u+w WordNet-1.6  # cannot delete files otherwise
        popd
        # Patch a relation issue on 'animatedly'. The original line,
        # abbreviated, has this:
        #   00258752 02 r 01 animatedly 0 001 \ 00121842 a 0000 | ...
        sed -i '/^00258752 /{s/\\ 00121842 a 0000 /\\ 00121842 a 0101 /}' \
            "${WNDIR}/dict/data.adv"
        # The above issue is fixed from WN 1.7.1, but it would cause a
        # validation error in the WN-LMF XML, so we fix it here.
    fi

elif [ "$VER" = "1.7" ]; then
    if [ ! -d "${WNDIR}" ]; then
        pushd "${TMPDIR}"
        wget https://wordnetcode.princeton.edu/1.7/wn17.unix.tar.gz
        # WordNet-1.7 doesn't tar the directory, so create it first
        mkdir -p "${WN}" && tar -C "${WN}" -xf wn17.unix.tar.gz
        chmod -R u+w WordNet-1.7  # cannot delete files otherwise
        popd
        # Patch a relation issue on 'animatedly'. The original line,
        # abbreviated, has this:
        #   00260778 02 r 01 animatedly 0 001 \ 00123463 a 0000 | ...
        sed -i '/^00260778 /{s/\\ 00123463 a 0000 /\\ 00123463 a 0101 /}' \
            "${WNDIR}/dict/data.adv"
        # The above issue is fixed from WN 1.7.1, but it would cause a
        # validation error in the WN-LMF XML, so we fix it here.
    fi

elif [ "$VER" = "1.7.1" ]; then
    if [ ! -d "${WNDIR}" ]; then
        pushd "${TMPDIR}"
        wget https://wordnetcode.princeton.edu/1.7.1/WordNet-1.7.1.tar.gz
        tar -xf WordNet-1.7.1.tar.gz
        chmod -R u+w WordNet-1.7.1  # cannot delete files otherwise
        popd
    fi

elif [ "$VER" = "2.0" ]; then
    if [ ! -d "${WNDIR}" ]; then
        pushd "${TMPDIR}"
        wget https://wordnetcode.princeton.edu/2.0/WordNet-2.0.tar.gz
        tar -xf WordNet-2.0.tar.gz
        chmod -R u+w WordNet-2.0  # cannot delete files otherwise
        popd
    fi

elif [ "$VER" = "2.1" ]; then
    if [ ! -d "${WNDIR}" ]; then
        pushd "${TMPDIR}"
        wget https://wordnetcode.princeton.edu/2.1/WordNet-2.1.tar.gz
        tar -xf WordNet-2.1.tar.gz
        chmod -R u+w WordNet-2.1  # cannot delete files otherwise
        # LICENSE file is missing, but COPYING is the same thing
        cp WordNet-2.1/COPYING WordNet-2.1/LICENSE
        popd
    fi

elif [ "$VER" = "3.0" ]; then
    WNID="omw-en"  # override omw-en30
    LICENSE="https://wordnet.princeton.edu/license-and-commercial-use"
    ILIMAP="${CILIDIR}/ili-map-pwn${SHORTVER}.tab"
    if [ ! -d "${WNDIR}" ]; then
        pushd "${TMPDIR}"
        wget http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.gz
        tar -xf WordNet-3.0.tar.gz
        chmod -R u+w WordNet-3.0  # cannot delete files otherwise
        # LICENSE file is missing, but COPYING is the same thing
        cp WordNet-3.0/COPYING WordNet-3.0/LICENSE
        # Patch a simple loop between inhibit and restrain. The original line,
        # abbreviated, has this:
        #   02423762 41 v 03 inhibit ... @ 02422663 v 0000 ... ~ 02422663 v 0000 ...
        sed -i '/^02423762 /{s/@ 02422663 /@ 00612841 /}' WordNet-3.0/dict/data.verb
        # NOTE: The above fix is also applied to the NLTK's distribution
        # of the Princeton WordNet 3.0, so there is precedent. Please
        # refrain from making any further changes to the data.
        popd
    fi

elif [ "$VER" = "3.1" ]; then
    LICENSE="https://wordnet.princeton.edu/license-and-commercial-use"
    ILIMAP="${CILIDIR}/ili-map-pwn${SHORTVER}.tab"
    if [ ! -d "${WNDIR}" ]; then
        pushd "${TMPDIR}"
        wget http://wordnetcode.princeton.edu/wn3.1.dict.tar.gz
        mkdir WordNet-3.1  # WN3.1 is only distributed with the dict/ subdirectory
        tar -C WordNet-3.1 -xf wn3.1.dict.tar.gz
        chmod -R u+w WordNet-3.0  # cannot delete files otherwise
        # NOTE: Do not make changes to the data unless necessary for a
        # well-formed and loadable WN-LMF document. Errors are meant to be
        # fixed in later versions.
        popd
        cp "${METADIR}/en31-LICENSE" "${WNDIR}/LICENSE"
    fi

else
    echo "Invalid WordNet version: $VER"
    exit 1

fi


# Build ################################################################

mkdir -p "${BLDDIR}"

## make the lexicon
mkdir -p "${BLDDIR}/${WNID}"
python -m scripts.wndb2lmf \
       "${WNDIR}/dict" \
       "${BLDDIR}/${WNID}/${WNID}.xml" \
       --id="${WNID}" \
       --version="${OMWVER}" \
       --label="${LABEL}" \
       --language='en' \
       --email="${EMAIL}" \
       --license="${LICENSE}" \
       --url="${URL}" \
       --citation="${CITATION}" \
       --ili-map="${ILIMAP}"

# below: cat instead of cp to reset permissions
cat "${WNDIR}/LICENSE" > "${BLDDIR}/${WNID}/LICENSE"
cat "${METADIR}/${LGVER}-README.md" > "${BLDDIR}/${WNID}/README.md"
cat "${METADIR}/fellbaum-1998.bib" > "${BLDDIR}/${WNID}/citation.bib"

# append original readme if available

if [ -f "${WNDIR}/README" ]; then

cat <<EOF >> "${BLDDIR}/${WNID}/README.md"

## Original README

The following is the text of the original \`README\` file that came with
WordNet ${VER}.

\`\`\`
$( cat "${WNDIR}/README" )
\`\`\`
EOF

fi
