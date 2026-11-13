"""Create traceable fixed-size and paragraph-based chunks."""
import hashlib
import re
from .models import Chunk, UnitMetadata

SIZE, OVERLAP, B_SIZE = 500, 50, 900

def fixed(text, size=SIZE, overlap=OVERLAP):
    for start in range(0, len(text), size - overlap):
        piece = text[start:start + size].strip()
        if piece:
            yield piece
        if start + size >= len(text):
            break


def paragraphs(text):
    pending = ''
    for paragraph in re.split(r'\n\s*\n', text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) > B_SIZE:
            if pending:
                yield pending
                pending = ''
            yield from fixed(paragraph, B_SIZE, OVERLAP)
        elif pending and len(pending) + len(paragraph) + 2 > B_SIZE:
            yield pending
            pending = paragraph
        else:
            pending = f'{pending}\n\n{paragraph}'.strip()
    if pending:
        yield pending


def make_chunks(documents: list[tuple[UnitMetadata, str]], strategy: str) -> list[Chunk]:
    if strategy not in ('A', 'B'):
        raise ValueError('Index strategy must be A or B; C shares the B index')
    chunks: list[Chunk] = []
    for unit, text in documents:
        pieces = fixed(text) if strategy == 'A' else paragraphs(text)
        for index, piece in enumerate(pieces):
            chunk_id = hashlib.sha256(f'{strategy}|{unit["unit_id"]}|{index}|{piece}'.encode('utf-8')).hexdigest()
            chunks.append({'id': chunk_id, 'text': piece, 'metadata': {
                'document_id': 'huggingface_transformers_nlp', 'source': unit['path'],
                'page': unit['unit_id'], 'chapter': unit['chapter'], 'chunk_index': index}})
    return chunks


