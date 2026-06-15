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

def get_supabase_client() -> Client:
    """Lazy initialize the Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


# ── Companies ───────────────────────────────────────────────
