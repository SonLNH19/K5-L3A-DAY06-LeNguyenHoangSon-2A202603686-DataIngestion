"""Local MDX ingestion and controlled A/B/C retrieval experiment."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import chromadb
import onnxruntime
import tokenizers
from .ingestion import read_corpus
from .embeddings import embedder, MODEL_HASH
from .store import build, open_store, search
from .evaluation import evaluate_query, summarize

ROOT = Path(__file__).resolve().parents[2]
STARTER = ROOT / 'starter'
RESULTS = ROOT / 'results'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--split', choices=['none','dev','test'], default='none')
    parser.add_argument('--rebuild', action='store_true', help='delete and rebuild only day06-a and day06-b indexes')
    parser.add_argument('--select', action='store_true', help='select strategy from existing dev metrics before testing')
    args = parser.parse_args()
    documents = read_corpus()
    client = open_store(STARTER / '.chroma-lab')
    if args.rebuild:
        for name in ('day06-a','day06-b'):
            try:
                client.delete_collection(name)
            except Exception as exc:
                if type(exc).__name__ != 'NotFoundError':
                    raise
    questions_hash = hashlib.sha256((ROOT / 'benchmark/questions.json').read_bytes()).hexdigest()
    if args.split == 'test':
        choice_path = RESULTS / 'selected_strategy.json'
        if not choice_path.exists():
            raise RuntimeError('Choose a strategy using --select after running dev, before running test')
        choice = json.loads(choice_path.read_text(encoding='utf-8'))
        if choice['benchmark_sha256'] != questions_hash:
            raise RuntimeError('Benchmark changed since selection; test is not an independent holdout')
        if choice.get('review_status') != 'reviewed':
            raise RuntimeError('Dev evidence and equivalent passages must be manually reviewed before locking selection and running test')
    model = embedder()
    print('Embedding model: Chroma ONNX all-MiniLM-L6-v2, 384 dimensions', flush=True)
    a, a_stats = build(client, model, documents, 'A')
    b, b_stats = build(client, model, documents, 'B')
    if args.split == 'test' and choice['indexes'] != {'A':a_stats['fingerprint'], 'B':b_stats['fingerprint']}:
        raise RuntimeError('Indexes changed since dev selection; rerun dev and select again')
    report = {'time_utc':datetime.now(timezone.utc).isoformat(), 'model':'Chroma ONNX all-MiniLM-L6-v2',
        'model_archive_sha256':MODEL_HASH, 'dimensions':384, 'provider':'local CPU', 'python_version':sys.version.split()[0],
        'chroma_version':chromadb.__version__, 'onnxruntime_version':onnxruntime.__version__, 'tokenizers_version':tokenizers.__version__,
        'query_document_processing':'same ONNX tokenizer and mean pooling; L2 normalized; 256-token maximum',
        'metric':'cosine', 'search':'Chroma local HNSW approximate',
        'A':a_stats, 'B':b_stats, 'C':{**b_stats, 'note':'same index and chunks as B; filter only when supplied'}}
    stats_path = RESULTS / ('ingestion_stats_reload.json' if a_stats['embedded_chunks'] == 0 and b_stats['embedded_chunks'] == 0 else 'ingestion_stats.json')
    stats_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    if args.select:
        metrics = json.loads((RESULTS / 'metrics_dev_reviewed.json').read_text(encoding='utf-8'))
        context = json.loads((RESULTS / 'context_dev.json').read_text(encoding='utf-8'))
        if context != {'benchmark_sha256':questions_hash, 'A':a_stats['fingerprint'], 'B':b_stats['fingerprint']}:
            raise RuntimeError('Dev metrics do not match current benchmark/index; rerun dev')
        initial = json.loads((RESULTS / 'ingestion_stats.json').read_text(encoding='utf-8'))
        chosen = min(('A','B','C'), key=lambda s: (-metrics[s]['hit3'], -metrics[s]['hit1'], initial[s]['ingest_seconds'], s))
        (RESULTS / 'selected_strategy.json').write_text(json.dumps({'strategy':chosen,'review_status':'reviewed','review_method':'Codex AI assisted dev review; see audit files for student confirmation','benchmark_sha256':questions_hash,'indexes':{'A':a_stats['fingerprint'],'B':b_stats['fingerprint']},'rule':'dev hit3, hit1, ingest time, alphabetical','note':'See results/dev_evidence_review.csv and metrics_dev_reviewed.json.'}, indent=2), encoding='utf-8')
        print(f'Dev selection: {chosen}; see audit files for review and confirmation')
        return
    if args.split == 'none':
        print('Ingestion complete. Re-run without --rebuild to verify no duplicates.')
        return
    questions = json.loads((ROOT / 'benchmark/questions.json').read_text(encoding='utf-8'))
    traces = []
    for q in (q for q in questions if q['split'] == args.split):
        vector = model([q['question']])
        for strategy, collection in [('A',a), ('B',b), ('C',b)]:
            where = q['filter'] if strategy == 'C' and q['filter'] else None
            output = search(collection, vector, filters=where)
            hits = []
            for chunk_id, text, meta, distance in zip(output['ids'][0], output['documents'][0], output['metadatas'][0], output['distances'][0]):
                match = evaluate_query(q, text, meta)
                hits.append({'chunk_id':chunk_id, 'text':text, 'metadata':meta, 'cosine_similarity':1-float(distance), 'gold_evidence_match':match})
            traces.append({'strategy':strategy,'id':q['id'],'split':args.split,'question':q['question'],
                'filter':where,'gold_source_id':q['gold_source_id'],'gold_page':q['gold_page'],
                'evidence_quote':q['evidence_quote'],'hits':hits})
    (RESULTS / f'trace_{args.split}.json').write_text(json.dumps(traces, ensure_ascii=False, indent=2), encoding='utf-8')
    metrics = summarize(traces)
    (RESULTS / f'metrics_{args.split}.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    (RESULTS / f'context_{args.split}.json').write_text(json.dumps({'benchmark_sha256':questions_hash, 'A':a_stats['fingerprint'], 'B':b_stats['fingerprint']}, indent=2), encoding='utf-8')
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        RESULTS.mkdir(exist_ok=True)
        record = {'time_utc':datetime.now(timezone.utc).isoformat(), 'error_type':type(exc).__name__, 'message':str(exc)}
        with (RESULTS / 'pipeline_errors.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')
        raise
