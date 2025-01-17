# Details of Converting WNDB to WN-LMF

## Definitions and Examples

In the original [WNDB] data, an entry contains one gloss delimited
from the rest of the entry by a pipe `|` character. WordNet's
documentation suggests that the gloss may contain an optional
definition followed by zero or more examples, but not neither. There
is no prescribed encoding for delimiting definitions from examples, so
all we have is convention. Here are some glosses that follow the
convention:

Single definition:
```
any living entity
```

Single definition with one or more examples:
```
technical aspects of doing something; "mechanisms of communication"; "the mechanics of prose style"
```

Examples with no definition:
```
"it signalled the ushering in of a new era"
```

By convention, definitions are unquoted and examples are quoted and
both are delimited with semicolons. Plenty of glosses defy this
convention, however:

Multiple definitions:
```
something having concrete existence; living or nonliving
```

Non-semicolon delimiters:
```
a notable achievement: "the book was her finest effort"
"dogs, foxes, and the like", "we don't want the likes of you around here"
```

Quoted dialogue:
```
"Oh, well," he shrugged diffidently, "I like the work."
```

Quotes in the definition:
```
These interpretations are called "schemas," or more pedantically, "schemata".
```

There are more variations than those listed here. We use a grammar to
try and account for the basic convention and several common
variations. Multiple definitions are grouped into one, but multiple
examples will be split when possible. It is not feasible to
automatically identify the ideal splits every time, so expect some
inaccuracies.

[WNDB]: https://wordnet.princeton.edu/documentation/wndb5wn

## Sense Index

WordNet 1.5 was the first release with a [Sense Index], but the file
is not distributed with the Windows [wn15.zip] package. It exists as a
separate download ([wn15si.zip]). For WordNet 1.6 and later, the
`index.sense` file is included in the database.

We also wrote a script to rebuild the sense index files (see
`scripts/build_senseidx.py`). We do not use the rebuilt files during
conversion, but the effort revealed some issues with the official
sense index files. In WordNets 1.5 and 1.6, the sense keys of
satellite adjectives may contain the adjpositional markers `(a)` or
`(p)` on the head word portion. Later versions of WordNet do not
include the markers on the sense keys, but they may persist in the
`cntlist` files. Tag counts are included in the sense index files from
WordNet 1.6, but the counts for sense keys with adjpositional markers
are sometimes `0`, perhaps caused by lookup errors with these
unconventional sense keys. For this reason, tag counts are taken from
the `cntlist` file instead of the `index.sense` file and a more robust
lookup method is used.

In WordNet 1.5, there is also an issue with the `lex_id` field for two
highly polysemous words: *create* and *make*. The entries in the
original sense index for these are:

    create%2:36:16:: 00926188 5
    make%2:36:16:: 00952386 24

The `16` in these entries is the `lex_id` field, which originally is a
1-digit hexadecimal number with a maximum value of `15`, so this
appears to be due to some bug in the original WordNet code. The
`lex_id` in the data files for these words are `0` (possibly a
roll-over from `f + 1`). This problem does not exist in WordNet 1.6 or
later.

[Sense Index]: https://wordnet.princeton.edu/documentation/senseidx5wn
[wn15.zip]: https://wordnetcode.princeton.edu/1.5/wn15.zip
[wn15si.zip]: https://wordnetcode.princeton.edu/1.5/wn15si.zip
