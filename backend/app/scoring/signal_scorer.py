import logging
from app.signals.registry import SignalSubtype

logger = logging.getLogger(__name__)

class SignalScorer:
    """Centralized scorer for signal confidence and importance."""
    
    # Base importance weights for subtypes (0-10)
    IMPORTANCE_WEIGHTS = {
        # Hiring
        SignalSubtype.AI_EXPANSION: 7.5,
        SignalSubtype.GTM_PUSH: 6.5,
        SignalSubtype.REGIONAL_EXPANSION: 6.0,
        SignalSubtype.HIRING_FREEZE: 8.5,
        SignalSubtype.LEADERSHIP_SURGE: 7.0,
        
        # Executives
        SignalSubtype.CEO_APPOINTED: 9.5,
        SignalSubtype.CEO_DEPARTED: 9.5,
        SignalSubtype.CTO_APPOINTED: 8.5,
        SignalSubtype.CFO_DEPARTED: 8.5,
        SignalSubtype.BOARD_CHANGE: 8.0,
        
        # Funding
        SignalSubtype.SEED: 6.0,
        SignalSubtype.SERIES_A: 7.0,
        SignalSubtype.SERIES_B: 8.0,
        SignalSubtype.SERIES_C: 8.5,
        SignalSubtype.IPO: 10.0,
        SignalSubtype.ACQUISITION: 10.0,
        SignalSubtype.DEBT: 6.5,
        
        # GitHub
        SignalSubtype.ENGINEERING_SURGE: 7.0,
        SignalSubtype.RELEASE_ACCELERATION: 6.5,
        SignalSubtype.OPEN_SOURCE_EXPANSION: 6.0,
        SignalSubtype.MAINTENANCE_DECLINE: 7.5,
        
        # Launch
        SignalSubtype.MAJOR_PRODUCT: 8.5,
        SignalSubtype.MAJOR_FEATURE: 7.0,
        SignalSubtype.BETA: 5.5,
        SignalSubtype.INTEGRATION: 5.0,
        SignalSubtype.PRICING_CHANGE: 7.5,
        
        # Partnerships
        SignalSubtype.STRATEGIC_PARTNERSHIP: 8.0,
        SignalSubtype.CLOUD_PARTNERSHIP: 7.5,
        SignalSubtype.AI_PARTNERSHIP: 8.5,
        SignalSubtype.GOVERNMENT_CONTRACT: 9.0,
        
        SignalSubtype.GENERAL_NEWS: 4.0,
    }

    def score_signal(self, signal: dict) -> dict:
        """
    pass