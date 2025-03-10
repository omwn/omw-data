# OMW English Wordnet based on WordNet 3.0

This is an export of the Princeton WordNet 3.0 into the WN-LMF
format. It is used as the taxonomic scaffolding for the other OMW
wordnets. It is highly compatible with the original WordNet, but there
are some differences:

## Summary of Changes

* It has a patch applied to stop a hyponym loop in *inhibit* (synset
  offset `02423762`) based on a patch from Ben Haskell
  <ben@clarity.princeton.edu>. This patch is also applied to the NLTK
  distribution of the WordNet data, so we think we are justified in
  applying it.

* Redundant `derivation` sense relations have been suppressed:
  - *strictness* (`04639371-n`) to *strict* (`02436995-s`)
  - *sombreness* (`04647478-n`) to *sombre* (`00365261-s`)
  - *somberness* (`04647478-n`) to *somber* (`00365261-s`)
  - *singularity* (`04763650-n`) to *singular* (`00494622-s`)
  - *repulsiveness* (`04781349-n`) to *repulsive* (`01625063-s`)
  - *benignancy* (`04840981-n`) to *benign* (`01372773-s`)
  - *dreariness* (`05206006-n`) to *dreary* (`00364881-s`)
  - *sombreness* (`07533257-n`) to *sombre* (`00365261-s`)
  - *somberness* (`07533257-n`) to *somber* (`00365261-s`)

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
