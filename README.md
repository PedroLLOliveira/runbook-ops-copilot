# 🛠️ Runbook Ops Copilot
**RAG + LangGraph para troubleshooting operacional com evidências, segurança e respostas acionáveis.**

> Um copiloto para times de engenharia/SRE: consulta runbooks, playbooks e docs internas, sugere um plano de investigação e gera comandos **read-only** com política de segurança — sempre com **citações** das fontes.

---

## ✨ Por que este projeto existe
Em incidentes, o que mais consome tempo é:
- encontrar o runbook certo,
- coletar sinais (logs/métricas),
- seguir um plano consistente,
- e evitar ações destrutivas por impulso.

O **Runbook Ops Copilot** organiza esse fluxo com **RAG** e uma **máquina de estados (LangGraph)**, entregando respostas:
- ✅ **Grounded** (com citações)
- ✅ **Ação + contexto** (plano passo a passo)
- ✅ **Seguras** (policy gate para comandos)

---

## 🚀 O que ele faz (MVP)
- 🔎 **Perguntas operacionais com RAG**  
  “Por que minha API está dando 502 no Nginx?” → resposta com trechos de runbook + diagnóstico provável.
- 🧭 **Plano de troubleshooting (checklist)**  
  Passos numerados com o que verificar, em qual ordem, e por quê.
- 🧪 **Comandos sugeridos com segurança**  
  Por padrão, gera apenas comandos **read-only** (ex.: `curl`, `journalctl`, `kubectl get`, `docker ps`).  
  Para comandos arriscados, o assistente **bloqueia** ou exige confirmação explícita.
- 📎 **Citações obrigatórias**  
  Cada resposta vem com “Fontes” apontando os documentos/chunks usados.
- ⚡ **Modo rápido (recomendado para CPU)**  
  Você pode rodar sem gerar plano/comandos para reduzir latência (1 chamada de LLM por request).

---

## 🧠 Arquitetura (LangGraph)
O fluxo é orquestrado por um grafo de estados:

```text
User Query
   |
   v
[1] classify_intent  ---> (Q&A | Incident | Command)   (v2)
   |
   v
[2] extract_context  ---> service/env/symptoms         (v2)
   |
   v
[3] retrieve_knowledge (pgvector)
   |
   v
[4] compose_answer_with_citations
   |
   v
[5] grounding_gate
   |        \
   |         -> ask_for_more_info (when insufficient evidence)
   v
[6] generate_plan_and_commands (optional)
   |
   v
[7] safety_policy_gate (allowlist + risk)
   |
   v
Final Answer (+ citations + optional plan + optional commands)
```
>No MVP atual, os nós classify_intent e extract_context podem ser implementados na v2, mantendo o core: retrieval → resposta com citações → plano/comandos opcional.

🧰 Stack

- Backend: FastAPI (Python)
- RAG/Orquestração: LangChain + LangGraph
- Vector Store: PostgreSQL + pgvector
- LLM local: Ollama (Chat + Embeddings)
- UI: Streamlit (MVP) (ou Vue/Vite em v2)
- Execução: Docker Compose

📦 Estrutura do repositório
```
.
├── app/
│   ├── api/                 # FastAPI routes
│   ├── graph/               # LangGraph nodes + state
│   ├── rag/                 # chunking, embeddings, retrieval
│   ├── policies/            # command allowlist + risk rules
│   └── settings.py
├── ui/                      # Streamlit UI
├── knowledge_base/          # runbooks, playbooks, docs (md/txt/log)
├── docker/postgres/         # init SQL (pgvector)
├── docker-compose.yml
├── Dockerfile
└── README.md
```

⚡ Quickstart (Docker + Ollama local)
1) Subir Postgres + Ollama + API
``` bash
docker compose up -d --build
```

2) Baixar modelos no Ollama (dentro do container)
``` bash
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama list
```

> Dica: em notebooks/CPU, modelos 3B/mini tendem a ser mais rápidos.

3) Indexar a base de conhecimento

Coloque seus arquivos em ./knowledge_base/ e rode:
``` bash
curl -s -X POST http://localhost:8000/api/ingest | jq
```

4) Testar a API

Health:
``` bash
curl -s http://localhost:8000/api/health
```

Chat (modo rápido):
``` bash
curl -s -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Nginx está retornando 502. Por onde começo?", "include_plan": false}' | jq
```

Chat (com plano + comandos):
``` bash
curl -s -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Nginx 502 em produção. Gere plano e comandos read-only.", "include_plan": true}' | jq
```

---
🖥️ Rodar a UI (Streamlit)

No host:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt streamlit requests
streamlit run ui/app.py
```

---
🔐 Política de segurança (MVP)

Este projeto não executa comandos em servidores reais. Ele apenas sugere comandos e aplica política de risco.

Padrão: allowlist read-only

- ✅ permitidos: curl, ping, journalctl, kubectl get/describe/logs, docker ps/logs, ps, df -h, etc.
- ❌ bloqueados: rm, kill, kubectl delete, DROP/DELETE, systemctl stop, iptables, etc.

Se a pergunta exigir ação destrutiva, o assistente:

- pede confirmação explícita e
- sugere alternativas seguras primeiro.

---
📚 Base de conhecimento (knowledge_base)

Para o projeto ficar “portfolio-ready”, inclua 8–12 runbooks clássicos:
- API 5xx / timeout (Nginx upstream, app)
- Postgres slow queries / locks
- CPU/RAM alta (processo/container)
- Disk full
- Deploy falhou / rollback
- SSL/TLS expiring
- DNS/network issues

Cada runbook idealmente tem:
- sintomas
- hipóteses
- checklist
- comandos read-only
- quando escalar