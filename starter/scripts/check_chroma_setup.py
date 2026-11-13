"""Check MDX readability and persistent Chroma search; not the lab benchmark."""
import json
import sys
from pathlib import Path

import chromadb

root = Path(__file__).resolve().parents[2]
manifest = json.loads((root / 'data/manifest.json').read_text(encoding='utf-8-sig'))
for unit in manifest['units']:
    if not (root / unit['path']).read_text(encoding='utf-8').strip():
        raise ValueError(f"Empty source: {unit['unit_id']}")
print(f"Readable corpus: {len(manifest['units'])} files")

client = chromadb.PersistentClient(path=str(root / 'starter/.chroma-setup-check'))
name = 'setup-check-only'
if len(sys.argv) > 1 and sys.argv[1] == 'verify':
    collection = client.get_collection(name, embedding_function=None)
    result = collection.query(query_embeddings=[[1.0, 0.0]], n_results=1)
    filtered = collection.query(query_embeddings=[[1.0, 0.0]], n_results=1, where={'chapter': 'chapter2'})
    assert collection.count() == 2 and result['ids'] == [['one']] and filtered['ids'] == [['two']], (result, filtered)
    print(f'Chroma {chromadb.__version__}: persisted data, vector search, and metadata filter OK')
    client.delete_collection(name)
else:
    collection = client.get_or_create_collection(name, embedding_function=None, metadata={'hnsw:space': 'cosine'})
    collection.upsert(ids=['one', 'two'], embeddings=[[1.0, 0.0], [0.0, 1.0]], metadatas=[{'chapter': 'chapter1'}, {'chapter': 'chapter2'}])
    print('Setup test vectors written; rerun with argument verify in a new process.')
