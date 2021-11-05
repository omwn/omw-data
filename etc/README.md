# Auxiliary Files for OMW Data Conversion

This directory is for additional files necessary for converting or
analyzing the OMW data. Only files that are not trivial to retrieve
are included in the repository, while the others will be retrieved
when building the lexicons.

* **Included**:
- `wn-core-ili.tab` the core ~5000 concepts derived from the [Princeton WordNet's core word senses](https://wordnet.princeton.edu/download/standoff-files), used for analysis of the lexicons
* Retrieved from <https://github.com/globalwordnet/cili/>:
  - `cili/ili-map-pwn30.tab` for mapping WordNet 3.0 synsets to ILIs
  - `cili/ili-map-pwn31.tab` for mapping WordNet 3.1 synsets to ILIs
* Retrieved from <https://github.com/globalwordnet/schemas>:
  - `WN-LMF-1.1.dtd` for validating the generated XML files
* Retrieved from <http://wordnetcode.princeton.edu/>:
  - `WordNet-3.0` WNDB data files for creating the `wn30` lexicon
  - `WordNet-3.1` WNDB data files for creating the `wn31` lexicon
