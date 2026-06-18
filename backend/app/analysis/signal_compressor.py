"""
Argos — Signal Compressor
A centralized, deterministic layer that compresses raw signals into
compact observations before feeding them to the HypothesisEngine.

Design principles:
- One compressor, one prompt, one style.
- Compression is deterministic first (no LLM calls).
- Summaries are OBSERVATIONS, not conclusions.
  Good: "OpenAI announced an Azure inference agreement covering model serving."
  Bad:  "This locks them into Microsoft's infrastructure for 3 years."
- The HypothesisEngine is the sole owner of strategic interpretation.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Maximum characters of content to use for the compressed observation.
# At ~4 chars/token, 400 chars ≈ 100 tokens per signal.
# 50 signals × 100 tokens = ~5000 tokens for context — safely under 8k.
CONTENT_CHAR_LIMIT = 400


def _extract_first_sentences(text: str, char_limit: int) -> str:
    """Extract the most informative content deterministically.
    
    Strategy:
    1. Strip HTML/markdown artifacts.
    2. Take the first N characters (title-heavy content appears early).
    3. Trim to the last sentence boundary to avoid mid-sentence cutoffs.
    """
    if not text:
        return ""

    # Strip common HTML tags
    clean = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    clean = re.sub(r"\s+", " ", clean).strip()

    if len(clean) <= char_limit:
        return clean

    truncated = clean[:char_limit]
    # Trim to last sentence boundary (. ! ?) to avoid mid-sentence cutoffs
    last_boundary = max(
        truncated.rfind(". "),
        truncated.rfind("! "),
        truncated.rfind("? "),
    )
    if last_boundary > char_limit // 2:
        return truncated[: last_boundary + 1].strip()
    return truncated.strip()


def compress_signal(signal: dict) -> dict:
    """Return a compressed version of a signal for use by HypothesisEngine.
    
    Output fields:
        title       - unchanged
        signal_type - unchanged
        importance  - unchanged
        source      - unchanged
        collected_at- unchanged
        summary     - compressed observation (≤ CONTENT_CHAR_LIMIT chars)
    """
    content = signal.get("content", "") or ""
    title = signal.get("title", "") or ""

    # If there is no content, fall back to title only
    if not content.strip():
        summary = title
    else:
        compressed = _extract_first_sentences(content, CONTENT_CHAR_LIMIT)
        summary = compressed if compressed else title

    return {
        "title": title,
        "signal_type": signal.get("signal_type", "UNKNOWN"),
        "importance": signal.get("importance", 0),
        "source": signal.get("source", ""),
        "collected_at": signal.get("collected_at", ""),
        "summary": summary,
    }


def compress_signals(signals: list[dict]) -> list[dict]:
    """Compress a list of signals. Safe to call on any signal list."""
    return [compress_signal(s) for s in signals]
