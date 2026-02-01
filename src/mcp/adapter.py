"""
Adapter: build and validate MCP payloads from canonicalize_v1 output + extras.

Usage:
  from datanet.canonicalize_v1 import canonicalize_html
  from mcp.adapter import build_mcp_payload

  canonical = canonicalize_html(html)
  mcp = build_mcp_payload(canonical, provenance_dict, matched_spans=[...])
"""
from typing import Dict, Any, List, Optional
import hashlib
from .schema_mcp import MCPPayload, MatchedSpan, Provenance, ProvenanceBreakdown, Source, ToolSpec
import json


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _make_source(canonical: Dict[str, Any]) -> Source:
    return Source(
        url=canonical.get("source_url"),
        canonicalize_version=canonical.get("canonicalize_version", "canonicalize_v1"),
        drhash=canonical.get("drhash") or _sha256_hex(canonical.get("canonical_text", "")),
        extra=canonical.get("meta", {}),
    )


def build_mcp_payload(
    canonical: Dict[str, Any],
    provenance: Dict[str, Any],
    matched_spans: Optional[List[Dict[str, Any]]] = None,
    tools: Optional[Dict[str, Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build, normalize and validate an MCP payload.
    Returns the validated dict (serializable).
    Raises pydantic.ValidationError on invalid payload.
    """
    if matched_spans is None:
        matched_spans = []

    # ensure drhash present in canonical
    if "drhash" not in canonical or not canonical["drhash"]:
        canonical["drhash"] = _sha256_hex(canonical.get("canonical_text", ""))

    # Build provenance objects (caller should pass floats)
    pb = provenance.get("provenance_breakdown", {})
    prov_breakdown = ProvenanceBreakdown(
        match_base=float(pb.get("match_base", 0.0)),
        main_content_bonus=float(pb.get("main_content_bonus", 0.0)),
        integrity_adjust=float(pb.get("integrity_adjust", 0.0)),
        multisource_bonus=float(pb.get("multisource_bonus", 0.0)),
        authority_boost=float(pb.get("authority_boost", 0.0)),
        final=float(pb.get("final", provenance.get("provenanceConfidence", 0.0))),
    )
    prov = Provenance(provenanceConfidence=float(provenance.get("provenanceConfidence", prov_breakdown.final)), provenance_breakdown=prov_breakdown)

    # Map matched spans to models (do not mutate original)
    ms_models = []
    for s in matched_spans:
        ms = MatchedSpan(
            text=s["text"],
            start=int(s["start"]),
            end=int(s["end"]),
            drhash=s.get("drhash", canonical.get("drhash")),
            context=s.get("context"),
            source_url=s.get("source_url"),
            main_content_match=s.get("main_content_match", False),
        )
        ms_models.append(ms)

    # Tools mapping
    tools_models = {}
    if tools:
        for k, v in tools.items():
            tools_models[k] = ToolSpec(kind=v.get("kind", "endpoint"), url=v["url"], desc=v.get("desc"))

    payload = MCPPayload(
        mcp_version="1.0",
        source=_make_source(canonical),
        canonical_text=canonical.get("canonical_text", ""),
        canonical_sample=canonical.get("canonical_sample"),
        provenance=prov,
        matched_spans=ms_models,
        tools=tools_models,
        metadata=metadata or {},
    )

    # Return as dict (serializable)
    return json.loads(payload.model_dump_json())
