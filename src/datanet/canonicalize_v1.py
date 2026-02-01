"""
Minimal canonicalization module for HTML content.
Used to normalize HTML for comparison and generate deterministic hash values (drhash).
"""
import hashlib
from typing import Dict, Any


def canonicalize_html(html: str) -> Dict[str, Any]:
    """
    Canonicalize HTML content and return canonical text with drhash.
    This is a simple implementation that just strips basic tags.
    """
    # Simple canonicalization: remove HTML tags and normalize whitespace
    import re
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Compute drhash
    drhash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    return {
        "canonical_text": text,
        "drhash": drhash
    }
