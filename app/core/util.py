from app.core.config import Config
from pathlib import Path

def get_uploaded_files():
     BASE_DIR = Path(__file__).resolve().parent.parent.parent
     req_dir = BASE_DIR/Config.UPLOAD_FOLDER
     return [
        file.name for file in Path(req_dir).iterdir() if file.is_file()
    ]
