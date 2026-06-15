"""
Argos — FastAPI Entry Point
REST API with all endpoints for the Argos CI Agent.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.config import API_PORT
from app.database import (
    get_all_companies,
    get_company_by_id,
    add_company,
    deactivate_company,
    get_signals,
    get_all_signals_feed,
    get_reports,
    get_all_reports,
    get_signals_today_count,
    get_high_priority_alert_count,
    get_total_reports_count,
)
from app.discovery.auto_discover import AutoDiscoverer
from app.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)

# ── Configure logging ───────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)


# ── Lifespan ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start scheduler on startup, stop on shutdown."""
    logger.info("🚀 Argos starting up...")
    start_scheduler()
    yield
    logger.info("🛑 Argos shutting down...")
    stop_scheduler()


# ── FastAPI App ─────────────────────────────────────────────

app = FastAPI(
    title="Argos — Competitive Intelligence Agent",
    description="Autonomous system monitoring companies across 8 data sources",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response Models ─────────────────────────────────

class AddCompanyRequest(BaseModel):
    name: str
    website: Optional[str] = None

