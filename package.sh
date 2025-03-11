#!/bin/bash

###
### Create compressed archive packages of the built wordnets.
###
### Usage: package.sh [--publish] VERSION TAGNAME
###
### e.g.  package.sh 1.4 v1.4
###
###
### If the --publish option is used before the other two arguments,
### the packages will be uploaded to the GitHub release given by
### TAGNAME.
###
### The following environment variables may be set to use non-OMW sources:
###
###     BLDDIR - the location of the built WN-LMF packages
###     BASEURL - the URL prefix of the upload destination
###     WNBASE - the lexicon identifier prefix
###
### If these environment variables are unset, they default to:
###
###     BLDDIR="build/omw-${VER}"
###     BASEURL="https://github.com/omwn/omw-data/releases/download/${TAG}"
###     WNBASE="omw"


if [ "$1" == --publish ]; then
    shift
    publish=true
fi
if [ $# -ne 2 ]; then
    echo "usage: package.sh [--publish] VERSION TAGNAME"
    exit 1
fi

VER=$1
TAG=$2

# if unset, assign default values to BLDDIR and BASEURL
: "${BLDDIR:=build/omw-${VER}}"
: "${BASEURL:=https://github.com/omwn/omw-data/releases/download/${TAG}}"
: "${WNBASE:=omw}"

TAROPTS="--checkpoint=.100 -c -J"

if [ ! -d "$BLDDIR" ]; then
    echo "Build directory not found: $BLDDIR"
    exit 1
fi

upload() {
    if [ "$publish" = true ]; then
	echo "Uploading asset: $1"
        gh release upload "${TAG}" "$1"
    fi
}
xpath-get() { xmlstarlet sel -t -v "$1" "$2" 2>/dev/null; }

index() {
    cat <<EOF >> release/index.toml
[$1]
  label = "$2"
  language = "$3"
  license = "$4"

  [${1}.versions."$VER"]
    url = "${BASEURL}/${1}-${VER}.tar.xz"

EOF
}

mkdir -p release/
echo -n > release/index.toml

for pkg in "${BLDDIR}"/*; do
    name=$( basename $pkg )
    asset="release/${name}-${VER}.tar.xz"
    echo -n "$name"
    tar -C "${BLDDIR}" $TAROPTS -f "$asset" "$name"
    echo
    label=$( xpath-get '//Lexicon[1]/@label' "${BLDDIR}/${name}/${name}.xml" )
    lang=$( xpath-get '//Lexicon[1]/@language' "${BLDDIR}/${name}/${name}.xml" )
    license=$( xpath-get '//Lexicon[1]/@license' "${BLDDIR}/${name}/${name}.xml" )
    upload "${asset}#${label} [${lang}]"
    index "$name" "$label" "$lang" "$license"
done

echo -n "$WNBASE-$VER"
tar -C build/ $TAROPTS \
    --exclude="omw-en1*" --exclude="omw-en2*" --exclude="omw-en31" \
    -f "release/$WNBASE-${VER}.tar.xz" "$WNBASE-$VER"
echo
label="Open Multilingual Wordnet"
lang=mul
license="Please consult the LICENSE files included with the individual wordnets. Note that all permit redistribution."
upload "release/$WNBASE-${VER}.tar.xz#${label} [${lang}]"
index "$WNBASE" "$label" "$lang" "$license"

# also upload the index file we've built for the release
upload "./release/index.toml#index.toml"
