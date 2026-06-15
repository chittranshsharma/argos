from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
from pydantic import BaseModel, Field

from app.signals.registry import SignalType, SignalSubtype, SignalStatus

logger = logging.getLogger(__name__)

class RawAgentSignal(BaseModel):
    """The expected output format from an Intelligence Agent."""
    company_id: str
    company_name: str
    signal_type: SignalType
    subtype: Optional[SignalSubtype] = None
    
    # Content
    title: str
    content: str
    url: str
    raw_source_text: Optional[str] = None  # To be split into Sources table
    
    # Metadata
    agent: str
    extraction_model: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    # Time
    occurred_at: Optional[str] = None
    expires_at: Optional[str] = None

class SignalValidator:
    """Validates raw agent signals against the unified schema."""
    
    def validate_and_format(self, raw_data: dict, agent_name: str) -> Optional[RawAgentSignal]:
        """Validates a dictionary output from an agent and ensures it matches the schema."""
        try:
            # Ensure the agent name is tracked
            raw_data["agent"] = agent_name
            
            # Default occurred_at if missing
            if not raw_data.get("occurred_at"):
                raw_data["occurred_at"] = datetime.now(timezone.utc).isoformat()
            
            # Map old 'source' format to signal_type if necessary
            if "source" in raw_data and "signal_type" not in raw_data:
                source_val = raw_data.pop("source").upper()
                try:
                    raw_data["signal_type"] = SignalType(source_val)
                except ValueError:
                    raw_data["signal_type"] = SignalType.NEWS
            
            signal = RawAgentSignal(**raw_data)
            return signal
        except Exception as e:
            logger.error(f"Signal validation failed for agent {agent_name}: {e}\nData: {raw_data}")
            return None