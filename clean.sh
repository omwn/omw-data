#!/bin/bash

### Remove duplicate entries, strip quotes, etc. in TSV files

clean() {
    echo "Cleaning ${1} ${2}" >&2
    tab="wns/${1}/wn-data-${2:-$1}.tab"
    err="wns/${1}/${2:-$1}-changes.tab"
    python -m scripts.clean-tsv --in-place "$tab" 2>>"$err"
}

# clean DIR [LG]
#   If LG is omitted, DIR is used as the LG code

clean als
clean arb
clean bul
clean cow cmn
clean cwn qcn
clean dan
clean ell
clean eng
clean fas
clean fin
clean fra
clean heb
clean hrv
clean isl
clean ita
clean iwn ita
clean jpn
clean mcr cat
clean mcr eus
clean mcr glg
clean mcr spa
clean msa ind
clean msa zsm
clean nld
clean nor nno
clean nor nob
clean pol
clean por
clean ron
clean slk
clean slv
clean swe
clean tha

# don't make empty files
find wns/ -name "*-changes.tab" -empty -delete
