"""Local registry adapter (no remote)."""

from __future__ import annotations

from hiri_bridge.devices.types import Device


class LocalAdapter:
    name = "local"

    def list_remote(self) -> list[Device]:
        return []

    def push_state(self, device: Device) -> None:
        return None
