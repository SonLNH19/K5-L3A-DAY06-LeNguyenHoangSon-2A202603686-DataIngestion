"""Fetch missing course files from the pinned commit; never overwrite existing files."""
import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8-sig'))
    commit = manifest['snapshot_commit']
    if len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('Invalid source commit')
    for unit in manifest['units']:
        path = (ROOT / unit['path']).resolve()
        if not path.is_relative_to(ROOT / 'data/transformers-nlp'):
            raise ValueError('File path outside corpus')
        if path.exists():
            content = path.read_bytes()
            action = 'existing'
        else:
            unit_id = unit['unit_id']
            if not re.fullmatch(r'chapter[0-9]+/[0-9]+[a-z]?', unit_id):
                raise ValueError('Invalid source unit ID')
            url = f'https://raw.githubusercontent.com/huggingface/course/{commit}/chapters/en/{unit_id}.mdx'
            with urlopen(Request(url, headers={'User-Agent': 'day06-corpus-verifier'}), timeout=60) as response:
                content = response.read()
            action = 'downloaded'
        if action == 'downloaded' and hashlib.sha256(content).hexdigest() != unit['sha256']:
            # The original snapshot was checked out on Windows with CRLF endings.
            # Accept this conversion only when it exactly reproduces the manifest hash.
            content = content.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
        if hashlib.sha256(content).hexdigest() != unit['sha256']:
            raise ValueError(f"{unit['unit_id']}: hash mismatch; file not overwritten")
        if action == 'downloaded':
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as handle:
                handle.write(content)
        print(f"{unit['unit_id']}: {action}, SHA-256 OK")


if __name__ == '__main__':
    main()
