
# omw-data scripts

This directory contains scripts and related data for building, packaging, and
inspecting the OMW wordnets.

---

## OMW 1.0 tab format

Wordnet data is stored in tab-separated (`.tab`) files.  Each file describes
one wordnet in one language.

### Header line

The first non-blank line must be a comment containing four tab-separated
fields:

```
# name	lang	url	license
```

| Field     | Description |
|-----------|-------------|
| `name`    | Human-readable project name |
| `lang`    | ISO 639-3 language code (three letters) |
| `url`     | Project URL |
| `license` | Short license name (see recognised values below) |

### Data lines

Each subsequent line has the form:

```
offset-pos	lang:type	arg1	[arg2]	…
```

| Column | Description |
|--------|-------------|
| `offset-pos` | Princeton WordNet 3.0 synset identifier: 8-digit zero-padded offset followed by `-` and POS tag (`n`, `v`, `a`, `r`; `s` is treated as `a`) |
| `lang:type`  | Two-part field: the language code from the header followed by `:` and the record type (see below) |
| `arg1`, … | Type-specific arguments |

### Record types

#### `lemma` — lexical entry

```
offset-pos	lang:lemma	word	[variant1, variant2, …]
```

Adds `word` as a lemma for this synset.  The optional fourth column is a
comma-separated list of alternate written forms (e.g. morphological variants)
that are attached to the same lexical entry as plain `<Form>` elements.  A
given lemma may appear in multiple synsets; the entry is created once and
re-used.

Example:
```
00460735-a	kaw:lemma	ahĕniṅ	mahĕniṅ, ahniṅ
```

#### `lemma:root` — root form

```
offset-pos	lang:lemma:root	root_form
```

Must immediately follow the `lemma` line it belongs to (same synset, same
lemma).  Adds the root form as a `<Form>` tagged `form=root`.

#### `lemma:brokenplural` — broken plural

```
offset-pos	lang:lemma:brokenplural	plural_form
```

Same grouping requirement as `lemma:root`.  Tags the form `number=plural`.

#### `def` — definition

```
offset-pos	lang:def	sid	definition text
```

`sid` is a zero-based integer ordering definitions when a synset has more
than one.

#### `exe` — example sentence

```
offset-pos	lang:exe	sid	example text
```

`sid` is a zero-based integer ordering examples.

#### `pron` — pronunciation

```
offset-pos	lang:pron	lemma	text	[variety]	[audio]	[notation]
```

Must immediately follow the `lemma` line it belongs to.  `lemma` must match
the previous lemma exactly.

#### `count` — sense frequency count

```
offset-pos	lang:count	lemma	value
```

Must immediately follow the `lemma` line it belongs to.  `value` is a
non-negative integer.

### Lexical gap indicators

If a synset has no true lexical entry in the language, write the special
lemma `GAP!` or `PSEUDOGAP!`.  These are removed from the output and cause
the synset (and any remaining senses) to be marked `lexicalized="false"` in
the LMF.

### Recognised licenses

| Short name | URL |
|------------|-----|
| `CC BY 3.0` | https://creativecommons.org/licenses/by/3.0/ |
| `CC BY 4.0` | https://creativecommons.org/licenses/by/4.0/ |
| `CC BY SA 3.0` | https://creativecommons.org/licenses/by-sa/3.0/ |
| `CC BY SA 4.0` | https://creativecommons.org/licenses/by-sa/4.0/ |
| `MIT` | https://opensource.org/licenses/MIT/ |
| `Apache 2.0` | https://opensource.org/licenses/Apache-2.0 |
| `ODC-BY 1.0` | http://opendefinition.org/licenses/odc-by/ |
| `wordnet` | (Princeton WordNet licence) |

### Full example

```
# Wordnet Bahasa	ind	http://wn-msa.sourceforge.net/	MIT
00019613-n	ind:def	0	masalah fisik yang nyata
00019613-n	ind:lemma	inti
00019613-n	ind:lemma	unsur
11407591-n	ind:def	0	Novelis dan kritikus Perancis
11407591-n	ind:def	1	pembela Dreyfus
11407591-n	ind:lemma	Emile Zola
11407591-n	ind:lemma	Zola
```

With variant forms (Old Javanese extension):
```
# Old Javanese	kaw	https://github.com/davidmoeljadi/OJW	CC BY 4.0
00460735-a	kaw:lemma	ahĕniṅ	mahĕniṅ, ahniṅ
01905653-a	kaw:lemma	arĕsik	marĕsik, arsik
00166146-a	kaw:lemma	arūm	marūm
```

---

## tsv2lmf.py — convert OMW 1.0 TSV to WN-LMF

Converts a `.tab` file (format described above) to WN-LMF 1.4 XML.

```
python3 tsv2lmf.py SOURCE DESTINATION \
    --id=LEXID \
    --label='Human-readable name' \
    --language=LANG \
    --email=EMAIL \
    --license=LICENSE_URL \
    --version=VERSION \
    [--url=URL] \
    [--citation='...'] \
    [--requires=ID:VERSION] \
    [--ili-map=PATH] \
    [--log=PATH] \
    [--abort-on-errors]
```

`--requires` specifies a dependency on another lexicon (e.g. `omw-en:2.0`).
`--ili-map` is a two-column tab file mapping `offset-pos` to ILI identifiers
(e.g. `ili-map-pwn30.tab` from the CILI repository).

---

## sum-rel.py / summarize-release.py — summarise a release

`wn-core-ili.tab` in this directory contains the OMW 1.0 core synset list
(originally from WN 2.0 mapped to WN 3.0 via TALP; then mapped to ILI ids).

---

## wndb2lmf.py — convert a WNDB database to WN-LMF

Exports Princeton WordNet 3.0 or 3.1 WNDB data to WN-LMF XML.

```bash
pip install pe==0.2.0 wn==0.8.0

wget http://wordnetcode.princeton.edu/3.0/WordNet-3.0.tar.bz2
tar xf WordNet-3.0.tar.bz2

git clone https://github.com/globalwordnet/cili.git

python3 wndb2lmf.py \
    WordNet-3.0/dict/ \
    wn30.xml \
    --id=wn30 \
    --version='1.4+omw' \
    --label='The OMW English Wordnet based on the Princeton WordNet 3.0' \
    --language=en \
    --email=maintainer@example.com \
    --license=https://... \
    --ili-map=cili/ili-map-pwn30.tab
```
