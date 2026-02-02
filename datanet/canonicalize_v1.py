"""
Stub module for HTML canonicalization.
This will be implemented later.
"""
import hashlib


def canonicalize_html(html):
    """
    Canonicalize HTML content.
    
    Args:
        html: HTML string to canonicalize
        
    Returns:
        dict with drhash and canonical_text
    """
    # Simple stub implementation
    text = html.replace("<html>", "").replace("</html>", "").replace("<body>", "").replace("</body>", "").replace("<p>", "").replace("</p>", "").strip()
    drhash = hashlib.sha256(text.encode()).hexdigest()[:16]
    return {
        "drhash": drhash,
        "canonical_text": text
    }
