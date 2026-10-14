from abc import ABC, abstractmethod
import re

from .models import SearchHit


class Answerer(ABC):
    @abstractmethod
    def answer(self, question: str, evidence: list[SearchHit]) -> str:
        raise NotImplementedError


class EvidenceOnlyAnswerer(Answerer):
    """A deterministic, evidence-only answerer for offline demonstrations.

    It deliberately makes no claims beyond permitted retrieved text. A future
    LLM adapter can implement the same Answerer interface without changing
    ingestion, retrieval, or access-control code.
    """

    def answer(self, question: str, evidence: list[SearchHit]) -> str:
        if not evidence:
            return "I could not find permitted evidence to answer that question."
        question_terms = set(re.findall(r"[a-z0-9]+", question.lower()))
        candidates: list[tuple[int, str]] = []
        for hit in evidence:
            sentences = re.split(r"(?<=[.!?])\s+", hit.chunk.text)
            for sentence in sentences:
                terms = set(re.findall(r"[a-z0-9]+", sentence.lower()))
                overlap = len(question_terms & terms)
                if sentence.strip():
                    candidates.append((overlap, sentence.strip()))

        selected = []
        for _, sentence in sorted(candidates, key=lambda item: item[0], reverse=True):
            if sentence not in selected:
                selected.append(sentence)
            if len(selected) == 2:
                break
        return "Based on the permitted documents, " + " ".join(selected)

