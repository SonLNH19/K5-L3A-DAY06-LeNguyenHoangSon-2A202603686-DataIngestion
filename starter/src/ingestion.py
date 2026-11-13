"""Read and validate the MDX corpus; normalize Unicode and log errors."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"

def normalize(text):
    text = unicodedata.normalize('NFC', text.replace('\r\n', '\n').replace('\r', '\n'))
    return '\n'.join(re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')).strip()


def read_corpus():
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8-sig'))
    documents, errors = [], []
    for unit in manifest['units']:
        try:
            path = ROOT / unit['path']
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != unit['sha256']:
                raise ValueError('SHA-256 differs from manifest')
            text = normalize(raw.decode('utf-8'))
            if not text:
                raise ValueError('empty after normalization')
            if unit['unit_id'].split('/')[0] != unit['chapter'] or f"/{unit['chapter']}/" not in unit['path']:
                raise ValueError('chapter metadata does not match source path')
            documents.append((unit, text))
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append({'unit_id': unit['unit_id'], 'error': str(exc)})
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / 'ingestion_errors.json').write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding='utf-8')
    if errors or len(documents) < 30:
        raise RuntimeError(f'Corpus incomplete: {len(documents)} units, {len(errors)} errors; see results/ingestion_errors.json')
    return documents


