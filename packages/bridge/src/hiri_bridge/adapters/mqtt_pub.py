"""Optional MQTT publisher for HA discovery (offline dry-run without paho)."""

from __future__ import annotations

import json
import os
from typing import Any

from hiri_bridge.devices.types import Device
from hiri_bridge.ha.discovery import discovery_payload, discovery_topic, state_topic


class MqttDiscoveryPublisher:
    name = "mqtt"

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self.host = host or os.environ.get("HIRI_MQTT_HOST", "127.0.0.1")
        self.port = int(port or os.environ.get("HIRI_MQTT_PORT", "1883"))
        self.username = username or os.environ.get("HIRI_MQTT_USER") or ""
        self.password = password or os.environ.get("HIRI_MQTT_PASSWORD") or ""

    def status(self) -> str:
        try:
            import paho.mqtt.client  # noqa: F401

            return f"paho ready → {self.host}:{self.port}"
        except ImportError:
            return "offline dry-run (pip install -e '.[mqtt]')"

    def list_remote(self) -> list[Device]:
        return []

    def push_state(self, device: Device) -> None:
        return None

    def build_messages(self, devices: list[Device]) -> list[dict[str, Any]]:
        """Build discovery + state messages without connecting."""
        msgs: list[dict[str, Any]] = []
        for d in devices:
            msgs.append(
                {
                    "topic": discovery_topic(d),
                    "payload": discovery_payload(d),
                    "retain": True,
                    "kind": "discovery",
                }
            )
            msgs.append(
                {
                    "topic": state_topic(d),
                    "payload": d.state if d.state else {"state": "unknown"},
                    "retain": True,
                    "kind": "state",
                }
            )
        msgs.append(
            {
                "topic": "hiri/status",
                "payload": "online",
                "retain": True,
                "kind": "availability",
            }
        )
        return msgs

    def publish(self, devices: list[Device], dry_run: bool = True) -> dict[str, Any]:
        messages = self.build_messages(devices)
        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "broker": f"{self.host}:{self.port}",
                "count": len(messages),
                "messages": messages[:40],
                "truncated": len(messages) > 40,
            }
        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:
            return {
                "ok": False,
                "error": 'paho-mqtt not installed; pip install -e ".[mqtt]" or use dry_run',
                "detail": str(exc),
            }

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if self.username:
            client.username_pw_set(self.username, self.password)
        client.connect(self.host, self.port, 30)
        published = 0
        for m in messages:
            payload = m["payload"]
            body = payload if isinstance(payload, str) else json.dumps(payload)
            client.publish(m["topic"], body, retain=bool(m.get("retain")))
            published += 1
        client.disconnect()
        return {
            "ok": True,
            "dry_run": False,
            "broker": f"{self.host}:{self.port}",
            "published": published,
        }
