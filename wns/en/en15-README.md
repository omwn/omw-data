# OMW English Wordnet based on WordNet 1.5

This is an export of the Princeton WordNet 1.5 into the WN-LMF
format. It is highly compatible with the original WordNet, but there
are some differences.

## Summary of Changes

* Redundant senses for the following have been suppressed:
  - *Andaman marble* (`07704901-n`)
  - *Siamese* (`02219260-a`)

* A `pertainym` relation on *animatedly* (`00175161-r`) is corrected
  to target a sense instead of a synset. This patch is required to
  ensure the WN-LMF file is valid.

* Multiword entries use ' ' as a word separator rather than '_'.

* Glosses are split into definitions and examples as WN-LMF encodes
  them as separate XML elements. This splitting process is
  sophisticated but imprecise, so there are some less-than-ideal
  definitions and examples.

* Information on adjective position is stored in the `adjposition`
  attribute instead of as part of the lemma: `a`, `p`, and `ip`

* Exceptional forms are only stored for words present in the
  lexicon. This should only affect the lemmatization of words not
  included in WordNet.

* The *lex_id* field used in WordNet's data files is not encoded
  directly. This field was used internally for constructing
  *sense_key* identifiers. In the WN-LMF lexicon, sense keys are
  stored on the `dc:identifier` attribute on `<Sense>` elements.

* Two sense keys in the distributed sense index appear to be
  incongruous with the database: `create%2:36:16::` and
  `make%2:36:16::`. The `16` is the *lex_id*, but in the data files
  this field is expressed with a single hexadecimal digit (i.e., with
  a maximum value of `f`, or `15` in decimal), which for these senses
  is given as `0`. WordNet 1.5 is the only version of the lexicon with
  this issue.

* NLTK-style synset identifiers (e.g., `entity.n.01`) are stored on
  the `dc:identifier` attribute on `<Synset>` elements.

* ILI identifiers from the [CILI][] project are stored on the `ili`
  attribute on `<Synset>` elements. In WN-LMF lexicons, this is the
  mechanism by which interlingual queries can be performed.

[CILI]: https://github.com/globalwordnet/cili/
