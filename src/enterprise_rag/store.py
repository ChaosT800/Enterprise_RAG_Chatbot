import json
import sqlite3
from pathlib import Path

from .models import Chunk, Document


class SQLiteStore:
    def __init__(self, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.connection.execute("CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, name TEXT, department TEXT, allowed_roles TEXT)")
        self.connection.execute("CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, document_id TEXT, document_name TEXT, page_number INTEGER, text TEXT)")
        self.connection.commit()

    def save_document(self, document: Document, chunks: list[Chunk]) -> None:
        self.connection.execute("INSERT OR REPLACE INTO documents VALUES (?, ?, ?, ?)", (document.id, document.name, document.department, json.dumps(sorted(document.allowed_roles))))
        self.connection.executemany("INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?, ?)", [(chunk.id, chunk.document_id, chunk.document_name, chunk.page_number, chunk.text) for chunk in chunks])
        self.connection.commit()

    def allowed_chunk_ids(self, user_role: str) -> set[str]:
        rows = self.connection.execute("SELECT id, allowed_roles FROM documents").fetchall()
        allowed_documents = {document_id for document_id, roles in rows if user_role in json.loads(roles)}
        return {row[0] for row in self.connection.execute("SELECT id FROM chunks WHERE document_id IN ({})".format(",".join("?" for _ in allowed_documents)), tuple(allowed_documents)).fetchall()} if allowed_documents else set()

