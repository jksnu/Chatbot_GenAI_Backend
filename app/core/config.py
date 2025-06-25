# app/core/config.py
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    APP_PORT = int(os.getenv("APP_PORT", 8000))
    ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "xlsx", "txt"}
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "data/uploads")
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    VECTOR_DIR = os.getenv("VECTOR_DIR", "data/vectorstore")
    MAX_CONTENT_LENGTH_MB = int(os.getenv("MAX_CONTENT_LENGTH_MB", 2))  # Max upload size per file
