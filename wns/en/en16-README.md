# OMW English Wordnet based on WordNet 1.6

This is an export of the Princeton WordNet 1.6 into the WN-LMF
format. It is highly compatible with the original WordNet, but there
are some differences.

## Summary of Changes

* Redundant senses for the following have been suppressed:
  - *Andaman marble* (`09069710-n`)
  - *United States dollar* (`09837118-n`)
  - *Caucasian* (`02636794-a`), including the redundant sense relation
    to *Caucasus* (`06283823-n`)
  - *Masonic* (`02676217-a`)
  - *Serbian* (`02731460-a`)
  - *Siamese* (`02854550-a`)

* The 'verb group' relation (`$` pointer) is mapped to
  'similar'. These were merged in the WN-LMF format and are
  completely distinguishable by looking at the part-of-speech.

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

* NLTK-style synset identifiers (e.g., `entity.n.01`) are stored on
  the `dc:identifier` attribute on `<Synset>` elements.

* ILI identifiers from the [CILI][] project are stored on the `ili`
  attribute on `<Synset>` elements. In WN-LMF lexicons, this is the
  mechanism by which interlingual queries can be performed.

[CILI]: https://github.com/globalwordnet/cili/
