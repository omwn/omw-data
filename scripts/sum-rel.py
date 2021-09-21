### summarize the release
import wn
from tabulate import tabulate

wn.config.data_directory = '/tmp'
#wn.download('omw:1.3')


licenses = {'wordnet':'wordnet',
            'https://wordnet.princeton.edu/license-and-commercial-use':'wordnet',
            'http://opendefinition.org/licenses/odc-by/':'ODC-BY',
            'http://www.cecill.info/licenses/Licence_CeCILL-C_V1-en.html':'CeCILL-1.0',
            "https://creativecommons.org/publicdomain/zero/1.0/":'CC0-1.0',
            "https://creativecommons.org/licenses/by/":'CC-BY',
            "https://creativecommons.org/licenses/by-sa/":'CC-BY-SA',
            "https://creativecommons.org/licenses/by/3.0/":'CC-BY-3.0',
            "https://creativecommons.org/licenses/by-sa/3.0/":'CC-BY-SA 3.0',
            "https://creativecommons.org/licenses/by/4.0/":'CC-BY-4.0',
            "https://creativecommons.org/licenses/by-sa/4.0/":'CC-BY-SA 4.0',
            'https://opensource.org/licenses/MIT/':'MIT',
            'https://opensource.org/licenses/Apache-2.0':'Apache-2.0',
            'https://www.unicode.org/license.html':'unicode'}


core = []
for l in open('wn-core-ili.tab'):
    core.append(l.strip())
#print(core)

def link(text, url):
    return (f"<a href='{url}'>{text}</a>")

stats = list()
for l in wn.lexicons():
    ### Fixme  link for wordnet license
    incore = len([s for s in wn.synsets(lexicon=l.id) if s.ili and (s.ili.id in core)])
    synsets = len(wn.synsets(lexicon=l.id))
    data = f"""  <tr>
    <th>{l.specifier()}</th>
    <td>{l.language}</td>
    <td>{link(l.label, l.url)}</td>
    <td align='right'>{synsets:,d}</td>
    <td align='right'>{len(wn.senses(lexicon=l.id)):,d}</td>
    <td align='right'>{len(wn.words(lexicon=l.id)):,d}</td>
    <td align='right'>{incore/len(core):.1%}</td>
    <td>{link(licenses[l.license], l.license)}</td> 
    </tr>"""
    stats.append(data)

headers = "ID:ver Lang Label Synsets Senses Words Core License".split()

print("<table border>")
for r in stats:
    print (r)
print("</table>")
