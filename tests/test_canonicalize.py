"""
Tests for canonicalize_v1 module
"""

import pytest
import json
from src.datanet.canonicalize_v1 import (
    canonicalize_value,
    canonicalize_json,
    verify_canonicalization,
    compute_canonical_hash
)


def test_canonicalize_simple_dict():
    """Test canonicalization of simple dictionary."""
    data = {"z": 1, "a": 2, "m": 3}
    result = canonicalize_json(data)
    expected = '{"a":2,"m":3,"z":1}'
    assert result == expected


def test_canonicalize_nested_dict():
    """Test canonicalization of nested dictionary."""
    data = {
        "outer": {
            "z": "last",
            "a": "first"
        },
        "alpha": 1
    }
    result = canonicalize_json(data)
    # Keys should be sorted at all levels
    assert '"alpha":1' in result
    assert '"outer":' in result
    assert '"a":"first"' in result
    assert '"z":"last"' in result


def test_canonicalize_list():
    """Test that lists preserve order."""
    data = {"items": [3, 1, 2]}
    result = canonicalize_json(data)
    expected = '{"items":[3,1,2]}'
    assert result == expected


def test_canonicalize_mixed_types():
    """Test canonicalization with mixed types."""
    data = {
        "string": "value",
        "number": 42,
        "float": 3.14,
        "bool": True,
        "null": None,
        "array": [1, 2, 3],
        "object": {"key": "val"}
    }
    result = canonicalize_json(data)
    parsed = json.loads(result)
    
    assert parsed["string"] == "value"
    assert parsed["number"] == 42
    assert parsed["float"] == 3.14
    assert parsed["bool"] is True
    assert parsed["null"] is None
    assert parsed["array"] == [1, 2, 3]
    assert parsed["object"] == {"key": "val"}


def test_canonicalize_from_json_string():
    """Test canonicalization from JSON string input."""
    json_str = '{"z": 1, "a": 2}'
    result = canonicalize_json(json_str)
    expected = '{"a":2,"z":1}'
    assert result == expected


def test_verify_canonicalization_valid():
    """Test verification of valid canonicalization."""
    original = '{"b": 2, "a": 1}'
    canonical = '{"a": 1, "b": 2}'
    assert verify_canonicalization(original, canonical) is True


def test_verify_canonicalization_invalid():
    """Test verification catches different data."""
    original = '{"a": 1, "b": 2}'
    canonical = '{"a": 1, "b": 3}'
    assert verify_canonicalization(original, canonical) is False


def test_compute_canonical_hash():
    """Test canonical hash computation."""
    data1 = {"z": 1, "a": 2}
    data2 = {"a": 2, "z": 1}  # Same data, different order
    
    hash1 = compute_canonical_hash(data1)
    hash2 = compute_canonical_hash(data2)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex digest length


def test_compute_canonical_hash_different():
    """Test that different data produces different hashes."""
    data1 = {"a": 1, "b": 2}
    data2 = {"a": 1, "b": 3}
    
    hash1 = compute_canonical_hash(data1)
    hash2 = compute_canonical_hash(data2)
    
    assert hash1 != hash2


def test_canonicalize_empty_dict():
    """Test canonicalization of empty dictionary."""
    data = {}
    result = canonicalize_json(data)
    assert result == '{}'


def test_canonicalize_empty_list():
    """Test canonicalization of empty list."""
    data = {"items": []}
    result = canonicalize_json(data)
    assert result == '{"items":[]}'


def test_canonicalize_unicode():
    """Test canonicalization with Unicode characters."""
    data = {"message": "Hello 世界"}
    result = canonicalize_json(data)
    assert "世界" in result


def test_canonicalize_idempotent():
    """Test that canonicalization is idempotent."""
    data = {"z": 1, "a": 2, "m": 3}
    result1 = canonicalize_json(data)
    result2 = canonicalize_json(result1)
    assert result1 == result2
