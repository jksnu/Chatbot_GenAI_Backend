import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from app.core.embedding import get_embedding
import logging
from app.core.util import get_uploaded_files

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="docs")

logger = logging.getLogger(__name__)

def add_documents_to_vector_store(docs: list[str], ids: list[str], filename: str) -> None:
    try:
        vectors = [get_embedding(text) for text in docs]
        collection.add(
            documents=docs, 
            embeddings=vectors, 
            ids=ids,
            metadatas=[{"filename": filename} for _ in docs]
        )
    except Exception as e:
        logger.error(f"Error adding documents to vector store: {e}")
        raise ValueError(f"Failed to add documents to vector store: {e}")

def query_similar_documents(query: str, top_k: int = 3) -> list[str]:
    try:
        context_files = get_uploaded_files()
        print(f"Context files available: {context_files}")
        if len(context_files) == 0:
            return []
        query_vector = get_embedding(query)
        results = collection.query(
            query_embeddings=[query_vector], 
            n_results=top_k,
            where={"filename": {"$in": context_files}}
        )
        return results["documents"][0]
    except Exception as e:
        logger.error(f"Error querying similar documents: {e}")
        raise ValueError(f"Failed to query similar documents: {e}")

def delete_document_by_filename(filename: str) -> bool:
    try:
        # Step 1: Get all IDs where metadata filename matches
        results = collection.get(where={"filename": filename})
        ids_to_delete = results.get("ids", [])

        if not ids_to_delete:
            return False

        # Step 2: Delete those vectors
        collection.delete(ids=ids_to_delete)
        return True
    except Exception as e:
        logger.error(f"Error deleting document by filename {filename}: {e}")
        raise ValueError(f"Failed to delete document by filename {filename}: {e}")
