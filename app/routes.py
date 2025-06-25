# app/routes.py
from flask import Blueprint, request, jsonify
import os
import logging
from werkzeug.utils import secure_filename
from pathlib import Path
from app.core.config import Config
from app.core.doc_loader import extract_texts_from_folder
from app.core.llm_query import process_documents, answer_query

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
        texts = extract_texts_from_folder(UPLOAD_FOLDER)
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

        response = answer_query(query)
        return jsonify({"status_code":200, "content":response})
    except Exception as e:
        logger.exception("Query processing failed")
        return jsonify({"error": "Internal server error during query processing."}), 500
