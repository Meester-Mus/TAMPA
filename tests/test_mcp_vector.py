import pytest
from pathlib import Path
import json
from datanet import canonicalize_v1

try:
    import faiss  # noqa: F401
    from sentence_transformers import SentenceTransformer  # noqa: F401
except Exception:
    faiss = None

from mcp import vector_search

@pytest.mark.skipif(faiss is None, reason="FAISS or sentence-transformers not installed")
def test_build_and_search(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    jobdir = data_dir / "job1"
    jobdir.mkdir()
    html = "<html><body><p>Hello FAISS world</p></body></html>"
    snapshot = jobdir / "snapshot.html"
    snapshot.write_text(html, encoding="utf-8")
    canonical = canonicalize_v1.canonicalize_html(html)
    meta = {"url": "https://example.com/job1", "drhash": canonical["drhash"], "canonical_text": canonical["canonical_text"]}
    (jobdir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

    res = vector_search.build_index(data_root=str(data_dir), model_name="all-MiniLM-L6-v2", force=True)
    assert res.get("doc_count", 0) == 1

    out = vector_search.search("Hello world", k=1, data_root=str(data_dir))
    assert "results" in out and len(out["results"]) >= 1
    assert out["results"][0]["job_id"] == "job1"
