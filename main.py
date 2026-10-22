"""Launcher for the Grid Balance project.

Running this file from anywhere starts the Flask application in backend/:

    python main.py

To read the pipeline output in the console instead, run
backend/main.py directly.

The port defaults to 5005 so Grid Balance never collides with the
PlacementPrediction app, which listens on 5000. To override:

    set GRIDBALANCE_PORT=5001
    python main.py
"""

import os
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent

BACKEND_DIR = PROJECT_DIR / "backend"

if not BACKEND_DIR.exists():

    raise SystemExit(f"Backend folder not found at: {BACKEND_DIR}")

# Backend modules import each other by name, so this folder must be importable.
sys.path.insert(0, str(BACKEND_DIR))

from App import app  # noqa: E402


if __name__ == "__main__":

    port = int(os.environ.get("GRIDBALANCE_PORT", 5005))

    print(f"Grid Balance Project")
    print(f"Application folder: {BACKEND_DIR}")
    print(f"Starting on http://127.0.0.1:{port}")
    print()

    app.run(debug=True, port=port)
