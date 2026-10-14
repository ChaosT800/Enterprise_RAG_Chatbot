from pathlib import Path

import streamlit as st

from enterprise_rag.answerer import EvidenceOnlyAnswerer
from enterprise_rag.embeddings import create_embedder
from enterprise_rag.service import EnterpriseRAGService
from enterprise_rag.store import SQLiteStore


@st.cache_resource
def service() -> EnterpriseRAGService:
    root = Path("data")
    return EnterpriseRAGService(
        store=SQLiteStore(root / "enterprise_rag.db"),
        index_path=root / "vector_index.json",
        embedder=create_embedder(),
        answerer=EvidenceOnlyAnswerer(),
    )


st.set_page_config(page_title="Enterprise RAG Chatbot", page_icon="📚")
st.title("Enterprise RAG Chatbot")
st.caption("Software-only RAG MVP with source citations and role-filtered retrieval")

rag = service()
roles = ["employee", "hr", "it", "finance", "manager", "admin"]
role = st.sidebar.selectbox("Demo user role", roles, index=0)

with st.sidebar:
    st.subheader("Upload knowledge")
    uploaded_files = st.file_uploader("PDF, DOCX, or TXT", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    department = st.text_input("Department", value="General")
    allowed_roles = st.multiselect("Allowed roles", roles, default=["employee"])
    if st.button("Ingest documents", disabled=not uploaded_files or not allowed_roles):
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for uploaded in uploaded_files:
            target = upload_dir / uploaded.name
            target.write_bytes(uploaded.getvalue())
            results.append(rag.ingest_file(target, department=department, allowed_roles=allowed_roles))
        chunk_count = sum(result.chunk_count for result in results)
        st.success(f"Indexed {len(results)} documents and {chunk_count} chunks.")

question = st.text_input("Ask a question about permitted enterprise documents")
if st.button("Ask", type="primary", disabled=not question.strip()):
    response = rag.ask(question, user_role=role)
    st.subheader("Answer")
    st.write(response.answer)
    st.subheader("Sources")
    if response.citations:
        for citation in response.citations:
            st.markdown(f"- **{citation.document_name}**, page {citation.page_number}: {citation.excerpt}")
    else:
        st.info("No permitted source was retrieved.")

