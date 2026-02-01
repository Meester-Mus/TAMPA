"""
Simple canonicalization module for HTML content.
This provides the canonicalize_html function that is referenced in tests.
"""
import hashlib
from typing import Dict, Any


def canonicalize_html(html: str) -> Dict[str, Any]:
    """
    Canonicalize HTML content.
    
    Args:
        html: HTML string to canonicalize
        
    Returns:
        Dictionary with canonical_text and drhash
    """
    # Simple canonicalization: strip tags and normalize whitespace
    # In a real implementation, this would be more sophisticated
    import re
    
    # Remove script and style elements
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Compute hash
    drhash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    return {
        "canonical_text": text,
        "drhash": drhash
    }
