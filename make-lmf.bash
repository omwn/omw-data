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
    xz -z -e "${RESDIR}/${lng}.tar"
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
echo Processing IWN  >&2

mkdir -p ${RESDIR}/iwn
tsv="$WNS/iwn/wn-data-ita.tab"
cp "$WNS/iwn/LICENSE" "${RESDIR}/iwn"
cp "$WNS/iwn/citation.bib"  "${RESDIR}/iwn"
python3 scripts/tsv2lmf.py iwn "it" scripts/ili-map.tab "$tsv" --version "1.0+omw" >  ${RESDIR}/iwn/iwn.xml
xmlstarlet -q validate -e --dtd scripts/WN-LMF.dtd  "${RESDIR}/iwn/iwn.xml"
tar -C "${RESDIR}" --exclude=citation.rst --exclude=*~ -cf  "${RESDIR}/iwn.tar"  "iwn"
xz -z -e "${RESDIR}/iwn.tar"

### pwn30 and pwn31
echo Processing PWN 3.0 and 3.1  >&2 

cp -rp "$WNS/pwn30" "${RESDIR}"
xz -d  "${RESDIR}/pwn30/wn30.xml.xz"
tar -C "${RESDIR}"  --exclude=*~ -cf  "${RESDIR}/pwn30.tar"  "pwn30"
xz -z -e "${RESDIR}/pwn30.tar"

cp -rp "$WNS/pwn31" "${RESDIR}"
xz -d  "${RESDIR}/pwn31/wn31.xml.xz"
tar -C "${RESDIR}"  --exclude=*~ -cf  "${RESDIR}/pwn31.tar"  "pwn31"
xz -z -e "${RESDIR}/pwn31.tar"

echo -e "pwn30\tPrinceton Wordnet 3.0" >> "$IDX"
echo -e "pwn31\tPrinceton Wordnet 3.1" >> "$IDX" 

cat <<EOT >> wn_config.py
config.add_project('pwn30', 'Princeton Wordnet 3.0', 'en')
config.add_project_version(
    'pwn30', '3.0',
    'somewhere
    'https://wordnet.princeton.edu/license-and-commercial-use',
)

config.add_project('pwn31', 'Princeton Wordnet 3.1', 'en')
config.add_project_version(
    'pwn31', '3.1',
    'somewere',
    'https://wordnet.princeton.edu/license-and-commercial-use',
)

EOT
