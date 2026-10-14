from pathlib import Path

from .models import ExtractedPage


class UnsupportedDocumentError(ValueError):
    pass


def extract_pages(path: Path) -> list[ExtractedPage]:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return [ExtractedPage(page_number=1, text=path.read_text(encoding="utf-8", errors="replace"))]
    if suffix == ".pdf":
        from pypdf import PdfReader

        return [
            ExtractedPage(page_number=index, text=page.extract_text() or "")
            for index, page in enumerate(PdfReader(path).pages, start=1)
        ]
    if suffix == ".docx":
        from docx import Document

        document = Document(path)
        text = "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
        return [ExtractedPage(page_number=1, text=text)]
    raise UnsupportedDocumentError("Supported formats: PDF, DOCX, TXT")

