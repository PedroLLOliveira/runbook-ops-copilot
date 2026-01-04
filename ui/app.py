import requests
import streamlit as st
from requests.exceptions import ReadTimeout, ConnectionError

st.set_page_config(page_title="Runbook Ops Copilot", layout="wide")
st.title("🛠️ Runbook Ops Copilot")

include_plan = st.checkbox("Gerar plano + comandos (mais lento)", value=False)
q = st.text_area("Pergunta", placeholder="Ex.: Nginx 502 em produção, como diagnosticar?", height=120)

if st.button("Perguntar"):
    try:
        r = requests.post(
            "http://127.0.0.1:8000/api/chat",
            json={"message": q, "include_plan": include_plan},
            timeout=600
        )
        r.raise_for_status()
        data = r.json()
    except ConnectionError:
        st.error("API offline. Verifique `docker compose ps` e `curl http://localhost:8000/api/health`.")
        st.stop()
    except ReadTimeout:
        st.error("Timeout. O modelo local ainda está processando. Use um modelo menor ou desmarque 'Gerar plano'.")
        st.stop()

    st.subheader("Resposta")
    st.write(data["answer"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Plano")
        if data["plan"]:
            for step in data["plan"]:
                st.write(step)
        else:
            st.caption("Plano desativado (modo rápido).")

    with col2:
        st.subheader("Comandos (read-only)")
        if data["commands"]:
            for cmd in data["commands"]:
                st.code(cmd)
        else:
            st.caption("Comandos desativados (modo rápido).")

    st.subheader("Fontes")
    st.json(data["citations"])
