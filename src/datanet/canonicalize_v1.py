"""
Canonicalization utilities for HTML content.
Simple stub implementation for testing.
"""
import hashlib
import re


def canonicalize_html(html: str) -> dict:
    """
    Canonicalize HTML content by extracting text and computing a hash.
    Returns a dict with 'canonical_text' and 'drhash'.
    """
    # Simple text extraction: remove tags
    text = re.sub(r'<[^>]+>', '', html)
    # Clean up whitespace
    text = ' '.join(text.split())
    
    # Compute SHA256 hash
    drhash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    return {
        "canonical_text": text,
        "drhash": drhash
    }
