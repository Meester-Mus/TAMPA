"""
Unit tests for strict TAMPA validator.
Tests various validation scenarios including success and failure cases.
"""
import pytest

from src.datanet.validate_tampa import validate_tampa_output, canonicalize_v1, sha256_hex


def test_success_case_with_matching_drhash():
    """Test successful validation with matching drhash and empty matched_spans."""
    html = "<html><body><p>This is a test document.</p></body></html>"
    canonical_text, canonical_sample, drhash = canonicalize_v1(html)
    
    tampa_json = {
        "verdict_hint": "NO_MATCH",
        "matched_spans": [],
        "supporting_sources": [],
        "checks": ["drhash_ok"],
        "provenance_breakdown": {
            "match_base": 0.000,
            "main_content_bonus": 0.000,
            "integrity_adjust": 0.000,
            "multisource_bonus": 0.000,
            "authority_boost": 0.000,
            "final": 0.000
        },
        "provenanceConfidence": 0.000,
        "internal": {
            "drhash": drhash,
            "canonical_sample": canonical_sample,
            "canonicalize_version": "canonicalize_v1"
        },
        "runtime_ms": 100,
        "sigma_trace": [0, 0, 0],
        "tampa_sigma": 0
    }
    
    is_valid, error = validate_tampa_output(tampa_json, canonical_text)
    assert is_valid is True
    assert error is None


def test_drhash_mismatch_rejects():
    """Test that drhash mismatch is rejected."""
    html = "<html><body><p>This is a test document.</p></body></html>"
    canonical_text, canonical_sample, drhash = canonicalize_v1(html)
    
    # Use wrong drhash
    wrong_drhash = "0" * 64
    
    tampa_json = {
        "verdict_hint": "NO_MATCH",
        "matched_spans": [],
        "supporting_sources": [],
        "checks": ["drhash_ok"],
        "provenance_breakdown": {
            "match_base": 0.000,
            "main_content_bonus": 0.000,
            "integrity_adjust": 0.000,
            "multisource_bonus": 0.000,
            "authority_boost": 0.000,
            "final": 0.000
        },
        "provenanceConfidence": 0.000,
        "internal": {
            "drhash": wrong_drhash,
            "canonical_sample": canonical_sample,
            "canonicalize_version": "canonicalize_v1"
        },
        "runtime_ms": 100,
        "sigma_trace": [0, 0, 0],
        "tampa_sigma": 0
    }
    
    is_valid, error = validate_tampa_output(tampa_json, canonical_text)
    assert is_valid is False
    assert "drhash_mismatch" in error


def test_span_text_mismatch_rejects():
    """Test that span text mismatch (indices mismatch) is rejected."""
    html = "<html><body><p>This is a test document.</p></body></html>"
    canonical_text, canonical_sample, drhash = canonicalize_v1(html)
    
    # Create a span with mismatched text
    # canonical_text should be something like "This is a test document."
    # Let's say we want to match "test" but provide wrong indices
    
    tampa_json = {
        "verdict_hint": "JA",
        "matched_spans": [
            {
                "text": "test",  # Correct text
                "start": 0,     # Wrong start (should be around position 10)
                "end": 4,       # Wrong end
                "context": canonical_sample,
                "source_url": None,
                "main_content_match": True,
                "drhash": drhash
            }
        ],
        "supporting_sources": [],
        "checks": ["existence", "exact_match"],
        "provenance_breakdown": {
            "match_base": 0.800,
            "main_content_bonus": 0.100,
            "integrity_adjust": 0.000,
            "multisource_bonus": 0.000,
            "authority_boost": 0.000,
            "final": 0.900
        },
        "provenanceConfidence": 0.900,
        "internal": {
            "drhash": drhash,
            "canonical_sample": canonical_sample,
            "canonicalize_version": "canonicalize_v1"
        },
        "runtime_ms": 150,
        "sigma_trace": [1, 2, 3],
        "tampa_sigma": 10
    }
    
    is_valid, error = validate_tampa_output(tampa_json, canonical_text)
    assert is_valid is False
    assert "span_text_mismatch" in error


def test_provenance_confidence_out_of_range_rejects():
    """Test that provenanceConfidence out of allowed range is rejected."""
    html = "<html><body><p>This is a test document.</p></body></html>"
    canonical_text, canonical_sample, drhash = canonicalize_v1(html)
    
    # Use provenanceConfidence > 0.995 (out of range)
    tampa_json = {
        "verdict_hint": "JA",
        "matched_spans": [],
        "supporting_sources": [],
        "checks": ["existence"],
        "provenance_breakdown": {
            "match_base": 0.999,
            "main_content_bonus": 0.000,
            "integrity_adjust": 0.000,
            "multisource_bonus": 0.000,
            "authority_boost": 0.000,
            "final": 0.999  # Out of range (> 0.995)
        },
        "provenanceConfidence": 0.999,  # Out of range
        "internal": {
            "drhash": drhash,
            "canonical_sample": canonical_sample,
            "canonicalize_version": "canonicalize_v1"
        },
        "runtime_ms": 100,
        "sigma_trace": [0, 0, 0],
        "tampa_sigma": 12
    }
    
    is_valid, error = validate_tampa_output(tampa_json, canonical_text)
    assert is_valid is False
    # Pydantic catches this before our manual check, so either error message is valid
    assert "provenance_out_of_range" in error or "pydantic_validation_failed" in error


def test_success_case_with_matched_span():
    """Test successful validation with a correctly matched span."""
    html = "<html><body><p>This is a test document.</p></body></html>"
    canonical_text, canonical_sample, drhash = canonicalize_v1(html)
    
    # Find the position of "test" in canonical_text
    test_start = canonical_text.find("test")
    if test_start == -1:
        pytest.skip("'test' not found in canonical_text")
    test_end = test_start + 4
    
    tampa_json = {
        "verdict_hint": "JA",
        "matched_spans": [
            {
                "text": "test",
                "start": test_start,
                "end": test_end,
                "context": canonical_sample,
                "source_url": None,
                "main_content_match": True,
                "drhash": drhash
            }
        ],
        "supporting_sources": [],
        "checks": ["existence", "exact_match"],
        "provenance_breakdown": {
            "match_base": 0.800,
            "main_content_bonus": 0.100,
            "integrity_adjust": 0.000,
            "multisource_bonus": 0.000,
            "authority_boost": 0.000,
            "final": 0.900
        },
        "provenanceConfidence": 0.900,
        "internal": {
            "drhash": drhash,
            "canonical_sample": canonical_sample,
            "canonicalize_version": "canonicalize_v1"
        },
        "runtime_ms": 150,
        "sigma_trace": [1, 2, 3],
        "tampa_sigma": 10
    }
    
    is_valid, error = validate_tampa_output(tampa_json, canonical_text)
    assert is_valid is True
    assert error is None


def test_missing_required_field_rejects():
    """Test that missing required top-level field is rejected."""
    html = "<html><body><p>This is a test document.</p></body></html>"
    canonical_text, canonical_sample, drhash = canonicalize_v1(html)
    
    # Missing 'internal' field
    tampa_json = {
        "verdict_hint": "NO_MATCH",
        "matched_spans": [],
        "supporting_sources": [],
        "checks": ["drhash_ok"],
        "provenance_breakdown": {
            "match_base": 0.000,
            "main_content_bonus": 0.000,
            "integrity_adjust": 0.000,
            "multisource_bonus": 0.000,
            "authority_boost": 0.000,
            "final": 0.000
        },
        "provenanceConfidence": 0.000,
        # "internal" is missing
        "runtime_ms": 100,
        "sigma_trace": [0, 0, 0],
        "tampa_sigma": 0
    }
    
    is_valid, error = validate_tampa_output(tampa_json, canonical_text)
    assert is_valid is False
    assert "missing_top_field" in error or "pydantic_validation_failed" in error


def test_provenance_breakdown_mismatch_rejects():
    """Test that provenanceConfidence and provenance_breakdown.final mismatch is rejected."""
    html = "<html><body><p>This is a test document.</p></body></html>"
    canonical_text, canonical_sample, drhash = canonicalize_v1(html)
    
    tampa_json = {
        "verdict_hint": "NO_MATCH",
        "matched_spans": [],
        "supporting_sources": [],
        "checks": ["drhash_ok"],
        "provenance_breakdown": {
            "match_base": 0.000,
            "main_content_bonus": 0.000,
            "integrity_adjust": 0.000,
            "multisource_bonus": 0.000,
            "authority_boost": 0.000,
            "final": 0.100  # Different from provenanceConfidence
        },
        "provenanceConfidence": 0.500,  # Doesn't match final (difference > 0.002)
        "internal": {
            "drhash": drhash,
            "canonical_sample": canonical_sample,
            "canonicalize_version": "canonicalize_v1"
        },
        "runtime_ms": 100,
        "sigma_trace": [0, 0, 0],
        "tampa_sigma": 0
    }
    
    is_valid, error = validate_tampa_output(tampa_json, canonical_text)
    assert is_valid is False
    assert "provenance_mismatch" in error
