import hashlib
import math
import os
import re
from abc import ABC, abstractmethod


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class HashEmbedder(Embedder):
    """Deterministic offline baseline, intended for MVP tests and demos."""

    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        output = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for token in re.findall(r"[a-z0-9]+", text.lower()):
                index = int(hashlib.sha256(token.encode()).hexdigest(), 16) % self.dimensions
                vector[index] += 1.0
            magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
            output.append([value / magnitude for value in vector])
        return output


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


def create_embedder() -> Embedder:
    kind = os.getenv("RAG_EMBEDDER", "hash").lower()
    if kind == "sentence-transformer":
        return SentenceTransformerEmbedder(os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"))
    return HashEmbedder()

