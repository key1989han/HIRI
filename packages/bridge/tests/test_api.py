from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from hiri_bridge.api import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_devices_and_command() -> None:
    r = client.get("/devices")
    assert r.status_code == 200
    assert len(r.json()) >= 10
    r2 = client.post("/devices/light.living_main/command", json={"action": "turn_on", "data": {"brightness": 100}})
    assert r2.status_code == 200
    assert r2.json()["state"]["state"] == "on"
