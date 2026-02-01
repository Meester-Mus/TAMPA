"""
Stub canonicalize_v1 module for MCP integration.
This provides a minimal implementation for the example and tests to work.
"""
import hashlib
from typing import Dict, Any


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def canonicalize_html(html: str, source_url: str = None) -> Dict[str, Any]:
    """
    Stub implementation of canonicalize_html.
    In production, this would parse and canonicalize HTML content.
    """
    # Simple extraction - just strip tags for demo purposes
    import re
    text = re.sub(r'<[^>]+>', '', html).strip()
    text = ' '.join(text.split())  # normalize whitespace
    
    drhash = _sha256_hex(text)
    
    return {
        "canonical_text": text,
        "canonical_sample": text[:200] if len(text) > 200 else text,
        "drhash": drhash,
        "canonicalize_version": "canonicalize_v1",
        "source_url": source_url,
        "meta": {},
    }
