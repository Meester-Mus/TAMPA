"""
Canonicalize v1 Reference Implementation

Implements DOS-MGC1-v1 (Diets-ordered serialization) for canonical
representation of data structures.
"""

import json
from typing import Any, Dict, List, Union
from collections import OrderedDict


def canonicalize_value(value: Any) -> Any:
    """
    Canonicalize a single value according to DOS-MGC1-v1 rules.
    
    Rules:
    - Dictionaries: Sort keys alphabetically (Diets-ordered)
    - Lists: Preserve order
    - Numbers: Use consistent representation
    - Strings: UTF-8 encoding
    - Booleans: true/false lowercase
    - Null: null
    """
    if value is None:
        return None
    elif isinstance(value, bool):
        return value
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        return value
    elif isinstance(value, dict):
        # Sort dictionary keys alphabetically (Diets-ordered)
        return OrderedDict(
            (k, canonicalize_value(v))
            for k, v in sorted(value.items())
        )
    elif isinstance(value, (list, tuple)):
        return [canonicalize_value(item) for item in value]
    else:
        raise ValueError(f"Unsupported type for canonicalization: {type(value)}")


def canonicalize_json(data: Union[Dict, List, str]) -> str:
    """
    Canonicalize JSON data to a deterministic string representation.
    
    Args:
        data: Dictionary, list, or JSON string to canonicalize
        
    Returns:
        Canonical JSON string (compact, sorted keys)
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    canonical_data = canonicalize_value(data)
    
    # Serialize with no whitespace, sorted keys, and consistent number format
    return json.dumps(
        canonical_data,
        ensure_ascii=False,
        separators=(',', ':'),
        sort_keys=True
    )


def verify_canonicalization(original: str, canonical: str) -> bool:
    """
    Verify that a canonical representation matches the original data.
    
    Args:
        original: Original JSON string
        canonical: Canonical JSON string
        
    Returns:
        True if canonical representation is valid
    """
    try:
        original_data = json.loads(original)
        canonical_data = json.loads(canonical)
        
        # Re-canonicalize both and compare
        recanon_original = canonicalize_json(original_data)
        recanon_canonical = canonicalize_json(canonical_data)
        
        return recanon_original == recanon_canonical
    except (json.JSONDecodeError, ValueError):
        return False


def compute_canonical_hash(data: Union[Dict, List, str]) -> str:
    """
    Compute a deterministic hash of canonicalized data.
    
    Args:
        data: Data to hash
        
    Returns:
        Hex digest of SHA-256 hash
    """
    import hashlib
    
    canonical = canonicalize_json(data)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
