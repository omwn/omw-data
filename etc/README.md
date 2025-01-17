# Auxiliary Files for OMW Data Conversion

This directory is for additional files necessary for converting or
analyzing the OMW data. Only files that are not trivial to retrieve
are included in the repository, while the others will be retrieved
when building the lexicons.

* **Included**:
- `wn-core-ili.tab` the core ~5000 concepts derived from the
  [Princeton WordNet's core word senses], used for analysis of the
  lexicons
* Retrieved from <https://github.com/globalwordnet/cili/> for mapping
  synsets to ILIs:
  - `cili/older-wn-mappings/ili-map-pwn15.tab`
  - `cili/older-wn-mappings/ili-map-pwn16.tab`
  - `cili/older-wn-mappings/ili-map-pwn17.tab`
  - `cili/older-wn-mappings/ili-map-pwn171.tab`
  - `cili/older-wn-mappings/ili-map-pwn20.tab`
  - `cili/older-wn-mappings/ili-map-pwn21.tab`
  - `cili/ili-map-pwn30.tab`
  - `cili/ili-map-pwn31.tab`
* Retrieved from <https://github.com/globalwordnet/schemas> for
  validating the generated XML files:
  - `WN-LMF-1.3.dtd`
* Retrieved from <http://wordnetcode.princeton.edu/> for creating
  WN-LMF lexicons from WNDB files:
  - `WordNet-1.5`
  - `WordNet-1.6`
  - `WordNet-1.7`
  - `WordNet-1.7.1`
  - `WordNet-2.0`
  - `WordNet-2.1`
  - `WordNet-3.0`
  - `WordNet-3.1`

[Princeton WordNet's core word senses]: https://wordnet.princeton.edu/download/standoff-files
