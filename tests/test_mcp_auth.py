import os
import pytest
from mcp import auth
from mcp import functions

# Test constants
LARGE_META_SIZE = 200_000  # Should exceed max_total_size for request_human_review (50k)

def test_validate_api_key_env(monkeypatch):
    monkeypatch.setenv("MCP_API_KEYS", "k1,k2")
    assert auth.is_auth_enabled()
    assert auth.validate_api_key("k1") is True
    assert auth.validate_api_key("k2") is True
    assert auth.validate_api_key("bad") is False
    assert auth.validate_api_key(None) is False

def test_compute_drhash_requires_key_when_enabled(monkeypatch):
    monkeypatch.setenv("MCP_API_KEYS", "k1")
    # without key should raise
    with pytest.raises(PermissionError):
        functions.compute_drhash("test text", api_key=None)
    # with key ok
    out = functions.compute_drhash("test text", api_key="k1")
    assert "drhash" in out

def test_request_human_review_validation(monkeypatch):
    monkeypatch.delenv("MCP_API_KEYS", raising=False)  # disable auth for this test
    # too-large meta should raise ValueError
    big_meta = {"a": "x" * LARGE_META_SIZE}
    with pytest.raises(ValueError):
        functions.request_human_review("reason", job_id="jid", meta=big_meta)
