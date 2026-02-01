import hashlib
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from mcp import metrics

DATA_ROOT = Path("data")
REVIEW_ROOT = DATA_ROOT / "human_reviews"
REVIEW_ROOT.mkdir(parents=True, exist_ok=True)

try:
    from mcp import searcher
except Exception:
    searcher = None  # type: ignore


def compute_drhash(canonical_text: str) -> Dict[str, str]:
    metrics.incr_function_call('compute_drhash')
    dr = hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()
    return {"drhash": dr}


def search_documents(query: str, k: int = 3) -> Dict[str, Any]:
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
                        # best-effort: load docs length (fast because small)
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


def request_human_review(reason: str, job_id: str = None, meta: Dict[str, Any] = None) -> Dict[str, str]:
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
