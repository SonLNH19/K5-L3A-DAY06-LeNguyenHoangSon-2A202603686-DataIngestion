"""Verify corpus, benchmark evidence and stored trace provenance without changing them."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalize(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', text)).strip()


def main():
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8-sig'))
    units = {u['unit_id']: u for u in manifest['units']}
    if len(units) < 30:
        raise ValueError('Fewer than 30 unique source units')
    sources = {}
    for unit_id, unit in units.items():
        path = (ROOT / unit['path']).resolve()
        if not path.is_relative_to(ROOT / 'data/transformers-nlp'):
            raise ValueError(f'{unit_id}: path outside corpus directory')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != unit['sha256']:
            raise ValueError(f'{unit_id}: SHA-256 mismatch')
        sources[unit_id] = normalize(raw.decode('utf-8'))
    questions = json.loads((ROOT / 'benchmark/questions.json').read_text(encoding='utf-8'))
    if len(questions) < 20 or len({q['id'] for q in questions}) != len(questions):
        raise ValueError('Benchmark count or IDs invalid')
    for q in questions:
        if normalize(q['evidence_quote']) not in sources[q['gold_page']]:
            raise ValueError(f"{q['id']}: evidence absent")
    for split in ('dev', 'test'):
        traces = json.loads((ROOT / f'results/trace_{split}.json').read_text(encoding='utf-8'))
        expected = {q['id'] for q in questions if q['split'] == split}
        for strategy in 'ABC':
            rows = [t for t in traces if t['strategy'] == strategy]
            if len(rows) != len(expected) or {t['id'] for t in rows} != expected:
                raise ValueError(f'{split}/{strategy}: incomplete trace')
            for trace in rows:
                if len(trace['hits']) != 3:
                    raise ValueError(f"{trace['id']}: expected top-3")
                for hit in trace['hits']:
                    page = hit['metadata']['page']
                    unit = units[page]
                    if (hit['metadata']['source'] != unit['path'] or
                        hit['metadata']['chapter'] != unit['chapter'] or
                        hit['metadata']['document_id'] != manifest['source_id'] or
                        normalize(hit['text']) not in sources[page]):
                        raise ValueError(f"{trace['id']}: trace provenance mismatch")
    print(f"OK: {len(units)} source files and hashes; {len(questions)} evidence passages; dev/test top-3 trace provenance.")
    print('This check does not validate the correctness of the answers or human audit labels.')


if __name__ == '__main__':
    main()
