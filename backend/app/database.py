"""
Argos — Supabase Database Client
Singleton client with all CRUD helper methods.
Uses lazy initialization to avoid crashing on import if .env is not populated.
"""

import logging
from datetime import datetime, timezone
from supabase import create_client, Client

from app.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# ── Supabase Client Singleton ───────────────────────────────
_supabase_client: Client | None = None
