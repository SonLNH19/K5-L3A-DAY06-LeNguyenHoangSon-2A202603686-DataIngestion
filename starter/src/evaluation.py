"""Exact-evidence retrieval proxy; equivalent evidence requires human review."""
import re
import unicodedata


def comparable(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', text)).strip()


def evaluate_query(question, text, metadata):
    """Return whether one chunk contains the full recorded gold evidence."""
    return (metadata['document_id'] == question['gold_source_id']
            and metadata['page'] == question['gold_page']
            and comparable(question['evidence_quote']) in comparable(text))


def summarize(traces):
    """Count exact-evidence hits per strategy; never infer manual labels."""
    metrics = {}
    for strategy in ('A', 'B', 'C'):
        rows = [trace for trace in traces if trace['strategy'] == strategy]
        metrics[strategy] = {
            'n': len(rows),
            'hit1': sum(bool(row['hits']) and row['hits'][0]['gold_evidence_match'] for row in rows),
            'hit3': sum(any(hit['gold_evidence_match'] for hit in row['hits']) for row in rows),
        }
    return metrics
