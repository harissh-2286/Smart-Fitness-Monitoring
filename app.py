#!/usr/bin/env python3
"""
Root Flask Entrypoint (compatible with Vercel, Gunicorn, and local runners)
"""
import sys
from pathlib import Path

# Add project root directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.config import Config

app = create_app()

if __name__ == "__main__":
    print("=" * 70)
    print("SMART FITNESS MONITORING AND HEALTHCARE PLATFORM")
    print("Capstone Project - Running locally on http://127.0.0.1:5000")
    print("=" * 70)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
