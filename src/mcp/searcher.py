from pathlib import Path
import json
from typing import List, Dict, Any, Optional

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    import joblib
except Exception:
    TfidfVectorizer = None  # type: ignore
    linear_kernel = None
    joblib = None  # type: ignore

INDEX_FILENAME = "mcp_index.joblib"


def _collect_documents(data_root: Path) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    if not data_root.exists():
        return docs
    for d in data_root.iterdir():
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


def build_index(data_root: str = "data", index_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Build a TF-IDF index over documents found under data_root and save it to index_path.
    Returns a dictionary with metadata about the index.
    """
    data_root_p = Path(data_root)
    idx_path = Path(index_path) if index_path else data_root_p / INDEX_FILENAME

    if TfidfVectorizer is None:
        raise RuntimeError("scikit-learn not available; install scikit-learn and joblib to use the searcher")

    docs = _collect_documents(data_root_p)
    corpus = [d["text"] or "" for d in docs]

    vectorizer = TfidfVectorizer(stop_words="english")
    if corpus:
        matrix = vectorizer.fit_transform(corpus)
    else:
        matrix = vectorizer.fit_transform([""])

    # persist
    joblib.dump({"vectorizer": vectorizer, "matrix": matrix, "docs": docs}, str(idx_path))

    return {"index_path": str(idx_path), "doc_count": len(docs)}


def search_documents(query: str, k: int = 3, data_root: str = "data", index_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Search the TF-IDF index for the given query and return top-k results with scores.
    If the index does not exist, raises RuntimeError.
    """
    data_root_p = Path(data_root)
    idx_path = Path(index_path) if index_path else data_root_p / INDEX_FILENAME

    if joblib is None:
        raise RuntimeError("scikit-learn not available; install scikit-learn and joblib to use the searcher")

    if not idx_path.exists():
        raise RuntimeError(f"Index not found at {idx_path}; build it with build_index()")

    data = joblib.load(str(idx_path))
    vectorizer = data["vectorizer"]
    matrix = data["matrix"]
    docs = data["docs"]

    qv = vectorizer.transform([query])
    scores = linear_kernel(qv, matrix).flatten()

    ranked = sorted(
        [
            {"job_id": docs[i]["job_id"], "score": float(scores[i]), "drhash": docs[i].get("drhash"), "url": docs[i].get("url"), "canonical_sample": docs[i].get("canonical_sample")}
            for i in range(len(docs))
        ],
        key=lambda r: r["score"],
        reverse=True,
    )

    return {"results": ranked[:k]}
