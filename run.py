# run.py
from app.main import app
import os
from app.core.config import Config

if __name__ == "__main__":
    port = Config.APP_PORT
    app.run(host="0.0.0.0", port=port, debug=True)
