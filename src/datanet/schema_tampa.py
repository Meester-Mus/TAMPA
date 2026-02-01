"""
Pydantic models for TAMPA output schema validation.
Defines the structural schema for TAMPA JSON outputs.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Span(BaseModel):
    """Matched span in canonical text"""
    text: str = Field(..., description="Exact substring from canonical_text")
    start: int = Field(..., ge=0, description="Start offset (inclusive, codepoint-based)")
    end: int = Field(..., ge=0, description="End offset (exclusive, codepoint-based)")
    context: str = Field(..., description="Surrounding context or full canonical_sample")
    source_url: Optional[str] = Field(None, description="Source URL or null")
    main_content_match: bool = Field(..., description="True if span was in <article>/<main>")
    drhash: str = Field(..., description="SHA256 hash of canonical_text (hex)")


class SupportingSource(BaseModel):
    """Supporting source information"""
    url: str
    authority_score: float = Field(..., ge=0.0, le=1.0)


class ProvenanceBreakdown(BaseModel):
    """Provenance score components"""
    match_base: float = Field(..., ge=0.0, le=1.0, description="Base match score")
    main_content_bonus: float = Field(..., ge=0.0, le=1.0, description="Main content bonus")
    integrity_adjust: float = Field(..., ge=-1.0, le=1.0, description="Integrity adjustment")
    multisource_bonus: float = Field(..., ge=0.0, le=1.0, description="Multi-source bonus")
    authority_boost: float = Field(..., ge=0.0, le=1.0, description="Authority boost")
    final: float = Field(..., ge=0.0, le=0.995, description="Final composed score")


class Internal(BaseModel):
    """Internal metadata"""
    drhash: str = Field(..., description="SHA256 hash of canonical_text (hex)")
    canonical_sample: str = Field(..., description="First ~200 chars of canonical_text")
    canonicalize_version: str = Field(..., description="Canonicalization version identifier")


class TampaOutput(BaseModel):
    """Root TAMPA output schema"""
    verdict_hint: str = Field(..., pattern="^(JA|WEAK_MATCH|NO_MATCH)$", description="Verdict")
    matched_spans: List[Span] = Field(..., description="Array of matched spans")
    supporting_sources: List[SupportingSource] = Field(default_factory=list, description="Supporting sources")
    checks: List[str] = Field(..., description="Validation checks performed")
    provenance_breakdown: ProvenanceBreakdown = Field(..., description="Provenance score breakdown")
    provenanceConfidence: float = Field(..., ge=0.0, le=0.995, description="Final confidence score")
    internal: Internal = Field(..., description="Internal metadata")
    runtime_ms: int = Field(..., description="Runtime in milliseconds")
    sigma_trace: List[int] = Field(..., description="Internal step buckets")
    tampa_sigma: int = Field(..., ge=0, le=12, description="Sigma score (0-12)")
    model_version: Optional[str] = Field(None, description="Model version")
    prompt_version: Optional[str] = Field(None, description="Prompt version")
