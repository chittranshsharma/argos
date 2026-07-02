import re
import logging
from urllib.parse import urlparse
from app.database import get_all_companies

logger = logging.getLogger(__name__)

ACTION_VERBS = [
    "launches",
    "announces",
    "acquires",
    "raises",
    "partners",
    "ships",
    "unveils"
]

class AttributionEngine:
    """
    Deterministic Attribution Engine for tagging scraped signals.
    Uses additive scoring and direct evidence multipliers to assign
    confidence and categories.
    """

    def __init__(self, portfolio_companies: list[str] = None):
        """Initialize engine, caching the list of portfolio company names."""
        if portfolio_companies is not None:
            self.portfolio_companies = portfolio_companies
        else:
            try:
                companies = get_all_companies()
                self.portfolio_companies = [c["name"] for c in companies if c.get("name")]
            except Exception as e:
                logger.error(f"Failed to load portfolio companies in AttributionEngine: {e}")
                self.portfolio_companies = []

    def calculate_attribution(
        self,
        title: str,
        description: str,
        url: str,
        company_name: str,
        website: str = None
    ) -> dict:
        """
        Evaluate a signal against a target company name and return attribution metadata.
        """
        title = title or ""
        description = description or ""
        url = url or ""
        
        normalized_title = title.lower()
        normalized_desc = description.lower()
        normalized_url = url.lower()
        normalized_target = company_name.lower()
        
        score = 0.0
        reasons = []
        
        # 1. Official Domain Match (+0.60)
        has_domain_match = False
        if website:
            try:
                # Extract clean domain name (e.g. openai.com from https://openai.com)
                domain = urlparse(website).netloc.replace("www.", "").lower()
                article_domain = urlparse(url).netloc.replace("www.", "").lower()
                if domain and domain in article_domain:
                    score += 0.60
                    reasons.append("official_domain_match")
                    has_domain_match = True
            except Exception as e:
                logger.warning(f"Error parsing domains for attribution: {e}")
                
        # Helper word boundary regex matching
        target_pattern = r"\b" + re.escape(normalized_target) + r"\b"
        in_title = bool(re.search(target_pattern, normalized_title))
        
        # 2. Company Name in Title (+0.25)
        if in_title:
            score += 0.25
            reasons.append("company_in_title")
            
        # 3. Company Name in URL path (+0.20)
        # Verify it matches as path/query token, not part of domain if possible
        if normalized_target in normalized_url:
            # Prevent double-counting if domain matched it
            if not (has_domain_match and domain and normalized_target in domain):
                score += 0.20
                reasons.append("company_in_url")
                
        # 4. Company Name in Description Only (+0.10)
        in_desc = bool(re.search(target_pattern, normalized_desc))
        if in_desc and not in_title:
            score += 0.10
            reasons.append("company_in_description")
            
        # 5. Primary Company Mention (+0.15)
        # Triggered if company name is in the first 30% of characters in the title
        # OR if it appears in the title before any action verbs (launches, announces, etc.)
        is_primary = False
        if in_title:
            # Check 30% threshold
            char_index = normalized_title.find(normalized_target)
            if char_index >= 0 and (char_index / len(normalized_title)) <= 0.30:
                is_primary = True
                reasons.append("primary_company_mention_first_30pct")
                
            # Check action verbs
            if not is_primary:
                for verb in ACTION_VERBS:
                    pattern = rf"\b{re.escape(normalized_target)}\b.*?\b{verb}\b"
                    if re.search(pattern, normalized_title):
                        is_primary = True
                        reasons.append(f"primary_company_mention_before_{verb}")
                        break
                        
        if is_primary:
            score += 0.15
            
        # Bounding raw score
        confidence = min(score, 1.0)
        
        # Direct Evidence Multiplier (0.8x if no official domain match)
        if not has_domain_match:
            confidence *= 0.8
            
        # Classify attribution type
        if confidence >= 0.80:
            attribution_type = "DIRECT"
        elif confidence >= 0.50:
            attribution_type = "PARTNER"
        elif confidence >= 0.20:
            attribution_type = "INDUSTRY"
        else:
            attribution_type = "NOISE"
            
        # 6. Co-occurrence Logging (matched_companies)
        matched_companies = []
        for name in self.portfolio_companies:
            name_pat = r"\b" + re.escape(name.lower()) + r"\b"
            if re.search(name_pat, normalized_title) or re.search(name_pat, normalized_desc):
                matched_companies.append(name)
                
        # Primary company key assignment
        primary_company = company_name if is_primary else None
        
        return {
            "attribution_confidence": round(confidence, 2),
            "attribution_type": attribution_type,
            "attribution_reason": reasons,
            "attribution_version": "v1",
            "matched_companies": matched_companies,
            "primary_company": primary_company
        }
