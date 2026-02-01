"""
Prototype FAISS-based vector search for MCP documents.

Requires:
- sentence-transformers
- faiss (faiss-cpu)
- numpy
- joblib

This module is intentionally defensive: it raises RuntimeError with instructions if dependencies are missing.
"""
from pathlib import Path
import json
from typing import List, Dict, Any, Optional

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    import joblib
except Exception:
    np = None  # type: ignore
    faiss = None  # type: ignore
    SentenceTransformer = None  # type: ignore
    joblib = None  # type: ignore

INDEX_FILENAME = "faiss_index.faiss"
META_FILENAME = "faiss_index_meta.joblib"


def _collect_documents(data_root: Path) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    if not data_root.exists():
        return docs
    for d in sorted(data_root.iterdir()):
        if not d.is_dir():
            continue
        meta_p = d / "meta.json"
        snap_p = d / "snapshot.html"
        try:
            meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
        except Exception:
            meta = {}
        try:
            snap = snap_p.read_text(encoding="utf-8") if snap_p.exists() else ""
        except Exception:
            snap = ""
        text = meta.get("canonical_text") or snap or meta.get("query", "")
        docs.append({
            "job_id": d.name,
            "text": text,
            "drhash": meta.get("drhash"),
            "url": meta.get("url"),
            "canonical_sample": (text[:200] if text else ""),
        })
    return docs


def build_index(data_root: str = "data", index_path: Optional[str] = None, model_name: str = "all-MiniLM-L6-v2", force: bool = False) -> Dict[str, Any]:
    """
    Build FAISS index and save index + metadata.
    Returns metadata dict with index paths and doc count.
    """
    if SentenceTransformer is None or faiss is None or np is None or joblib is None:
        raise RuntimeError("Missing dependencies. Install: faiss-cpu, sentence-transformers, numpy, joblib")

    data_root_p = Path(data_root)
    idx_path = Path(index_path) if index_path else data_root_p / INDEX_FILENAME
    meta_path = idx_path.with_name(META_FILENAME)

    if idx_path.exists() and not force:
        return {"index_path": str(idx_path), "meta_path": str(meta_path), "doc_count": None, "note": "index exists; use force=True to rebuild"}

    docs = _collect_documents(data_root_p)
    corpus = [d["text"] or "" for d in docs]
    if not corpus:
        # create an empty index to avoid downstream errors
        dim = 384
        index = faiss.IndexFlatIP(dim)
        faiss.write_index(index, str(idx_path))
        joblib.dump({"docs": docs, "model_name": model_name, "dim": dim}, str(meta_path))
        return {"index_path": str(idx_path), "meta_path": str(meta_path), "doc_count": len(docs)}

    # embed
    model = SentenceTransformer(model_name)
    embeddings = model.encode(corpus, show_progress_bar=False, convert_to_numpy=True)
    # normalize to unit vectors for cosine similarity via inner product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    embeddings = embeddings / norms

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    # persist
    faiss.write_index(index, str(idx_path))
    joblib.dump({"docs": docs, "model_name": model_name, "dim": int(dim)}, str(meta_path))

    return {"index_path": str(idx_path), "meta_path": str(meta_path), "doc_count": len(docs)}


def search(query: str, k: int = 3, data_root: str = "data", index_path: Optional[str] = None, meta_path: Optional[str] = None, model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Search the FAISS index for the query and return top-k results with scores.
    """
    if SentenceTransformer is None or faiss is None or np is None or joblib is None:
        raise RuntimeError("Missing dependencies. Install: faiss-cpu, sentence-transformers, numpy, joblib")

    data_root_p = Path(data_root)
    idx_path = Path(index_path) if index_path else data_root_p / INDEX_FILENAME
    meta_p = Path(meta_path) if meta_path else idx_path.with_name(META_FILENAME)

    if not idx_path.exists() or not meta_p.exists():
        raise RuntimeError("Index or metadata not found. Build the index first with build_index()")

    meta = joblib.load(str(meta_p))
    docs = meta.get("docs", [])
    model_used = model_name or meta.get("model_name")

    model = SentenceTransformer(model_used)
    q_emb = model.encode([query], convert_to_numpy=True)
    q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-12)

    index = faiss.read_index(str(idx_path))
    distances, indices = index.search(q_emb.astype("float32"), k)
    res = []
    for score, idx in zip(distances[0].tolist(), indices[0].tolist()):
        if idx < 0 or idx >= len(docs):
            continue
        d = docs[idx]
        res.append({"job_id": d.get("job_id"), "score": float(score), "drhash": d.get("drhash"), "url": d.get("url"), "canonical_sample": d.get("canonical_sample")})
    return {"results": res}
