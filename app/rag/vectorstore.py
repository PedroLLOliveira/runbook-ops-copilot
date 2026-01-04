from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from app.settings import settings

def get_vectorstore() -> PGVector:
    embeddings = OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )
    return PGVector(
        embeddings=embeddings,
        collection_name=settings.collection_name,
        connection=settings.postgres_dsn,
        use_jsonb=True,
    )
