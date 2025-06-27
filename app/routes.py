# app/routes.py
from flask import Blueprint, request, jsonify
import os
import logging
from werkzeug.utils import secure_filename
from pathlib import Path
from app.core.config import Config
from app.core.doc_loader import extract_texts_from_filepaths
from app.core.llm_query import answer_query
from app.core.process_documents import process_documents
from app.core.chroma_store import delete_document_by_filename

routes_bp = Blueprint("routes", __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
UPLOAD_FOLDER = Path(Config.UPLOAD_FOLDER)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@routes_bp.route("/upload", methods=["POST"])
def upload_documents():
    try:
        if "files" not in request.files:
            return jsonify({"error": "No files part in the request"}), 400

        files = request.files.getlist("files")

        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = UPLOAD_FOLDER / filename
                file.save(file_path)
                saved_files.append(str(file_path))
            else:
                return jsonify({"error": f"Unsupported file type: {file.filename}"}), 400

        # Extract text from files and process
        texts = extract_texts_from_filepaths(saved_files)
        if not texts:
            raise Exception(status_code=400, detail="No valid documents to process.")

        process_documents(texts)
        return jsonify(content={"message": "Documents uploaded and indexed successfully."})

    except Exception as e:
        logger.exception("Upload failed")
        return jsonify({"error": "Internal server error during file upload."}), 500


@routes_bp.route("/query", methods=["POST"])
def query_document():
    try:
        query = request.form.get("query")
        if not query:
            return jsonify({"error": "Query string is required."}), 400

        logger.info(f"Received query: {query}")

        question, answer = answer_query(query)
        return jsonify({"status_code":200, "content":{"question": question, "answer": answer}})
    except Exception as e:
        logger.exception("Query processing failed")
        return jsonify({"error": "Internal server error during query processing."}), 500

@routes_bp.route("/files", methods=["GET"])
def list_files():
    try:
        files = [file.name for file in UPLOAD_FOLDER.iterdir() if file.is_file()]
        return jsonify({"files": files})
    except Exception as e:
        logger.exception("Failed to list files")
        return jsonify({"error": "Internal server error while listing files."}), 500    
    
@routes_bp.route("/files/<filename>", methods=["DELETE"])
def delete_file(filename):
    try:
        #   Validate the filename
        if not filename or not filename.strip():    
            return jsonify({"error": "Filename cannot be empty."}), 400 
        
        #   checking if allowed file type for deletion
        if not allowed_file(filename):
            return jsonify({"error": "Unsupported file type for deletion."}), 400

        file_path = UPLOAD_FOLDER / filename
        if not file_path.exists():
            return jsonify({"error": "File not found."}), 404           
        
        #   Delete the document from the vector store
        logger.info(f"Deleting document with filename: {filename}")
        is_deleted = delete_document_by_filename(filename)
        if not is_deleted:
            return jsonify({"error": "No document found with the specified filename."}), 404    
            
        file_path.unlink()

        logger.info(f"File {filename} deleted successfully.")

        #   Return success message
        return jsonify({"message": f"File {filename} deleted successfully."})
    except Exception as e:
        logger.exception("Failed to delete file")
        return jsonify({"error": "Internal server error while deleting file."}), 500