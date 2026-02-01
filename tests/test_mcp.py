"""
Tests for MCP schema and adapter functionality.
"""
import pytest
from datetime import datetime
from src.mcp.schema_mcp import (
    Source,
    ProvenanceBreakdown,
    Provenance,
    MatchedSpan,
    ToolSpec,
    MCPPayload,
)
from src.mcp.adapter import build_mcp_payload, _sha256_hex


class TestSchema:
    """Test MCP schema models."""

    def test_source_minimal(self):
        """Test Source with minimal required fields."""
        source = Source(drhash="abc123")
        assert source.drhash == "abc123"
        assert source.url is None
        assert source.canonicalize_version is None

    def test_source_full(self):
        """Test Source with all fields."""
        source = Source(
            url="https://example.com",
            canonicalize_version="v1.0",
            drhash="abc123",
            extra={"key": "value"},
        )
        assert str(source.url) == "https://example.com/"
        assert source.canonicalize_version == "v1.0"
        assert source.drhash == "abc123"
        assert source.extra == {"key": "value"}

    def test_provenance_breakdown_valid(self):
        """Test ProvenanceBreakdown with valid values."""
        pb = ProvenanceBreakdown(
            match_base=0.8,
            main_content_bonus=0.1,
            integrity_adjust=0.05,
            multisource_bonus=0.02,
            authority_boost=0.03,
            final=0.9,
        )
        assert pb.match_base == 0.8
        assert pb.final == 0.9

    def test_provenance_breakdown_boundary(self):
        """Test ProvenanceBreakdown boundary values."""
        pb = ProvenanceBreakdown(
            match_base=0.0,
            main_content_bonus=0.995,
            integrity_adjust=-1.0,
            multisource_bonus=0.0,
            authority_boost=0.995,
            final=0.995,
        )
        assert pb.match_base == 0.0
        assert pb.main_content_bonus == 0.995
        assert pb.integrity_adjust == -1.0

    def test_matched_span_minimal(self):
        """Test MatchedSpan with minimal fields."""
        span = MatchedSpan(text="example text", start=0, end=12)
        assert span.text == "example text"
        assert span.start == 0
        assert span.end == 12
        assert span.drhash is None
        assert span.main_content_match is False

    def test_matched_span_full(self):
        """Test MatchedSpan with all fields."""
        span = MatchedSpan(
            text="example",
            start=10,
            end=17,
            drhash="hash123",
            context="full context",
            source_url="https://source.com",
            main_content_match=True,
        )
        assert span.text == "example"
        assert span.drhash == "hash123"
        assert span.main_content_match is True

    def test_tool_spec(self):
        """Test ToolSpec."""
        tool = ToolSpec(kind="api", url="https://api.example.com", desc="API endpoint")
        assert tool.kind == "api"
        assert tool.url == "https://api.example.com"
        assert tool.desc == "API endpoint"

    def test_mcp_payload_minimal(self):
        """Test MCPPayload with minimal required fields."""
        source = Source(drhash="hash123")
        pb = ProvenanceBreakdown(
            match_base=0.8,
            main_content_bonus=0.1,
            integrity_adjust=0.0,
            multisource_bonus=0.0,
            authority_boost=0.0,
            final=0.9,
        )
        prov = Provenance(provenanceConfidence=0.9, provenance_breakdown=pb)
        
        payload = MCPPayload(
            source=source,
            canonical_text="Example canonical text",
            provenance=prov,
        )
        
        assert payload.mcp_version == "1.0"
        assert payload.canonical_text == "Example canonical text"
        assert payload.provenance.provenanceConfidence == 0.9
        assert len(payload.matched_spans) == 0
        assert payload.tools == {}


class TestAdapter:
    """Test MCP adapter functions."""

    def test_sha256_hex(self):
        """Test SHA256 hashing function."""
        result = _sha256_hex("test")
        assert len(result) == 64
        assert result == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

    def test_build_mcp_payload_minimal(self):
        """Test building MCP payload with minimal data."""
        canonical = {
            "canonical_text": "Test text",
            "source_url": "https://example.com",
        }
        provenance = {
            "provenanceConfidence": 0.85,
            "provenance_breakdown": {
                "match_base": 0.8,
                "main_content_bonus": 0.05,
                "integrity_adjust": 0.0,
                "multisource_bonus": 0.0,
                "authority_boost": 0.0,
                "final": 0.85,
            },
        }
        
        result = build_mcp_payload(canonical, provenance)
        
        assert result["mcp_version"] == "1.0"
        assert result["canonical_text"] == "Test text"
        assert result["provenance"]["provenanceConfidence"] == 0.85
        assert "drhash" in result["source"]
        assert len(result["matched_spans"]) == 0

    def test_build_mcp_payload_with_matched_spans(self):
        """Test building MCP payload with matched spans."""
        canonical = {
            "canonical_text": "Test text with spans",
            "drhash": "test_hash",
        }
        provenance = {
            "provenanceConfidence": 0.9,
            "provenance_breakdown": {
                "match_base": 0.85,
                "main_content_bonus": 0.05,
                "integrity_adjust": 0.0,
                "multisource_bonus": 0.0,
                "authority_boost": 0.0,
                "final": 0.9,
            },
        }
        matched_spans = [
            {
                "text": "Test",
                "start": 0,
                "end": 4,
                "main_content_match": True,
            }
        ]
        
        result = build_mcp_payload(canonical, provenance, matched_spans=matched_spans)
        
        assert len(result["matched_spans"]) == 1
        assert result["matched_spans"][0]["text"] == "Test"
        assert result["matched_spans"][0]["start"] == 0
        assert result["matched_spans"][0]["end"] == 4

    def test_build_mcp_payload_with_tools(self):
        """Test building MCP payload with tools."""
        canonical = {
            "canonical_text": "Test",
            "drhash": "hash123",
        }
        provenance = {
            "provenanceConfidence": 0.9,
            "provenance_breakdown": {
                "match_base": 0.9,
                "main_content_bonus": 0.0,
                "integrity_adjust": 0.0,
                "multisource_bonus": 0.0,
                "authority_boost": 0.0,
                "final": 0.9,
            },
        }
        tools = {
            "verifier": {
                "kind": "api",
                "url": "https://verifier.example.com",
                "desc": "Verification API",
            }
        }
        
        result = build_mcp_payload(canonical, provenance, tools=tools)
        
        assert "verifier" in result["tools"]
        assert result["tools"]["verifier"]["kind"] == "api"
        assert result["tools"]["verifier"]["url"] == "https://verifier.example.com"

    def test_build_mcp_payload_auto_drhash(self):
        """Test that drhash is auto-generated if missing."""
        canonical = {
            "canonical_text": "Test text",
        }
        provenance = {
            "provenanceConfidence": 0.8,
            "provenance_breakdown": {
                "match_base": 0.8,
                "main_content_bonus": 0.0,
                "integrity_adjust": 0.0,
                "multisource_bonus": 0.0,
                "authority_boost": 0.0,
                "final": 0.8,
            },
        }
        
        result = build_mcp_payload(canonical, provenance)
        
        assert "drhash" in result["source"]
        expected_hash = _sha256_hex("Test text")
        assert result["source"]["drhash"] == expected_hash
