from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_seed_covers_many_domains(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    stats = reg.stats()
    assert stats["total"] >= 15
    assert "light" in stats["by_domain"]
    assert "sensor" in stats["by_domain"]
    assert "climate" in stats["by_domain"]


def test_command_light(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("light.living_main", "turn_on", {"brightness": 200})
    assert dev.state["state"] == "on"
    assert dev.state["brightness"] == 200


def test_discovery_export(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    disc = export_discovery(reg.list())
    assert len(disc) == reg.stats()["total"]
    assert all("topic" in x and "payload" in x for x in disc)
