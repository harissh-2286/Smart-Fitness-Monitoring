#!/usr/bin/env python3
"""
Smart Fitness Monitoring and Healthcare Application Launcher
"""
import sys
from pathlib import Path

# Add project root directory
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app
from backend.config import Config

app = create_app()

if __name__ == "__main__":
    print("=" * 70)
    print("SMART FITNESS MONITORING AND HEALTHCARE PLATFORM")
    print("Capstone Project - College Demonstration Server")
    print("=" * 70)
    print(f" * Server running on: http://{Config.HOST}:{Config.PORT}")
    print(f" * Firebase Mode:     {Config.FIREBASE_MODE.upper()}")
    print(" * Pre-configured Accounts:")
    print("     - Admin: admin@smartfitness.local  (Password: Admin@123456)")
    print("     - Demo:  demo@smartfitness.local   (Password: Demo@123456)")
    print("=" * 70)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
