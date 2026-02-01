from typing import Tuple, Dict, Any
import hashlib


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def validate_tampa_output(tampa: Dict[str, Any], canonical_text: str) -> Tuple[bool, str]:
    # Basic structural checks (tolerant): must be dict with verdict_hint and matched_spans
    if not isinstance(tampa, dict):
        return False, 'not_object'
    if 'verdict_hint' not in tampa or 'matched_spans' not in tampa:
        return False, 'missing_fields'
    # Check drhash if provided
    internal = tampa.get('internal', {})
    if 'drhash' in internal:
        if internal['drhash'] != _sha256_hex(canonical_text):
            return False, 'drhash_mismatch'
    # Basic sanity
    return True, None
