import uuid
from pathlib import Path
from typing import Iterable

from .answerer import Answerer
from .chunking import chunk_pages
from .embeddings import Embedder
from .ingestion import extract_pages
from .models import ChatResponse, Citation, Document, IngestionResult
from .retrieval import LocalVectorIndex
from .store import SQLiteStore


class EnterpriseRAGService:
    def __init__(self, store: SQLiteStore, index_path: Path, embedder: Embedder, answerer: Answerer) -> None:
        self.store = store
        self.index = LocalVectorIndex(index_path, embedder)
        self.answerer = answerer

    def ingest_file(self, path: Path, department: str, allowed_roles: Iterable[str]) -> IngestionResult:
        document = Document(str(uuid.uuid4()), path.name, department, frozenset(allowed_roles))
        chunks = chunk_pages(document.id, document.name, extract_pages(path))
        if not chunks:
            raise ValueError("No readable text was found in this document")
        self.store.save_document(document, chunks)
        self.index.add(chunks)
        return IngestionResult(document.name, len(chunks))

    def ask(self, question: str, user_role: str) -> ChatResponse:
        hits = self.index.search(question, self.store.allowed_chunk_ids(user_role))
        citations = [Citation(hit.chunk.document_name, hit.chunk.page_number, hit.chunk.text[:180] + ("..." if len(hit.chunk.text) > 180 else "")) for hit in hits]
        return ChatResponse(self.answerer.answer(question, hits), citations)

