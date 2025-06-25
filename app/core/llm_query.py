import os
import requests
import logging
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

logger = logging.getLogger(__name__)

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") #    sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL = os.getenv("LLM_MODEL") #    mistralai/Mixtral-8x7B-Instruct-v0.1

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
    "Content-Type": "application/json"
}

documents = []
document_vectors = []
vectorizer = None

def get_embedding(text: str) -> List[float]:
    url = f"https://api-inference.huggingface.co/feature-extraction/{EMBEDDING_MODEL}"
    response = requests.post(url, headers=headers, json={"inputs": text})
    response.raise_for_status()
    embedding = response.json()
    return embedding  # This is a list of floats

def get_llm_response(prompt: str) -> str:
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

def extract_qa(response_text):
    question_match = re.search(r"(?i)question:\s*(.+)", response_text)
    answer_match = re.search(r"(?i)answer:\s*(.+)", response_text)

    question = question_match.group(1).strip() if question_match else ""
    answer = answer_match.group(1).strip() if answer_match else ""

    return question, answer

def process_documents(doc_texts: List[str]):
    global documents, document_vectors, vectorizer
    try:
        logger.info("Processing documents...")
        documents = doc_texts
        vectorizer = TfidfVectorizer()
        document_vectors = vectorizer.fit_transform(documents)
        logger.info("Documents embedded and stored.")
    except Exception as e:
        logger.exception("Failed to process documents.")
        raise e

def answer_query(query: str) -> str:
    try:
        if document_vectors is None or document_vectors.shape[0] == 0:
            return "No documents available. Please upload documents first."

        query_vector = vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, document_vectors).flatten()

        if similarities.max() < 0.1:
            return "No relevant documents found."

        best_index = similarities.argmax()
        context = documents[best_index]

        prompt = f"Answer the question based on the context below.\n\nContext:\n{context}\n\nQuestion:\n{query}\nAnswer:"
        answer = get_llm_response(prompt)
        return answer
    except Exception as e:
        logger.exception("Error answering query")
        return "Sorry, could not process your query."
