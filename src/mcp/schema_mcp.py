from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, timezone


class Source(BaseModel):
    url: Optional[HttpUrl] = None
    canonicalize_version: Optional[str] = None
    drhash: str
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProvenanceBreakdown(BaseModel):
    match_base: float = Field(..., ge=0.0, le=0.995)
    main_content_bonus: float = Field(..., ge=0.0, le=0.995)
    integrity_adjust: float = Field(..., ge=-1.0, le=1.0)
    multisource_bonus: float = Field(..., ge=0.0, le=0.995)
    authority_boost: float = Field(..., ge=0.0, le=0.995)
    final: float = Field(..., ge=0.0, le=0.995)


class Provenance(BaseModel):
    provenanceConfidence: float = Field(..., ge=0.0, le=0.995)
    provenance_breakdown: ProvenanceBreakdown


class MatchedSpan(BaseModel):
    text: str
    start: int
    end: int
    drhash: Optional[str] = None
    context: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    main_content_match: Optional[bool] = False


class ToolSpec(BaseModel):
    kind: str
    url: str
    desc: Optional[str] = None


class MCPPayload(BaseModel):
    mcp_version: str = "1.0"
    source: Source
    canonical_text: str
    canonical_sample: Optional[str] = None
    provenance: Provenance
    matched_spans: List[MatchedSpan] = Field(default_factory=list)
    tools: Optional[Dict[str, ToolSpec]] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
