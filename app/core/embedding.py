
import requests
from typing import List
import os
import logging

headers = {
    "Authorization": f"Bearer {os.getenv("HUGGINGFACEHUB_API_TOKEN")}",
    "Content-Type": "application/json"
}

logger = logging.getLogger(__name__)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")    

# Function to get embedding for a given text using Hugging Face API
# This function assumes that the environment variable EMBEDDING_MODEL is set to a valid Hugging Face model ID
# Example: EMBEDDING_MODEL="BAAI/bge-small-en-v1.5"

def get_embedding(text: str) -> List[float]:
    try:
        url = f"https://api-inference.huggingface.co/models/{EMBEDDING_MODEL}"
        print(f"url: {url}")
        response = requests.post(url, headers=headers, json={"inputs": text}, timeout=60)
        response.raise_for_status()
        embedding = response.json()
        return embedding  # This is a list of floats
    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        raise ValueError("Failed to get embedding from the model.")