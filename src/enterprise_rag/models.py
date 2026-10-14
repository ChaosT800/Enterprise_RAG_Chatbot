from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class Document:
    id: str
    name: str
    department: str
    allowed_roles: frozenset[str]


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    document_name: str
    page_number: int
    text: str


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float


@dataclass(frozen=True)
class Citation:
    document_name: str
    page_number: int
    excerpt: str


@dataclass(frozen=True)
class ChatResponse:
    answer: str
    citations: Sequence[Citation]


@dataclass(frozen=True)
class IngestionResult:
    document_name: str
    chunk_count: int

