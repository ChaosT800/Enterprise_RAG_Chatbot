from pathlib import Path

from enterprise_rag.answerer import EvidenceOnlyAnswerer
from enterprise_rag.embeddings import HashEmbedder
from enterprise_rag.service import EnterpriseRAGService
from enterprise_rag.store import SQLiteStore


def make_service(tmp_path: Path) -> EnterpriseRAGService:
    return EnterpriseRAGService(SQLiteStore(tmp_path / "db.sqlite"), tmp_path / "index.json", HashEmbedder(), EvidenceOnlyAnswerer())


def test_role_filtering_prevents_restricted_citation(tmp_path: Path) -> None:
    public_file = tmp_path / "handbook.txt"
    public_file.write_text("Employees may request annual leave from their manager.")
    finance_file = tmp_path / "forecast.txt"
    finance_file.write_text("The confidential quarterly revenue forecast is twelve percent growth.")
    rag = make_service(tmp_path)
    rag.ingest_file(public_file, "HR", ["employee", "admin"])
    rag.ingest_file(finance_file, "Finance", ["finance", "admin"])

    employee = rag.ask("What is the confidential quarterly revenue forecast?", "employee")
    finance = rag.ask("What is the confidential quarterly revenue forecast?", "finance")

    assert all(citation.document_name != "forecast.txt" for citation in employee.citations)
    assert any(citation.document_name == "forecast.txt" for citation in finance.citations)


def test_no_permitted_evidence_returns_safe_message(tmp_path: Path) -> None:
    document = tmp_path / "it.txt"
    document.write_text("VPN access is available through the IT help desk.")
    rag = make_service(tmp_path)
    rag.ingest_file(document, "IT", ["it"])

    response = rag.ask("How do I access the VPN?", "employee")

    assert response.citations == []
    assert "could not find permitted evidence" in response.answer


def test_answer_uses_relevant_sentence_from_permitted_evidence(tmp_path: Path) -> None:
    document = tmp_path / "leave.txt"
    document.write_text("The office is open on weekdays. Full-time employees receive twenty annual leave days per calendar year.")
    rag = make_service(tmp_path)
    rag.ingest_file(document, "HR", ["hr"])

    response = rag.ask("How many annual leave days do full-time employees receive?", "hr")

    assert "twenty annual leave days" in response.answer
