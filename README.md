# Enterprise RAG Chatbot

A software-only, provider-independent RAG chatbot for internal documents. It ingests PDF, DOCX, and TXT files, retrieves relevant permitted chunks, and returns grounded answers with citations.

## Current MVP scope

- PDF, DOCX, and TXT ingestion
- Chunking with page-aware citations
- SQLite metadata store and local JSON vector index
- Role-based document filtering before answer generation
- Provider-independent answer interface
- Evidence-only extractive answerer, so no API key is required for tests or demonstrations

This MVP uses application-level RBAC for a demo environment. It does not claim live IAM, SSO, or production security controls.

The default answerer selects the most question-relevant sentences from permitted retrieved evidence. It does not use an external AI provider or make unsupported inferences. A later LLM adapter can use the same provider-independent interface.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

For better semantic retrieval on a machine that can download models:

```powershell
pip install -e ".[dev,local-embeddings]"
```

## Run

```powershell
streamlit run app.py
```

Choose a demo role, select one or more documents, assign a department and allowed roles for that upload batch, then ask a question. The default hash embedder keeps the system runnable offline. Select the SentenceTransformer embedder only after its model is available locally.

## Demo documents and roles

The `sample_documents/` folder contains fictional documents for a safe demonstration. Upload them through the app with the following permissions:

| Document | Allowed roles |
| --- | --- |
| `employee_handbook.txt` | employee, hr, it, finance, manager, admin |
| `hr_leave_policy.txt` | hr, manager, admin |
| `it_vpn_policy.txt` | it, admin |
| `finance_budget_policy.txt` | finance, manager, admin |

## Roles and security boundary

Each document has an explicit allowed-role list. Retrieval filters chunks by that list *before* context goes to the answerer. The UI role picker represents a demo login, not authentication. Later work should replace it with real authentication and authorization.

## Tests

```powershell
pytest
```

