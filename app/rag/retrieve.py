from app.rag.vectorstore import get_vectorstore
from app.settings import settings

def retrieve(query: str):
    vs = get_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": settings.top_k})
    return retriever.invoke(query)
