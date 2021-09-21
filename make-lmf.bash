##
## Convert the OMW 1.0 files into the format for OMW 2.0
##
## make directories for them with their LICENSE, README and citation.bib
## tar these and compress with xz
##
## Also package up pwn30 and pwn31 in the same way.
##

if [ $# -ne 1 ]; then
    echo "usage: make-lmf.bash VERSION"
    exit 1
fi

VERSION="$1"
VER="${VERSION#[Vv]}"  # e.g., v1.3 -> 1.3
BASEURL="https://github.com/bond-lab/omw-data/releases/download/${VERSION}" # /xyz.tar.xz

XZOPTS=''  # '-e'  # options for xz beyond -z

OMWROOT="$( cd "$( dirname "$0" )"; echo "$PWD" )"
RESDIR="$OMWROOT/release"
OMWDIR="$RESDIR/omw"
WNS="$OMWROOT/wns"
IDX="$RESDIR/index.tsv"
CITATIONFILE="$WNS/omw-citations.tab"
mkdir -p log

mkdir -p "$OMWDIR"
cp "${WNS}/README" "${OMWDIR}/"
cp "${WNS}/citation.bib" "${OMWDIR}/"


###
### All original wordnets forwhich we are sure about licenses
### Except English, which we do separately
###

### 3 letter language code to BCP 47
declare -A lngs=(\
		 ["als"]="als" \
			["arb"]="arb" \
			["bul"]="bg" \
			["cmn"]="cmn-Hans" \
#			["qcn"]="cmn-Hant" \
			["dan"]="da" \
			["ell"]="el" \
#			["eng"]="en" \
#			["fas"]="fa" \
			["fin"]="fi" \
			["fra"]="fr" \
			["heb"]="he" \
			["hrv"]="hr" \
			["isl"]="is" \
			["ita"]="it" \
			["jpn"]="ja" \
			["cat"]="ca" \
			["eus"]="eu" \
			["glg"]="gl" \
			["spa"]="es" \
			["ind"]="id" \
			["zsm"]="zsm" \
			["nld"]="nl" \
			["nno"]="nn" \
			["nob"]="nb" \
			["pol"]="pl" \
			["por"]="pt" \
			["ron"]="ro" \
			["lit"]="lt" \
			["slk"]="sk" \
			["slv"]="sl" \
			["swe"]="sv" \
			["tha"]="th" \
)

#declare -A lngs=( ["als"]="als" )

### Also make a configuration file

# index takes 4 arguments: name label language license
index() {
    cat <<EOT >> index.toml

[$1]
  label = "$2"
  language = "$3"
  license = "$4"
EOT
}

# index-ver takes 3 arguments: name version basename
index-ver() {
    cat <<EOT >> index.toml
  [$1.versions."$2"]
    url = "${BASEURL}/$3.tar.xz"
EOT
}

echo -n > index.toml

index iwn "Italian Wordnet" "it" "http://opendefinition.org/licenses/odc-by/"
index-ver iwn "${VER}+omw" "iwn"

echo -e "iwn\tit\tItalian Wordnet" > "$IDX"

for lng in "${!lngs[@]}"
do
    echo Processing $lng \("${lngs[$lng]}"\) >&2
    mkdir -p "${OMWDIR}/${lng}"
    ### extract
    if [ $lng = 'lit' ]  ###
    then
	prj='slk'
    ### MCR
    elif [ $lng = 'cat' ] || [ $lng = 'eus' ] ||  [ $lng = 'spa' ] || [ $lng = 'glg' ]
    then
	prj="mcr"
    elif [ $lng = 'cmn' ]  ### COW
    then
	prj="cow"
    elif [ $lng = 'ind' ]  || [ $lng = 'zsm' ] ### MSA
    then
	prj="msa"
    elif [ $lng = 'nno' ]  || [ $lng = 'nob' ] ### NOR
    then
	prj="nor"
    else
	prj="${lng}"
    fi
    tsv="$WNS/${prj}/wn-data-${lng}.tab"

    ### copy miscellaneous files
    for name in LICENSE README citation.bib; do
        if [ -f "${WNS}/${prj}/${name}" ]; then
            cp "${WNS}/${prj}/${name}" "${OMWDIR}/${lng}/"
        fi
    done

    grep -P "${lng}\t|${lng}," ${CITATIONFILE} | cut -f2 > ${OMWDIR}/${lng}/citation.rst
    ### convert
    python3 scripts/tsv2lmf.py \
        "${lng}wn" \
        "${lngs[$lng]}" \
        scripts/ili-map.tab \
        "$tsv" \
        --version "${VER}+omw" \
        --citation="${OMWDIR}/${lng}/citation.rst" \
        >  "${OMWDIR}/${lng}/${lng}wn.xml"
    ### validate
    xmlstarlet -q validate -e --dtd scripts/WN-LMF.dtd  "${OMWDIR}/${lng}/${lng}wn.xml"
    tar -C "${OMWDIR}" --exclude=citation.rst --exclude=*~ -cf  "${RESDIR}/${lng}.tar" "${lng}"
    xz -z $XZOPTS "${RESDIR}/${lng}.tar"
    ###
    ### config files
    ###
    label=$( xmlstarlet sel -t -v '//Lexicon/@label' "${OMWDIR}/${lng}/${lng}wn.xml" 2>/dev/null )
    license=$( xmlstarlet sel -t -v '//Lexicon/@license' "${OMWDIR}/${lng}/${lng}wn.xml" 2>/dev/null )
    lgcode=$( xmlstarlet sel -t -v '//Lexicon/@language' "${OMWDIR}/${lng}/${lng}wn.xml" 2>/dev/null )
    #echo $licenseee $licensee $license
    index "${lng}wn" "${label}" "${lngs[$lng]}" "${license}"    
    index-ver "${lng}wn" "${VER}+omw" "${lng}"

    echo -e "${lng}\t${lgcode}\t${label}" >> "$IDX"
done

### Second Italian Wordnet
echo Processing IWN  >&2

mkdir -p ${OMWDIR}/iwn
tsv="$WNS/iwn/wn-data-ita.tab"
cp "$WNS/iwn/LICENSE" "${OMWDIR}/iwn"
cp "$WNS/iwn/citation.bib"  "${OMWDIR}/iwn"
grep -P "iwn\t" ${CITATIONFILE} | cut -f2 > ${OMWDIR}/iwn/citation.rst
python3 scripts/tsv2lmf.py \
    iwn \
    "it" \
    scripts/ili-map.tab \
    "$tsv" \
    --version \
    "${VER}+omw" \
    --citation="${OMWDIR}/iwn/citation.rst" \
    >  ${OMWDIR}/iwn/iwn.xml
xmlstarlet -q validate -e --dtd scripts/WN-LMF.dtd  "${OMWDIR}/iwn/iwn.xml"
tar -C "${OMWDIR}" --exclude=citation.rst --exclude=*~ -cf  "${RESDIR}/iwn.tar"  "iwn"
xz -z $XZOPTS "${RESDIR}/iwn.tar"

### pwn30 and pwn31
echo Processing PWN 3.0 and 3.1  >&2

cp -rp "$WNS/pwn30" "${RESDIR}"
xz -d  "${RESDIR}/pwn30/wn30.xml.xz"
tar -C "${RESDIR}"  --exclude=*~ -cf  "${RESDIR}/pwn30.tar"  "pwn30"
xz -z $XZOPTS "${RESDIR}/pwn30.tar"

cp -rp "$WNS/pwn31" "${RESDIR}"
xz -d  "${RESDIR}/pwn31/wn31.xml.xz"
tar -C "${RESDIR}"  --exclude=*~ -cf  "${RESDIR}/pwn31.tar"  "pwn31"
xz -z $XZOPTS "${RESDIR}/pwn31.tar"

echo -e "pwn30\ten\tPrinceton Wordnet 3.0" >> "$IDX"
echo -e "pwn31\ten\tPrinceton Wordnet 3.1" >> "$IDX"

index "pwn" "Princeton WordNet" "en" "https://wordnet.princeton.edu/license-and-commercial-use"
index-ver "pwn" "3.0" "pwn30"
index-ver "pwn" "3.1" "pwn31"

echo Processing OMW Collection >&2

tar -C "${RESDIR}" --exclude=*~ -cf "${RESDIR}/omw-${VER}.tar" "omw"
xz -z $XZOPTS "${RESDIR}/omw-${VER}.tar"
echo -e "omw-${VER}\tmul\tOpen Multilingual Wordnet ${VERSION}" >> "$IDX"

index "omw" "Open Multilingual Wordnet" "mul" "Please consult the LICENSE files included with the individual wordnets. Note that all permit redistribution."
index-ver "omw" "${VER}" "omw-${VER}"

echo Done >&2
