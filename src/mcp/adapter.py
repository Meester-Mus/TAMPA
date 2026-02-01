"""
Stub module for MCP adapter functionality.
This module provides functions to build MCP payloads for model consumption.
"""
from typing import Dict, Any, List

def build_mcp_payload(canonical_text: str, provenance: Dict[str, Any], matched_spans: List[Any]) -> Dict[str, Any]:
    """
    Build an MCP (Model Context Protocol) payload from canonical text and provenance data.
    
    Args:
        canonical_text: The canonicalized text content
        provenance: Provenance metadata including confidence scores
        matched_spans: List of matched text spans
        
    Returns:
        MCP payload dictionary
    """
    import hashlib
    drhash = hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()
    
    return {
        "canonical_text": canonical_text,
        "source": {
            "drhash": drhash,
            "provenance": provenance
        },
        "matched_spans": matched_spans
    }
