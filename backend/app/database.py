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

def get_all_companies() -> list:
    """Return all active companies."""
    try:
        client = get_supabase_client()
        response = client.table("companies").select("*").eq("is_active", True).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting all companies: {e}")
        return []


def get_company_by_id(company_id: str) -> dict:
    """Return a single company by UUID."""
    try:
        client = get_supabase_client()
        response = client.table("companies").select("*").eq("id", company_id).single().execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {e}")
        return {}


def add_company(company_data: dict) -> dict:
    return {}