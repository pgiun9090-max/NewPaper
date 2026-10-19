"""
Configuration settings for the Newspaper Generator.
Loads environment variables from .env and provides sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory (Project Root: d:\NewsPaper)
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = Path(__file__).resolve().parent

# Load environment variables from root .env
load_dotenv(BASE_DIR / ".env")

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Gmail IMAP Settings
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
GMAIL_USER = os.getenv("GMAIL_USER", "pgiun9090@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()
GMAIL_LABEL = os.getenv("GMAIL_LABEL", "News")

# Newspaper Metadata Settings
NEWSPAPER_NAME = os.getenv("NEWSPAPER_NAME", "Mars Tech Daily")
NEWSPAPER_EDITION = os.getenv("NEWSPAPER_EDITION", "Mars 에디션")
NEWSPAPER_PUBLISHER = os.getenv("NEWSPAPER_PUBLISHER", "LeeJaeHoon")

# Scheduling Settings
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "08:00")

# Directories
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "Output"
IMAGE_DIR = BASE_DIR / "Image"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
