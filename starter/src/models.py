"""Data contracts for source units and persisted chunks."""
from typing import TypedDict


class UnitMetadata(TypedDict):
    unit_id: str
    chapter: str
    path: str
    sha256: str


class ChunkMetadata(TypedDict):
    document_id: str
    source: str
    page: str
    chapter: str
    chunk_index: int


class Chunk(TypedDict):
    id: str
    text: str
    metadata: ChunkMetadata
