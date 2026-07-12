"""Zigbee2MQTT adapter — fixture offline; optional live HTTP/MQTT later."""

from __future__ import annotations

from hiri_bridge.devices.types import Device

# Minimal offline fixture mimicking z2m /api/devices-ish payload
Z2M_FIXTURE: list[dict] = [
    {
        "friendly_name": "kitchen/motion",
        "type": "EndDevice",
        "definition": {"model": "SNZB-03", "vendor": "SONOFF", "description": "Motion"},
        "exposes": [{"type": "binary", "name": "occupancy"}],
    },
    {
        "friendly_name": "hall/contact",
        "type": "EndDevice",
        "definition": {"model": "MCCGQ11LM", "vendor": "Xiaomi", "description": "Door"},
        "exposes": [{"type": "binary", "name": "contact"}],
    },
    {
        "friendly_name": "living/bulb",
        "type": "Router",
        "definition": {"model": "LED1623G12", "vendor": "IKEA", "description": "Bulb"},
        "exposes": [{"type": "light", "features": [{"name": "state"}, {"name": "brightness"}]}],
    },
]


class Zigbee2MqttAdapter:
    name = "z2m"

    def __init__(self, base_url: str = "", use_fixture: bool = True):
        self.base_url = (base_url or "").rstrip("/")
        self.use_fixture = use_fixture

    def list_remote(self) -> list[Device]:
        if self.base_url and not self.use_fixture:
            # Live HTTP to z2m frontend API would go here
            return []
        devices: list[Device] = []
        for row in Z2M_FIXTURE:
            name = row["friendly_name"]
            exposes = row.get("exposes") or []
            domain = "sensor"
            if any(e.get("type") == "light" for e in exposes):
                domain = "light"
            elif any(e.get("name") in {"occupancy", "contact", "motion"} for e in exposes):
                domain = "binary_sensor"
            slug = name.replace("/", "_").replace(" ", "_").lower()
            devices.append(
                Device(
                    id=f"{domain}.z2m_{slug}",
                    name=name,
                    domain=domain,
                    manufacturer=(row.get("definition") or {}).get("vendor", "Zigbee"),
                    model=(row.get("definition") or {}).get("model", "z2m"),
                    area=name.split("/")[0] if "/" in name else "home",
                    state={"state": "off" if domain != "sensor" else "0"},
                    attributes={
                        "via": "z2m",
                        "device_class": "motion"
                        if "motion" in name or "occupancy" in str(exposes)
                        else "door"
                        if "contact" in name
                        else None,
                    },
                    adapter="z2m",
                )
            )
        return devices

    def push_state(self, device: Device) -> None:
        return None
