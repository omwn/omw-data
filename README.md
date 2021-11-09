# omw-data

This packages up data for the Open Multilingual Wordnet.  It is roughly the version that is described in Bond and Foster (2013).

It includes the data in the original OMW 1.0 format, and in the packaged up in the [GWA format](https://github.com/globalwordnet/schemas/) for OMW 2 as a [release](https://github.com/omwn/omw-data/releases).

It can be used by the Python library [Wn](https://github.com/goodmami/wn).

The raw data (under *wns*) also has the automatically extracted data for over 150 languages from [Wiktionary](https://www.wiktionary.org/) and the Unicode [Common Locale Data Repository (CLDR)](https://cldr.unicode.org/).

## Citation

If you use OMW please cite both the citation below, and the individual wordnets (citation data is included in each wordnet):

Francis Bond and Ryan Foster (2013)
[Linking and extending an open multilingual wordnet](http://aclweb.org/anthology/P/P13/P13-1133.pdf)</a>.
In *51st Annual Meeting of the Association for Computational Linguistics:  ACL-2013*.
Sofia. 1352–1362


## Notes

The directory *wns* has the wordnet data from OMW 1.2 with some small fixes
 * added a citation for the Icelandic wordnet
 * added human readable citations in [index.toml](index.toml)

By default the label is the name of the project.  If the project has multiple wordnets, then the language is added in parentheses.  E.g.:

`label = "Multilingual Central Repository (Catalan)"`

The package name (and id) for each wordnet is, by default, `omw-lg`,
with the following exceptions:

 * ItalWordnet will be `omw-iwn` not `omw-it` (used by multiwordnet)
 * COW will just be `omw-cmn` not `omw-cmn-Hans`
 * WN derived from PWN 3.0 will be `omw-en`
 * WN derived from PWN 3.1 will be `omw-en31`

We thanks the developers of all of the wordnets!  More recent versions
are available for many of these.

Francis Bond and Ryan Foster (2013)
[Linking and extending an open multilingual wordnet](https://aclanthology.org/P13-1133/)</a>.
In *51st Annual Meeting of the Association for Computational Linguistics:  ACL-2013*.
Sofia. 1352–1362
