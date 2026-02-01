"""
Strict validator for TAMPA JSON outputs.
Validates structure via Pydantic and performs additional strict checks.
"""
import hashlib
from typing import Tuple, Any, Dict

from pydantic import ValidationError

from .schema_tampa import TampaOutput


def sha256_hex(text: str) -> str:
    """Compute SHA256 hex digest of text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def canonicalize_v1(html: str) -> Tuple[str, str, str]:
    """
    Simple canonicalization function (placeholder implementation).
    
    ⚠️ WARNING: This is a simplified test implementation with known limitations.
    It uses regex for HTML tag removal which cannot handle all edge cases.
    
    In production, use proper HTML parsing libraries (BeautifulSoup, lxml)
    which correctly handle:
    - Malformed HTML
    - Edge cases like </script > with whitespace
    - Nested tags
    - CDATA sections
    - Comments
    
    For production implementation, see configs/canonicalizer_guidance.txt
    
    Returns:
        Tuple of (canonical_text, canonical_sample, drhash)
    """
    # Simplified implementation for testing only
    import re
    from html import unescape
    import unicodedata
    
    # Remove script and style tags using aggressive regex
    # Known limitation: May not catch malformed tags with unusual whitespace
    # This is acceptable for a test helper but NOT for production use
    text = html
    # Remove everything between script tags (multiple passes to handle nesting)
    for _ in range(3):  # Multiple passes to handle nested/malformed tags
        text = re.sub(r'<script[^>]*>.*?</script[^>]*>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style[^>]*>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Decode HTML entities
    text = unescape(text)
    
    # Normalize Unicode to NFC
    text = unicodedata.normalize('NFC', text)
    
    # Normalize typographic quotes and dashes to ASCII
    replacements = {
        '\u2018': "'", '\u2019': "'",  # Single quotes
        '\u201c': '"', '\u201d': '"',  # Double quotes
        '\u2013': '-', '\u2014': '-',  # En/em dashes
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Collapse consecutive whitespace to single spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Trim ends
    canonical_text = text.strip()
    
    # Create sample (first ~200 chars)
    canonical_sample = canonical_text[:200] if len(canonical_text) > 200 else canonical_text
    
    # Compute drhash
    drhash = sha256_hex(canonical_text)
    
    return canonical_text, canonical_sample, drhash


def validate_tampa_output(tampa_json: Dict[str, Any], canonical_text: str) -> Tuple[bool, str]:
    """
    Strict validator for TAMPA outputs.
    
    Validates:
    1. Structural schema via Pydantic (TampaOutput model)
    2. Required top-level fields exist
    3. provenanceConfidence and provenance_breakdown.final match (within 0.002)
    4. All provenance scores in valid ranges
    5. internal.drhash matches sha256(canonical_text)
    6. Each matched_span validates correctly:
       - Has required fields
       - start/end are integers with start >= 0 and end >= start
       - Substring canonical_text[start:end] == span.text (Python codepoint indexing)
    
    Args:
        tampa_json: Dictionary representing TAMPA JSON output
        canonical_text: The canonical text to validate against
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
        On success: (True, None)
        On failure: (False, "error_code:details")
    """
    # Step 1: Validate structure with Pydantic
    try:
        output = TampaOutput(**tampa_json)
    except ValidationError as e:
        return False, f"pydantic_validation_failed:{str(e)}"
    
    # Step 2: Check required top-level fields (already validated by Pydantic, but explicit check)
    required_fields = ['verdict_hint', 'matched_spans', 'provenanceConfidence', 
                      'provenance_breakdown', 'internal']
    for field in required_fields:
        if field not in tampa_json:
            return False, f"missing_top_field:{field}"
    
    # Step 3: Validate provenanceConfidence and provenance_breakdown.final match
    # Tolerance of 0.002 accounts for floating-point rounding differences
    # while ensuring the values are effectively the same (3 decimal places)
    PROVENANCE_TOLERANCE = 0.002
    pc = output.provenanceConfidence
    pb_final = output.provenance_breakdown.final
    
    # Round both to 3 decimals for comparison
    pc_rounded = round(pc, 3)
    pb_final_rounded = round(pb_final, 3)
    
    if abs(pc_rounded - pb_final_rounded) > PROVENANCE_TOLERANCE:
        return False, f"provenance_mismatch:pc={pc_rounded},pb_final={pb_final_rounded}"
    
    # Step 4: Validate provenance ranges
    if not (0.0 <= pc <= 0.995):
        return False, f"provenance_out_of_range:provenanceConfidence={pc}"
    
    pb = output.provenance_breakdown
    if not (0.0 <= pb.match_base <= 1.0):
        return False, f"provenance_out_of_range:match_base={pb.match_base}"
    if not (0.0 <= pb.main_content_bonus <= 1.0):
        return False, f"provenance_out_of_range:main_content_bonus={pb.main_content_bonus}"
    if not (-1.0 <= pb.integrity_adjust <= 1.0):
        return False, f"provenance_out_of_range:integrity_adjust={pb.integrity_adjust}"
    if not (0.0 <= pb.multisource_bonus <= 1.0):
        return False, f"provenance_out_of_range:multisource_bonus={pb.multisource_bonus}"
    if not (0.0 <= pb.authority_boost <= 1.0):
        return False, f"provenance_out_of_range:authority_boost={pb.authority_boost}"
    if not (0.0 <= pb.final <= 0.995):
        return False, f"provenance_out_of_range:final={pb.final}"
    
    # Step 5: Validate internal.drhash
    expected_drhash = sha256_hex(canonical_text)
    if output.internal.drhash != expected_drhash:
        return False, f"drhash_mismatch:expected={expected_drhash},got={output.internal.drhash}"
    
    # Step 6: Validate each matched_span
    for idx, span in enumerate(output.matched_spans):
        # Check required fields (already validated by Pydantic)
        
        # Check start/end are integers and start >= 0, end >= start
        if not isinstance(span.start, int) or not isinstance(span.end, int):
            return False, f"span_invalid_type_{idx}:start_or_end_not_int"
        
        if span.start < 0:
            return False, f"span_invalid_range_{idx}:start<0"
        
        if span.end < span.start:
            return False, f"span_invalid_range_{idx}:end<start"
        
        # Check substring match
        if span.start > len(canonical_text) or span.end > len(canonical_text):
            return False, f"span_out_of_bounds_{idx}:start={span.start},end={span.end},len={len(canonical_text)}"
        
        actual_substring = canonical_text[span.start:span.end]
        if actual_substring != span.text:
            return False, f"span_text_mismatch_{idx}:expected='{span.text}',got='{actual_substring}'"
        
        # Validate drhash in span matches canonical_text hash
        if span.drhash != expected_drhash:
            return False, f"span_drhash_mismatch_{idx}:expected={expected_drhash},got={span.drhash}"
    
    # All validations passed
    return True, None
