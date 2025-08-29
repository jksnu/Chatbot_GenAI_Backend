# SearchBot API

This is RAG based SearchBot API using HuggingFace Model and HuggingFace Embedded model. It is using ChromaDB as a Vector DB. UI uploads files that is used as a context for generating the response.

# SearchBot UI Repo

https://github.com/jksnu/ChatBot_GenAI_UI.git

# Python version

3.10.0

# Run command

python run.py

# .ENV

APP_PORT=8000

UPLOAD_FOLDER=data/uploads

VECTOR_DIR=data/vector_store

LOG_DIR=logs

MAX_CONTENT_LENGTH_MB=2

HUGGINGFACEHUB_API_TOKEN=Your_HuggingFace_API_Token

LLM_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
