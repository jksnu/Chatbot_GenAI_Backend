# app/main.py
from flask import Flask
from flask_cors import CORS
from app.core.logger import setup_logging
from app.routes import routes_bp
import os
from dotenv import load_dotenv
from app.core.config import Config

# Load environment variables from .env
load_dotenv()

# Setup logging
setup_logging()

# Create Flask app
app = Flask(__name__)

# Configure CORS (allow frontend origin if needed)
CORS(app, resources={r"/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(routes_bp)

app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH_MB * 1024 * 1024

@app.route("/")
def root():
    return {"message": "Document Search Bot API (Flask) is running."}

# Entry point (for development)
# if __name__ == "__main__":
#     port = int(os.getenv("APP_PORT", 8000))
#     app.run(host="0.0.0.0", port=port, debug=True)
