from pathlib import Path
import json
from mcp import fncall_handlers
from datanet import canonicalize_v1


def test_fetch_and_annotate(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    jobdir = data_dir / "job1"
    jobdir.mkdir()
    html = "<html><body><p>Alpha beta gamma</p></body></html>"
    snapshot = jobdir / "snapshot.html"
    snapshot.write_text(html, encoding="utf-8")
    canonical = canonicalize_v1.canonicalize_html(html)
    meta = {"url": "https://example.com/job1", "drhash": canonical["drhash"], "canonical_text": canonical["canonical_text"]}
    (jobdir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

    # Use pytest's monkeypatch fixture to modify DATA_ROOT
    import mcp.fncall_handlers as fh
    monkeypatch.setattr(fh, "DATA_ROOT", data_dir)

    payload = fncall_handlers.fetch_full_mcp("job1")
    assert payload["job_id"] == "job1"
    assert "meta" in payload and payload["meta"]["drhash"] == canonical["drhash"]

    ann = fncall_handlers.annotate_span("job1", canonical["drhash"], 0, 5, "label:alpha")
    assert ann["note"] == "label:alpha"

    exported = fncall_handlers.export_result("job1", "json")
    assert exported.get("export_path")
