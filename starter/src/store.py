"""Persistent Chroma collections with cosine search and idempotent ingestion."""
import hashlib
import statistics
import time
import chromadb
from .chunking import make_chunks
from .embeddings import MODEL_HASH


def open_store(path):
    return chromadb.PersistentClient(path=str(path))


def search(collection, vector, filters=None, top_k=3):
    return collection.query(query_embeddings=vector, n_results=top_k, where=filters, include=["documents", "metadatas", "distances"])


def build(client, model, documents, strategy):
    started = time.perf_counter()
    chunks = make_chunks(documents, strategy)
    fingerprint = hashlib.sha256(('v1|' + '|'.join(c['id'] for c in chunks) + '|' + MODEL_HASH).encode()).hexdigest()
    name = f'day06-{strategy.lower()}'
    try:
        collection = client.get_collection(name, embedding_function=None)
    except Exception as exc:
        if type(exc).__name__ != 'NotFoundError':
            raise
        collection = None
    if collection is not None and (collection.metadata or {}).get('fingerprint') != fingerprint:
        raise RuntimeError(f'{name}: index does not match corpus/config; explicitly rebuild with --rebuild')
    if collection is None:
        collection = client.create_collection(name, embedding_function=None, metadata={'hnsw:space':'cosine', 'fingerprint':fingerprint})
    expected = {c['id'] for c in chunks}
    present = set(collection.get(include=[])['ids'])
    if not present.issubset(expected):
        raise RuntimeError(f'{name}: unexpected old chunk IDs; use --rebuild')
    missing = [c for c in chunks if c['id'] not in present]
    for start in range(0, len(missing), 32):
        batch = missing[start:start + 32]
        vectors = model([c['text'] for c in batch])
        if len(vectors) != len(batch) or any(len(v) != 384 for v in vectors):
            raise RuntimeError('Embedding model returned an unexpected number of vectors or dimensions')
        collection.upsert(ids=[c['id'] for c in batch], embeddings=vectors,
                          documents=[c['text'] for c in batch], metadatas=[c['metadata'] for c in batch])
        print(f'{strategy}: embedded {min(start + 32, len(missing))}/{len(missing)}', flush=True)
    if collection.count() != len(chunks):
        raise RuntimeError('Index count does not match expected chunks')
    lengths = sorted(len(c['text']) for c in chunks)
    return collection, {'chunk_count':len(chunks), 'characters':sum(lengths), 'min_length':min(lengths),
        'median_length':statistics.median(lengths), 'max_length':max(lengths),
        'ingest_seconds':round(time.perf_counter() - started, 3), 'embedded_chunks':len(missing),
        'previously_present':len(present), 'cost_usd':0, 'fingerprint':fingerprint}


