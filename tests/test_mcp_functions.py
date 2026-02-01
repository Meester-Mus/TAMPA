from mcp.functions import compute_drhash, request_human_review
from datanet import canonicalize_v1
import json
import os

def test_compute_drhash_matches_canonicalizer():
    html = "<html><body><p>Z</p></body></html>"
    canonical = canonicalize_v1.canonicalize_html(html)
    res = compute_drhash(canonical["canonical_text"])
    assert res["drhash"] == canonical["drhash"]

def test_request_human_review_creates_ticket(tmp_path, monkeypatch):
    # point DATA_ROOT to tmpdir by monkeypatching environment / Path optionally
    # Simpler: call and assert returned structure contains ticket_url
    r = request_human_review(reason="test", job_id="jid-1", meta={"a":1})
    assert "ticket_url" in r
