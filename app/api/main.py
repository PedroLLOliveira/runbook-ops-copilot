from fastapi import FastAPI
from pydantic import BaseModel
from app.graph.graph import build_graph

app = FastAPI(title="Runbook Ops Copilot", version="0.1.0")
graph = build_graph()

class ChatIn(BaseModel):
    message: str
    include_plan: bool = False

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/ingest")
def ingest():
    from app.rag.ingest import ingest as do_ingest
    return do_ingest()

@app.post("/api/chat")
def chat(payload: ChatIn):
    state = {
        "question": payload.message,
        "include_plan": payload.include_plan,
        "docs": [],
        "answer": "",
        "plan": [],
        "commands": [],
        "citations": [],
        "need_more_info": False,
    }
    out = graph.invoke(state)
    return {
        "answer": out["answer"],
        "plan": out["plan"],
        "commands": out["commands"],
        "citations": out["citations"],
        "need_more_info": out["need_more_info"],
    }
