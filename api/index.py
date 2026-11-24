import sys
from pathlib import Path

# Add project root directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import create_app

app = create_app()
