from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
import os

load_dotenv()

def build_qdrant_store(fewshots: list[str], embeddings, metadata: list[dict[str,str]]):
  url = os.getenv("QDRANT_URL")
  collection_name = os.getenv("QDRANT_COLLECTION_NAME")
  client = QdrantClient(url=url)

  existing = [c.name for c in client.get_collections().collections]
  if collection_name in existing:
    # Connect to existing — no re-embedding
    return QdrantVectorStore(
      client=client,
      collection_name=collection_name,
      embedding=embeddings,
    )
  else:
    qdrant = QdrantVectorStore.from_texts(
      texts=fewshots,
      embedding=embeddings,
      metadatas=metadata,
      url=url,
      collection_name=collection_name,
    )
  
  return qdrant