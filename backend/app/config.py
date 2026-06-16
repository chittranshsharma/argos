"""
Argos — Central Configuration
All constants and settings loaded from environment.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# ── LLM Models ──────────────────────────────────────────────
GROQ_MODEL = "llama-3.1-8b-instant"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_EMBEDDING_MODEL = "text-embedding-004"

# ── Scheduling ──────────────────────────────────────────────
MONITOR_INTERVAL_HOURS = 6
WEEKLY_DIGEST_DAY = "monday"
WEEKLY_DIGEST_HOUR = 9
ALERT_CHECK_INTERVAL_MINUTES = 15

# ── Importance Detection ────────────────────────────────────
HIGH_IMPORTANCE_KEYWORDS = [
    "launch", "acquisition", "funding", "layoff", "hire",
    "partnership", "breach", "outage", "IPO", "pivot"
]

# ── Supabase ────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ── Neo4j ───────────────────────────────────────────────────
NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# ── LLM API Keys ───────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── News API ────────────────────────────────────────────────
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# ── Reddit ──────────────────────────────────────────────────
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "Argos/1.0")

# ── ProductHunt ─────────────────────────────────────────────
PRODUCTHUNT_DEVELOPER_TOKEN = os.getenv("PRODUCTHUNT_DEVELOPER_TOKEN", "")

# ── Telegram ────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Gmail ───────────────────────────────────────────────────
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

# ── API ─────────────────────────────────────────────────────
API_PORT = int(os.getenv("API_PORT", "8001"))
NEXT_PUBLIC_API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8001")
