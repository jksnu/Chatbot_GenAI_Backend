import uuid
from app.core.chroma_store import add_documents_to_vector_store
import re
import logging

logger = logging.getLogger(__name__)

def process_documents(doc_texts: dict[str, list[str]]) -> None:
    """
    Splits and adds document text to ChromaDB vector store.
    """
    try:
        #all_chunks = []
        #ids = []

        for doc_text_key, doc_text_value in doc_texts.items():
            doc_text = doc_text_value
            filename = doc_text_key
            # 1. Split document into chunks
            chunks = split_text(doc_text)  # Either use Langchain's splitter or define your own
            ids = []
            # 2. Append chunks and generate unique IDs
            #all_chunks.extend(chunks)
            ids.extend([str(uuid.uuid4()) for _ in chunks])

            # 3. Add to Chroma vector store
            add_documents_to_vector_store(chunks, ids, filename)

        # 3. Add to Chroma vector store
        #add_documents_to_vector_store(all_chunks, ids)

        logger.info("Documents processed and stored in Chroma vector DB.")
    except Exception as e:
        logger.error(f"Failed to process documents: {e}")
        raise ValueError(f"Failed to process documents: {e}")
    
# text_splitter.py
# This is a simple text splitter that can be replaced with Langchain's splitter if needed.
# It splits text into chunks while preserving sentence boundaries.

def split_text(text: str, max_chunk_size: int = 500) -> list[str]:
    """
    Splits text into chunks of up to `max_chunk_size` characters, preserving sentence boundaries.
    """
    try:
        sentences = re.split(r'(?<=[.!?]) +', text)
        
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
    except Exception as e:
        logger.error(f"Error splitting text: {e}")
        raise ValueError(f"Failed to split text: {e}")