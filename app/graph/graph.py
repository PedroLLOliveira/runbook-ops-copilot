from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from app.settings import settings
from app.rag.retrieve import retrieve
from app.policies.commands import is_allowed

class GraphState(TypedDict):
    question: str
    include_plan: bool
    docs: list
    answer: str
    plan: List[str]
    commands: List[str]
    citations: List[dict]
    need_more_info: bool

def node_retrieve(state: GraphState) -> GraphState:
    docs = retrieve(state["question"])
    state["docs"] = docs
    state["need_more_info"] = len(docs) == 0
    return state

def node_answer(state: GraphState) -> GraphState:
    if state["need_more_info"]:
        state["answer"] = (
            "Não encontrei evidências suficientes na base de runbooks para responder com segurança. "
            "Informe: serviço (nginx/api/db), ambiente (prod/stg/dev) e 1–2 sintomas (erro, timeout, CPU, trecho de log)."
        )
        state["plan"] = []
        state["commands"] = []
        state["citations"] = []
        return state

    llm = ChatOllama(
        model=settings.ollama_chat_model,
        base_url=settings.ollama_base_url,
        temperature=0,
        options={"num_predict": 280, "num_ctx": 2048},
    )

    sources_text = []
    citations = []
    for d in state["docs"]:
        src = d.metadata.get("source", "unknown")
        sources_text.append(f"SOURCE: {src}\n---\n{d.page_content}\n")
        citations.append({"source": src})

    system = SystemMessage(content=(
        "Você é um assistente de operações/SRE. "
        "Responda APENAS usando as fontes fornecidas. "
        "No final, inclua a seção 'Fontes' listando os SOURCE usados. "
        "Se faltar evidência, peça mais dados."
    ))
    user = HumanMessage(content=(
        f"Pergunta: {state['question']}\n\n"
        "Fontes:\n" + "\n".join(sources_text)
    ))

    state["answer"] = llm.invoke([system, user]).content
    state["citations"] = citations
    return state

def node_plan_and_commands(state: GraphState) -> GraphState:
    if state["need_more_info"] or not state.get("include_plan", False):
        state["plan"] = []
        state["commands"] = []
        return state

    llm = ChatOllama(
        model=settings.ollama_chat_model,
        base_url=settings.ollama_base_url,
        temperature=0,
        options={"num_predict": 220, "num_ctx": 2048},
    )

    system = SystemMessage(content=(
        "Gere um plano de troubleshooting em 5 a 7 passos, numerado. "
        "Depois gere até 5 comandos SÓ READ-ONLY (diagnóstico), um por linha, prefixados com '$ '. "
        "Não inclua comandos destrutivos."
    ))
    user = HumanMessage(content=f"Contexto: {state['question']}")
    resp = llm.invoke([system, user]).content

    plan, cmds = [], []
    for line in resp.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("$"):
            cmd = line[1:].strip()
            if is_allowed(cmd):
                cmds.append(cmd)
        else:
            plan.append(line)

    state["plan"] = plan[:7]
    state["commands"] = cmds[:5]
    return state

def build_graph():
    g = StateGraph(GraphState)
    g.add_node("retrieve", node_retrieve)
    g.add_node("answer_node", node_answer)
    g.add_node("plan_node", node_plan_and_commands)

    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "answer_node")
    g.add_edge("answer_node", "plan_node")
    g.add_edge("plan_node", END)

    return g.compile()
