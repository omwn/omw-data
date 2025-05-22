#!/bin/bash

###
### Validate wordnets built by build.sh.
###
### Usage: validate.sh [BLDDIR]
###
### The BLDDIR argument is the directory of the built WN-LMF packages.
### If it is not given as an argument, a BLDDIR environment variable
### should be set instead. Arguments override environment variables.


: "${BLDDIR:=$1}"

if [ -z "$BLDDIR" ]; then
    echo "BLDDIR must be provided as an argument or environment variable."
    exit 1
fi

if [ ! -d "$BLDDIR" ]; then
    echo "Build directory not found: $BLDDIR"
    exit 1
fi

DTD="WN-LMF-1.3.dtd"
mkdir -p etc
if [ ! -f etc/"${DTD}" ]; then
    wget "https://globalwordnet.github.io/schemas/${DTD}" -O etc/"$DTD"
fi

for xmlfile in $( find "$BLDDIR" -name \*.xml | sort ); do
    xmlstarlet val -d etc/"$DTD" "$xmlfile"
    # python3 -m wn validate "$xmlfile"  # from Wn 0.9.0
done
