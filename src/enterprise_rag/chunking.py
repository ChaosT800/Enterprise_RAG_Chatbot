import re
import uuid

from .models import Chunk, ExtractedPage


def chunk_pages(document_id: str, document_name: str, pages: list[ExtractedPage], *, size: int = 700, overlap: int = 120) -> list[Chunk]:
    if size <= overlap:
        raise ValueError("Chunk size must be larger than overlap")
    chunks: list[Chunk] = []
    for page in pages:
        text = re.sub(r"\s+", " ", page.text).strip()
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            if end < len(text):
                break_at = text.rfind(" ", start + size // 2, end)
                if break_at > start:
                    end = break_at
            section = text[start:end].strip()
            if section:
                chunks.append(Chunk(str(uuid.uuid4()), document_id, document_name, page.page_number, section))
            if end == len(text):
                break
            start = end - overlap
    return chunks

