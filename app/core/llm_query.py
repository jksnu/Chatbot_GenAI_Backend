import os
import requests
import logging
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import chromadb
from chromadb.config import Settings
from app.core.chroma_store import query_similar_documents, add_documents_to_vector_store

logger = logging.getLogger(__name__)

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
LLM_MODEL = os.getenv("LLM_MODEL") #    mistralai/Mixtral-8x7B-Instruct-v0.1

headers = {
    "Authorization": f"Bearer {os.getenv("HUGGINGFACEHUB_API_TOKEN")}",
    "Content-Type": "application/json"
}

client = chromadb.Client(Settings(persist_directory="./chroma_store"))
collection = client.get_or_create_collection("documents")

def extract_qa(response_text):
    try:
        question_match = re.search(r"(?i)question:\s*(.+)", response_text)
        answer_match = re.search(r"(?i)answer:\s*(.+)", response_text)

        question = question_match.group(1).strip() if question_match else ""
        answer = answer_match.group(1).strip() if answer_match else ""

        return question, answer
    except Exception as e:
        logger.error(f"Error extracting question and answer: {e}")
        raise ValueError("Failed to extract question and answer from the response.")

def get_llm_response(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.5,
                "max_new_tokens": 200
            }
        }

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{LLM_MODEL}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        output = response.json()
    
        if isinstance(output, list) and "generated_text" in output[0]:
            return extract_qa(output[0]["generated_text"])
        else:
            raise ValueError(f"Unexpected response: {output}")
    except Exception as e:
        logger.error(f"Error getting LLM response: {e}")
        raise ValueError("Failed to get response from the LLM model.")

def answer_query(query: str) -> str:
    try:
        similar_docs = query_similar_documents(query)

        if len(similar_docs) == 0:
            return query, "No relevant documents found for your query."
        
        context = "\n".join(similar_docs)
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        return get_llm_response(prompt)
    except Exception as e:
        logger.exception("Error answering query")
        return "Sorry, could not process your query."
