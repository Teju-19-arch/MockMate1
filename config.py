"""
config.py
---------
Centralized Configuration for MockMate Technical Interview Module.
Loads environment variables for Gemini API key, model selection,
caching settings, retry policies, and application constants.
"""

import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file if present
load_dotenv(os.path.join(BASE_DIR, ".env"))

# ---------------------------------------------------------------------------
# Gemini API Configuration
# ---------------------------------------------------------------------------
# Reads Gemini API Key from environment variables (.env or system env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

# ---------------------------------------------------------------------------
# Retry & Resilience Settings
# ---------------------------------------------------------------------------
MAX_API_RETRIES = int(os.getenv("MAX_API_RETRIES", "3"))
RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "2"))
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "15"))

# ---------------------------------------------------------------------------
# Caching Settings
# ---------------------------------------------------------------------------
ENABLE_QUESTION_CACHE = os.getenv("ENABLE_QUESTION_CACHE", "True").lower() in ("true", "1", "yes")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour cache TTL

# ---------------------------------------------------------------------------
# Technical Interview Module Configuration Defaults
# ---------------------------------------------------------------------------
DEFAULT_QUESTION_COUNT = 5
MAX_QUESTION_COUNT = 20

DEFAULT_TIME_LIMIT_MINUTES = 10

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

AVAILABLE_DOMAINS = [
    "AIML",
    "Web Development",
    "Data Science",
    "Core CS",
    "Cloud & DevOps"
]

SUPPORTED_COMPANIES = [
    "TCS",
    "Infosys",
    "Wipro",
    "Accenture",
    "Amazon",
    "Google",
    "Microsoft"
]
