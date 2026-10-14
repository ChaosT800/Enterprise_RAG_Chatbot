import json
from pathlib import Path

from .embeddings import Embedder
from .models import Chunk, SearchHit


class LocalVectorIndex:
    def __init__(self, index_path: Path, embedder: Embedder) -> None:
        self.index_path = index_path
        self.embedder = embedder
        self.records = json.loads(index_path.read_text()) if index_path.exists() else []

    def add(self, chunks: list[Chunk]) -> None:
        vectors = self.embedder.embed([chunk.text for chunk in chunks])
        self.records.extend({"id": chunk.id, "document_id": chunk.document_id, "document_name": chunk.document_name, "page_number": chunk.page_number, "text": chunk.text, "vector": vector} for chunk, vector in zip(chunks, vectors))
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(json.dumps(self.records))

    def search(self, question: str, allowed_chunk_ids: set[str], limit: int = 4, minimum_score: float = 0.08) -> list[SearchHit]:
        if not allowed_chunk_ids:
            return []
        query = self.embedder.embed([question])[0]
        hits = []
        for record in self.records:
            if record["id"] not in allowed_chunk_ids:
                continue
            score = sum(left * right for left, right in zip(query, record["vector"]))
            chunk = Chunk(record["id"], record["document_id"], record["document_name"], record["page_number"], record["text"])
            if score >= minimum_score:
                hits.append(SearchHit(chunk, score))
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]

