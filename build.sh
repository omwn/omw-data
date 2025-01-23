#!/bin/bash

###
### Build the English Wordnets based on Princeton WordNet and the
### other OMW wordnets.
###
### WordNet 3.0 has a loop in the verb taxonomy that is patched here.
### The build wordnets should not be tracked by Git.
###

# Configuration ########################################################

if [ $# -ne 1 ]; then
    echo "usage: build.sh OMWVERSION"
    echo "  OMWVERSION: Version of the OMW release (e.g., 1.5)"
    exit 1
fi

OMWVER="$1"

BUILD="build/omw-${OMWVER}"
mkdir -p "${BUILD}"

# Princeton WordNet ####################################################

./build-en.sh "$OMWVER" "1.5"
./build-en.sh "$OMWVER" "1.6"
./build-en.sh "$OMWVER" "1.7"
./build-en.sh "$OMWVER" "1.7.1"
./build-en.sh "$OMWVER" "2.0"
./build-en.sh "$OMWVER" "2.1"
./build-en.sh "$OMWVER" "3.0"
./build-en.sh "$OMWVER" "3.1"

# Other OMW Lexicons ###################################################

python -m scripts.build --version="${OMWVER}"
