from datanet import canonicalize_v1
from mcp.adapter import build_mcp_payload
import pytest

def test_build_minimal_mcp():
    html = "<html><body><p>Hello MCP</p></body></html>"
    canonical = canonicalize_v1.canonicalize_html(html)
    provenance = {
        "provenanceConfidence": 0.0,
        "provenance_breakdown": {
            "match_base": 0.0,
            "main_content_bonus": 0.0,
            "integrity_adjust": 0.0,
            "multisource_bonus": 0.0,
            "authority_boost": 0.0,
            "final": 0.0,
        },
    }
    mcp = build_mcp_payload(canonical, provenance, matched_spans=[])
    assert mcp["mcp_version"].startswith("1")
    assert "canonical_text" in mcp
    assert mcp["source"]["drhash"] == canonical["drhash"]

def test_invalid_provenance_raises():
    html = "<html><body><p>Bad</p></body></html>"
    canonical = canonicalize_v1.canonicalize_html(html)
    provenance = {
        "provenanceConfidence": 2.0,  # invalid
        "provenance_breakdown": {
            "match_base": 2.0,
            "main_content_bonus": 0.0,
            "integrity_adjust": 0.0,
            "multisource_bonus": 0.0,
            "authority_boost": 0.0,
            "final": 2.0,
        },
    }
    with pytest.raises(Exception):
        build_mcp_payload(canonical, provenance, matched_spans=[])
