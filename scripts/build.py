
from typing import Optional
from pathlib import Path
import argparse

import tomli

from . import tsv2lmf

parser = argparse.ArgumentParser()
parser.add_argument('--version', required=True, help='the version to build')
parser.add_argument('--dry-run', action='store_true',
                    help='print what would be built without building')
parser.add_argument('LEXID', nargs='*',
                    help='which wordnet to build (default: all)')
args = parser.parse_args()

REQUIRED_ATTRIBUTES = {
    'label',
    'language',
    'email',
    'license',
    'source',
}

OMWDATA = Path(__file__).parent.parent
INDEXPATH = OMWDATA / 'index.toml'
BUILD = OMWDATA / 'build' / f'omw-{args.version}'

BUILD.mkdir(parents=True, exist_ok=True)

index = tomli.load(INDEXPATH.open('rb'))
defaults = index.get('package-defaults', {})
packages = index.get('packages', {})

LEXIDS = set(args.LEXID) or set(packages)

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
        tsv2lmf.convert(
            project['source'],
            str(outfile),
            lexid,
            get('label'),
            get('language'),
            get('email'),
            get('license'),
            args.version,
            url=get('url'),
            citation=get('citation'),
            logo=get('logo'),
            requires=get('requires'),
        )
