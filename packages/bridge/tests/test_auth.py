from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


def test_auth_optional_when_unset(monkeypatch):
    monkeypatch.delenv("HIRI_API_TOKEN", raising=False)
    # re-import app pieces
    from hiri_bridge.auth import api_token

    assert api_token() == ""


def test_post_protected_when_token_set(monkeypatch, tmp_path):
    monkeypatch.setenv("HIRI_API_TOKEN", "secret-test-token")
    # fresh app module would need reload; test middleware logic via client after env
    import importlib

    import hiri_bridge.api as api_mod

    importlib.reload(api_mod)
    client = TestClient(api_mod.app)
    # GET open
    r = client.get("/health")
    assert r.status_code == 200
    # POST without token
    r = client.post("/devices/seed")
    assert r.status_code == 401
    # POST with token
    r = client.post(
        "/devices/seed",
        headers={"Authorization": "Bearer secret-test-token"},
    )
    assert r.status_code == 200
    monkeypatch.delenv("HIRI_API_TOKEN", raising=False)
    importlib.reload(api_mod)
