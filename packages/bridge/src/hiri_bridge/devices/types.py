from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# Home Assistant-style domains HIRI aims to bridge
DeviceDomain = Literal[
    "light",
    "switch",
    "binary_sensor",
    "sensor",
    "climate",
    "cover",
    "lock",
    "fan",
    "media_player",
    "vacuum",
    "camera",
    "button",
    "number",
    "select",
    "siren",
    "humidifier",
    "water_heater",
    "alarm_control_panel",
]

DOMAINS: list[str] = [
    "light",
    "switch",
    "binary_sensor",
    "sensor",
    "climate",
    "cover",
    "lock",
    "fan",
    "media_player",
    "vacuum",
    "camera",
    "button",
    "number",
    "select",
    "siren",
    "humidifier",
    "water_heater",
    "alarm_control_panel",
]


class Device(BaseModel):
    id: str
    name: str
    domain: str
    manufacturer: str = "HIRI"
    model: str = "generic"
    area: str = "home"
    online: bool = True
    state: dict[str, Any] = Field(default_factory=dict)
    attributes: dict[str, Any] = Field(default_factory=dict)
    adapter: str = "local"  # local | mqtt | ha_rest | tuya | z2m | matter


class DeviceCommand(BaseModel):
    device_id: str
    action: str
    data: dict[str, Any] = Field(default_factory=dict)
