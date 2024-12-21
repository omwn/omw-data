

## Sense Index

WordNet 1.5 was the first release with a [Sense Index], but the file
is not distributed with the Windows [wn15.zip] package. It exists as a
separate download ([wn15si.zip]), but for the OMW version of the
lexicon, we recreate the sense index. The resulting sense index is
identical to the original except for two entries:

    create%2:36:16:: 00926188 5
    make%2:36:16:: 00952386 24

The `16` in these entries is the `lex_id` field, which originally is a
1-digit hexadecimal number with a maximum value of `15`, so this
appears to be due to some bug in the original WordNet code. The
entries we use instead are:

    create%2:36:00:: 00926188 5
    make%2:36:00:: 00952386 24

The `lex_id` of `00` follows the hexadecimal value of `0` from the
data files.

[Sense Index]: https://wordnet.princeton.edu/documentation/senseidx5wn
[wn15.zip]: https://wordnetcode.princeton.edu/1.5/wn15.zip
[wn15si.zip]: https://wordnetcode.princeton.edu/1.5/wn15si.zip
