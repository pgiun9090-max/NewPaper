"""
Root entry point forwarding to Source/main.py
"""
import sys
from pathlib import Path

# Add Source directory to sys.path
SOURCE_DIR = Path(__file__).resolve().parent / "Source"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from main import main

if __name__ == "__main__":
    main()

