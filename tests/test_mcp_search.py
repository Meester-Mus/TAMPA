import json
from mcp import searcher
from datanet import canonicalize_v1


def test_build_and_search(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    jobdir = data_dir / "job1"
    jobdir.mkdir()
    # create snapshot and meta
    html = "<html><body><p>Hello world from MCP</p></body></html>"
    snapshot = jobdir / "snapshot.html"
    snapshot.write_text(html, encoding="utf-8")
    canonical = canonicalize_v1.canonicalize_html(html)
    meta = {"url": "https://example.com/job1", "drhash": canonical["drhash"], "canonical_text": canonical["canonical_text"]}
    (jobdir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

    # build index
    res = searcher.build_index(data_root=str(data_dir))
    assert res["doc_count"] == 1

    out = searcher.search_documents("Hello world", k=1, data_root=str(data_dir))
    assert out and "results" in out and len(out["results"]) == 1
    assert out["results"][0]["job_id"] == "job1"
