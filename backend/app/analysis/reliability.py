"""
Argos — Source Reliability & Confidence Scoring
Tiered scoring system for intelligence sources.
"""

from urllib.parse import urlparse

# Tier 1: Primary Sources (1.00)
TIER_1_DOMAINS = {
    "sec.gov", "investor.apple.com", "ir.tesla.com", "about.google" # Will be expanded to match known IR patterns
}

# Tier 2: Major PR Wires (0.95)
TIER_2_DOMAINS = {
    "businesswire.com", "globenewswire.com", "prnewswire.com", "accesswire.com"
}

# Tier 3: Top-tier Financial/Business News (0.90)
TIER_3_DOMAINS = {
    "reuters.com", "bloomberg.com", "wsj.com", "ft.com", "cnbc.com", "forbes.com"
}

# Tier 4: Major Tech/Industry News (0.85)
TIER_4_DOMAINS = {
    "techcrunch.com", "theinformation.com", "venturebeat.com", "wired.com", "techmeme.com"
}

# Tier 5: General Industry/Tech Blogs (0.75)
TIER_5_DOMAINS = {
    "siliconangle.com", "geekwire.com", "techspot.com", "kdnuggets.com", "cointelegraph.com", "ycombinator.com"
}

def get_source_score(url: str) -> float:
    """Returns the reliability score for a given source URL."""
    if not url:
        return 0.45
        
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
            
        # Exact match checks
        if domain in TIER_1_DOMAINS: return 1.00
        if domain in TIER_2_DOMAINS: return 0.95
        if domain in TIER_3_DOMAINS: return 0.90
        if domain in TIER_4_DOMAINS: return 0.85
        if domain in TIER_5_DOMAINS: return 0.75
        
        # Subdomain match checks (e.g. news.ycombinator.com)
        for t2 in TIER_2_DOMAINS:
            if domain.endswith("." + t2): return 0.95
        for t3 in TIER_3_DOMAINS:
            if domain.endswith("." + t3): return 0.90
        for t4 in TIER_4_DOMAINS:
            if domain.endswith("." + t4): return 0.85
            
        # Pattern match for Investor Relations / Official PR
        if "investor." in domain or "ir." in domain or "press." in domain:
            return 1.00
            
    except Exception:
        pass
        
    return 0.45 # Unknown source

def calculate_weighted_confidence(source_urls: list[str], source_count: int, evidence_score: float, extraction_score: float) -> tuple[float, dict]:
    """
    Calculates weighted confidence based on source quality, evidence quality, and extraction quality.
    Formula: confidence = source_score * 0.4 + evidence_score * 0.3 + extraction_score * 0.3
    Returns (confidence, reasoning_dict).
    """
    # Use the highest scoring source if multiple exist
    best_source_score = 0.45
    for url in source_urls:
        score = get_source_score(url)
        if score > best_source_score:
            best_source_score = score
            
    # Boost evidence score if we have cross-source confirmation
    cross_source_confirmed = source_count > 1
    if cross_source_confirmed:
        evidence_score = min(evidence_score + 0.15, 1.0)
        
    # Calculate final weighted confidence
    confidence = (best_source_score * 0.4) + (evidence_score * 0.3) + (extraction_score * 0.3)
    
    # Cap at 0.99
    confidence = round(min(confidence, 0.99), 2)
    
    # Determine review status
    # Require review if confidence < 0.70, or if it relies entirely on a single unknown source (0.45)
    needs_review = confidence < 0.70 or (source_count == 1 and best_source_score <= 0.45)
    review_status = "pending" if needs_review else "auto_approved"
    
    reasoning = {
        "source_score": best_source_score,
        "source_count": source_count,
        "evidence_score": round(evidence_score, 2),
        "extraction_score": round(extraction_score, 2),
        "cross_source_confirmed": cross_source_confirmed,
        "review_status": review_status
    }
    
    return confidence, reasoning
