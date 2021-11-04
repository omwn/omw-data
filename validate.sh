#!/bin/bash

###
### Validate wordnets built by build.sh.
###

if [ $# -ne 1 ]; then
    echo "usage: validate.sh VERSION"
    exit 1
fi

VER=$1
BUILD="build/omw-${VER}"

if [ ! -d "$BUILD" ]; then
    echo "Build directory not found: $BUILD"
    exit 1
fi

DTD="WN-LMF-1.1.dtd"
mkdir -p etc
if [ ! -f etc/"${DTD}" ]; then
    wget "https://globalwordnet.github.io/schemas/${DTD}" -O etc/"$DTD"
fi

for xmlfile in $( find "$BUILD" -name \*.xml | sort ); do
    xmlstarlet val -d etc/"$DTD" "$xmlfile"
    # python3 -m wn validate "$xmlfile"  # from Wn 0.9.0
done
