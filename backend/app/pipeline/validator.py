from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
from pydantic import BaseModel, Field

from app.signals.registry import SignalType, SignalSubtype, SignalStatus

logger = logging.getLogger(__name__)

class RawAgentSignal(BaseModel):
    pass