# Updated instrumented functions with optional API-key gating and argument validation.
import hashlib
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from mcp import metrics
from mcp import auth

DATA_ROOT = Path("data")
REVIEW_ROOT = DATA_ROOT / "human_reviews"
REVIEW_ROOT.mkdir(parents=True, exist_ok=True)

try:
    from mcp import searcher
except Exception:
    searcher = None  # type: ignore


def _require_api_key_or_raise(api_key: Optional[str]) -> None:
    valid = auth.validate_api_key(api_key)
    if not valid:
        metrics.incr_validation_failure()
        # raise PermissionError so callers can map to 401/403 as needed
        raise PermissionError("Invalid or missing API key")


def compute_drhash(canonical_text: str, api_key: Optional[str] = None) -> Dict[str, str]:
    # Authorize if auth enabled
    if auth.is_auth_enabled():
        _require_api_key_or_raise(api_key)
    metrics.incr_function_call('compute_drhash')
    dr = hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()
    return {"drhash": dr}


def search_documents(query: str, k: int = 3, api_key: Optional[str] = None) -> Dict[str, Any]:
    if auth.is_auth_enabled():
        _require_api_key_or_raise(api_key)
    # Validate inputs (small guard)
    auth.validate_function_args({"query": query, "k": k}, allowed_keys=["query", "k"], max_total_size=10_000)
    metrics.incr_function_call('search_documents')
    start = time.time()
    # Prefer production searcher
    try:
        if searcher is not None:
            try:
                out = searcher.search_documents(query, k=k, data_root=str(DATA_ROOT))
                elapsed = time.time() - start
                metrics.observe_search_latency(elapsed)
                # update doc count gauge if index info available
                try:
                    import joblib
                    idx = Path(DATA_ROOT) / 'mcp_index.joblib'
                    if idx.exists():
                        data = joblib.load(str(idx))
                        docs = data.get('docs', [])
                        metrics.set_index_doc_count(len(docs))
                except Exception:
                    pass
                return out
            except Exception:
                pass
    except Exception:
        pass

    # Fallback: simple substring scoring
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
                "drhash": meta.get("drhash"),
            })
        except Exception:
            continue
    results = sorted(results, key=lambda r: r.get("score", 0.0), reverse=True)[:k]
    elapsed = time.time() - start
    metrics.observe_search_latency(elapsed)
    return {"results": results}


def request_human_review(reason: str, job_id: str = None, meta: Dict[str, Any] = None, api_key: Optional[str] = None) -> Dict[str, str]:
    if auth.is_auth_enabled():
        _require_api_key_or_raise(api_key)
    # Validate args
    auth.validate_function_args({"reason": reason, "job_id": job_id, "meta": meta or {}}, allowed_keys=["reason", "job_id", "meta"], max_total_size=50_000)
    metrics.incr_function_call('request_human_review')
    ticket = {
        "job_id": job_id,
        "reason": reason,
        "meta": meta or {},
    }
    idx = len(list(REVIEW_ROOT.glob("ticket-*.json"))) + 1
    fname = REVIEW_ROOT / f"ticket-{idx:04d}.json"
    fname.write_text(json.dumps(ticket, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ticket_url": f"/internal/reviews/{fname.name}"}
