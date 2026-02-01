"""
Simple server-side handlers for the expanded function calling schema.
These are small, local implementations intended for examples and tests. Replace with real services in production.
"""
import json
from pathlib import Path
from typing import Dict, Any

DATA_ROOT = Path("data")


def fetch_full_mcp(job_id: str) -> Dict[str, Any]:
    """Return full MCP-like payload for a job directory (meta.json + snapshot.html).
    Raises FileNotFoundError if job not found.
    """
    jobdir = DATA_ROOT / job_id
    if not jobdir.exists():
        raise FileNotFoundError(f"job not found: {job_id}")
    meta_p = jobdir / "meta.json"
    snapshot_p = jobdir / "snapshot.html"

    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
    snapshot = snapshot_p.read_text(encoding="utf-8") if snapshot_p.exists() else ""

    payload = {
        "job_id": job_id,
        "meta": meta,
        "snapshot": snapshot,
    }
    return payload


def annotate_span(job_id: str, drhash: str, start: int, end: int, note: str) -> Dict[str, Any]:
    """Append an annotation to job_dir/annotations.json (list of annotations).
    Returns the created annotation record.
    """
    jobdir = DATA_ROOT / job_id
    jobdir.mkdir(parents=True, exist_ok=True)
    ann_p = jobdir / "annotations.json"
    anns = []
    if ann_p.exists():
        try:
            anns = json.loads(ann_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            anns = []
    ann = {"drhash": drhash, "start": int(start), "end": int(end), "note": note}
    anns.append(ann)
    ann_p.write_text(json.dumps(anns, ensure_ascii=False, indent=2), encoding="utf-8")
    return ann


def export_result(job_id: str, export_format: str) -> Dict[str, Any]:
    """Export a simple representation of the job (meta + snapshot sample) to data/{job_id}/export.{ext}
    Returns a dict with export path.
    """
    jobdir = DATA_ROOT / job_id
    if not jobdir.exists():
        raise FileNotFoundError(f"job not found: {job_id}")
    meta_p = jobdir / "meta.json"
    snapshot_p = jobdir / "snapshot.html"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
    snapshot = snapshot_p.read_text(encoding="utf-8") if snapshot_p.exists() else ""

    if export_format == "json":
        out = {"meta": meta, "snapshot_sample": snapshot[:1000]}
        ext = "json"
        content = json.dumps(out, ensure_ascii=False, indent=2)
    else:
        ext = "txt"
        content = (meta.get("canonical_text", "")[:1000] or snapshot[:1000])

    out_p = jobdir / f"export.{ext}"
    out_p.write_text(content, encoding="utf-8")
    return {"export_path": str(out_p)}
