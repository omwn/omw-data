# omw-data

This packages up data for the Open Multilingual Wordnet.  It is roughly the version that is described in Bond and Foster (2013).

It includes the data in the original OMW 1.0 format, and in the packaged up in the [GWA format](https://github.com/globalwordnet/schemas/) for OMW 2 as a [release](https://github.com/bond-lab/omw-data/releases).

It can be used by the Python library [wn](https://github.com/goodmami/wn).

The raw data (under *wns*) also has the automatically extracted data
for over 150 languages from Wiktionary and the ‎Unicode Common Locale
Data Repository.


The directory *wns* has the wordnet data from OMW 1.2 with some small fixes
 * added a citation for the Icelandic wordnet
 * added human readable citations in ``omw-citations.tab``
 * added PWN 3.0 and 3.1 in OMW 2.0 format

By defualt the label is the name of the project.  If the project has multiple wordents, then the language is added in parantheses.  E.g.:

label = "Multilingual Central Repository (Catalan)"


If you use OMW please cite both the citation below, and the individual wordnets (citation data is included in each wordnet):

Francis Bond and Ryan Foster (2013)
[Linking and extending an open multilingual wordnet](http://aclweb.org/anthology/P/P13/P13-1133.pdf)</a>.
In *51st Annual Meeting of the Association for Computational Linguistics:  ACL-2013*.
Sofia. 1352–1362
      
