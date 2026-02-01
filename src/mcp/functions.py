"""
Server-side implementations for functions the model can call.
These are minimal stubs: replace with real integrations (search index, ticketing, etc.) as needed.
"""
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any

DATA_ROOT = Path("data")
REVIEW_ROOT = DATA_ROOT / "human_reviews"
REVIEW_ROOT.mkdir(parents=True, exist_ok=True)

def compute_drhash(canonical_text: str) -> Dict[str, str]:
    """Return SHA256 hex digest for canonical_text."""
    dr = hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()
    return {"drhash": dr}

def search_documents(query: str, k: int = 3) -> Dict[str, Any]:
    """
    Very small local search stub: scans data/ directory for files named meta.json and returns top-k matches by simple substring scoring.
    In production, replace with vector DB / retrieval service.
    """
    results: List[Dict[str, Any]] = []
    for p in DATA_ROOT.rglob("meta.json"):
        try:
            meta = json.loads(p.read_text(encoding="utf-8"))
            snapshot_file = p.parent / "snapshot.html"
            sample = snapshot_file.read_text(encoding="utf-8")[:200] if snapshot_file.exists() else ""
            score = 1.0 if query.lower() in json.dumps(meta).lower() or query.lower() in sample.lower() else 0.0
            results.append({
                "job_id": p.parent.name,
                "url": meta.get("url"),
                "canonical_sample": sample,
                "score": score,
                "drhash": meta.get("drhash")
            })
        except Exception:
            continue
    # sort by score desc and return top k
    results = sorted(results, key=lambda r: r.get("score", 0.0), reverse=True)[:k]
    return {"results": results}

def request_human_review(reason: str, job_id: str = None, meta: Dict[str, Any] = None) -> Dict[str, str]:
    """
    Create a small JSON file representing a human review ticket and return a fake ticket URL.
    """
    ticket = {
        "job_id": job_id,
        "reason": reason,
        "meta": meta or {},
    }
    # simple unique filename
    idx = len(list(REVIEW_ROOT.glob("ticket-*.json"))) + 1
    fname = REVIEW_ROOT / f"ticket-{idx:04d}.json"
    fname.write_text(json.dumps(ticket, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ticket_url": f"/internal/reviews/{fname.name}"}
