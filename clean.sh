#!/bin/bash

### Remove duplicate entries, strip quotes, etc. in TSV files

clean() {
    python -m scripts.clean-tsv --in-place "$1" 2>"$2"
}

LGS=(
  als
  arb
  bul
  cow
  cwn
  dan
  ell
  eng
  fas
  fin
  fra
  heb
  hrv
  isl
  ita
  iwn
  jpn
  mcr
  msa
  nld
  nor
  pol
  por
  ron
  slk
  slv
  swe
  tha
)

for lg in ${LGS[*]}; do
    echo "Cleaning ${lg}" >&2
    tab="wns/${lg}/wn-data-${lg}.tab"
    err="wns/${lg}/changes.tab"
    clean "$tab" "$err"
done
