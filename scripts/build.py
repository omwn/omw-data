
from typing import Optional
from pathlib import Path
import argparse

import tomli

from . import tsv2lmf
from .util import load_ili_map

parser = argparse.ArgumentParser()
parser.add_argument('--version', required=True, help='the version to build')
parser.add_argument('--dry-run', action='store_true',
                    help='print what would be built without building')
parser.add_argument('LEXID', nargs='*',
                    help='which wordnet to build (default: all)')
args = parser.parse_args()

# The index must specify these on an entry or as a default.
REQUIRED_ATTRIBUTES = {
    'label',
    'language',
    'email',
    'license',
    'source',
}

# If the following filenames are present in the source directory, they
# will be copied into the LMF package.
LMF_PACKAGE_FILENAMES = [
    'README',  # 'README.txt', 'README.md', 'README.rst',
    'LICENSE',  # 'LICENSE.txt', 'LICENSE.md', 'LICENSE.rst',
    'citation.bib',
]

OMWDATA = Path(__file__).parent.parent
INDEXPATH = OMWDATA / 'index.toml'

ILIFILE = OMWDATA / 'etc' / 'cili' / 'ili-map-pwn30.tab'
ilimap = load_ili_map(ILIFILE)

BUILD = OMWDATA / 'build' / f'omw-{args.version}'
BUILD.mkdir(parents=True, exist_ok=True)

LOGDIR = OMWDATA / 'log'
LOGDIR.mkdir(exist_ok=True)

index = tomli.load(INDEXPATH.open('rb'))
defaults = index.get('package-defaults', {})
packages = index.get('packages', {})

LEXIDS = set(args.LEXID) or set(packages)
VERSION = args.version

for lexid, project in packages.items():
    if lexid not in LEXIDS or not isinstance(project, dict):
        continue

    packagedir = BUILD / lexid
    packagedir.mkdir(exist_ok=True)
    outfile = packagedir / f'{lexid}.xml'

    def get(key: str) -> Optional[str]:
        return project.get(key, defaults.get(key))

    if any(get(attr) is None for attr in REQUIRED_ATTRIBUTES):
        print(f'{lexid}: missing one or more required attributes '
              f'({" ".join(REQUIRED_ATTRIBUTES)})')
        continue
    print(f'{lexid}: converting')
    if not args.dry_run:
        with (LOGDIR / f'tsv2lmf_{lexid}-{VERSION}.log').open('w') as logfile:
            tsv2lmf.convert(
                project['source'],
                str(outfile),
                lexid,
                get('label'),
                get('language'),
                get('email'),
                get('license'),
                VERSION,
                url=get('url'),
                citation=get('citation'),
                logo=get('logo'),
                requires=get('requires'),
                ilimap=ilimap,
                logfile=logfile,
            )

    # copy extra files if available
    sourcedir = Path(project['source']).parent
    for filename in LMF_PACKAGE_FILENAMES:
        path = (sourcedir / filename)
        if path.is_file():
            (packagedir / filename).write_bytes(path.read_bytes())  # copy
