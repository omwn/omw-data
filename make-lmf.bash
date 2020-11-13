##
## Convert the OMW 1.0 files into the format for OMW 2.0
##
##

OMWROOT="$( cd "$( dirname "$0" )"; echo "$PWD" )"
RESDIR="$OMWROOT/release"
WNS="$OMWROOT/wns"
IDX="$RESDIR/index.tsv"
CITATIONFILE="$WNS/omw-citations.tab"
mkdir -p log
mkdir -p "$RESDIR"



###
### All original wordnets forwhich we are sure about licenses
### Except English, which we do separately
###

### 3 letter language code to BCP 47
declare -A lngs=(\
		 ["als"]="als" \
			["arb"]="arb" \
			["bul"]="bg" \
			["cmn"]="zh" \
#			["qcn"]="zh_Hant" \
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
			["jpn"]="jp" \
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
cat <<EOT > wn_config.py
config.add_project('iwn', 'Italian Wordnet', 'it')
config.add_project_version(
    'iwn', '1.0+wn',
    'http://192.168.1.81/~bond/omw1.0/iwn.xml',
    'http://opendefinition.org/licenses/odc-by/',
)
EOT

echo -e "iwn\tItalian Wordnet" > "$IDX"

for lng in "${!lngs[@]}"
do
    echo Processing $lng \("${lngs[$lng]}"\) >&2 
    mkdir -p ${RESDIR}/${lng}
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
            cp "${WNS}/${prj}/${name}" "${RESDIR}/${lng}/"
        fi
    done
    
    grep -P "${lng}\t|${lng}," ${CITATIONFILE} | cut -f2 > ${RESDIR}/${lng}/citation.rst
    ### convert
    python3 scripts/tsv2lmf.py ${lng}wn "${lngs[$lng]}" scripts/ili-map.tab "$tsv" --version "1.0+omw" --citation="${RESDIR}/${lng}/citation.rst" >  "${RESDIR}/${lng}/${lng}wn.xml"
    ### validate
    xmlstarlet -q validate -e --dtd scripts/WN-LMF.dtd  ${RESDIR}/${lng}/${lng}wn.xml
    tar -C "${RESDIR}" --exclude=citation.rst --exclude=*~ -cf  "${RESDIR}/${lng}.tar"  "${lng}"
    xz -z "${RESDIR}/${lng}.tar"
    ###
    ### config files
    ###
    labelll=`grep "           label=" ${RESDIR}/${lng}/${lng}wn.xml`
    labell="${labelll#           label=\"}"
    label="${labell%\" }"
    licenseee=`grep "           license=" ${RESDIR}/${lng}/${lng}wn.xml`
    licensee="${licenseee#           license=\"}"
    license="${licensee%\" }"
    #echo $licenseee $licensee $license
    cat << EOT >>  wn_config.py
config.add_project('${lng}wn', '${label}',  '${lngs[$lng]}')
config.add_project_version(
    '${lng}wn', '1.0+wn',
    'http://somewhere/~bond/omw1.0/${lang}/${lng}.tar.xz',
    '${license}'
)

EOT
    echo -e "${lng}\t${label}" >> "$IDX" 
done	    

### Second Italian Wordnet
mkdir -p ${RESDIR}/iwn
tsv="$WNS/iwn/wn-data-ita.tab"
cp "$WNS/iwn/LICENSE" "${RESDIR}/iwn"
cp "$WNS/iwn/citation.bib"  "${RESDIR}/iwn"
python3 scripts/tsv2lmf.py iwn "it" scripts/ili-map.tab "$tsv" --version "1.0+omw" >  ${RESDIR}/iwn/iwn.xml
xmlstarlet -q validate -e --dtd scripts/WN-LMF.dtd  "${RESDIR}/iwn/iwn.xml"
tar -C "${RESDIR}" --exclude=citation.rst --exclude=*~ -cf  "${RESDIR}/iwn.tar"  "iwn"
xz -z "${RESDIR}/iwn.tar"
