import os
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.vectorstore import get_vectorstore

KB_DIR = Path("knowledge_base")

def load_docs() -> list[Document]:
    docs: list[Document] = []
    for path in KB_DIR.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix.lower() not in {".md", ".txt", ".log"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        docs.append(Document(page_content=text, metadata={"source": str(path)}))
    return docs

def ingest() -> dict:
    raw_docs = load_docs()
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_documents(raw_docs)

    vs = get_vectorstore()

    ids = [f"{c.metadata.get('source')}::chunk::{i}" for i, c in enumerate(chunks)]
    vs.add_documents(chunks, ids=ids)

    return {"files": len(raw_docs), "chunks": len(chunks)}

if __name__ == "__main__":
    result = ingest()
    print(result)
