"""
Simple HTML canonicalizer for TAMPA/Datanet PoC.
Extracts visible text from HTML and computes a sha256 hash (drhash).
"""
import hashlib
import re
from typing import Dict, Any


def canonicalize_html(html: str) -> Dict[str, Any]:
    """
    Extract visible text from HTML (simple tag stripping) and compute drhash.
    
    Args:
        html: HTML content string
    
    Returns:
        Dict with 'canonical_text' and 'drhash' keys
    """
    # Simple tag removal - strip all HTML tags
    text = re.sub(r'<[^>]+>', '', html)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Compute sha256 hash
    drhash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    return {
        "canonical_text": text,
        "drhash": drhash
    }
