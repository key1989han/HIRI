"""Tuya cloud/local adapter stub with offline mapping table."""

from __future__ import annotations

from hiri_bridge.devices.types import Device

# Offline mapping table: tuya category → HA domain
TUYA_CATEGORY_MAP: dict[str, str] = {
    "dj": "light",  # light
    "kg": "switch",  # switch
    "cz": "switch",  # socket
    "wsdcg": "sensor",  # temp humidity
    "mcs": "binary_sensor",  # contact
    "ywbj": "binary_sensor",  # smoke
    "wk": "climate",  # thermostat
    "cl": "cover",  # curtain
}

TUYA_FIXTURE: list[dict] = [
    {"id": "bf123light", "name": "Tuya RGB bulb", "category": "dj", "online": True},
    {"id": "bf456sock", "name": "Tuya plug farm", "category": "cz", "online": True},
    {"id": "bf789th", "name": "Tuya temp/hum", "category": "wsdcg", "online": True},
    {"id": "bf000door", "name": "Tuya door", "category": "mcs", "online": False},
]


class TuyaAdapter:
    name = "tuya"

    def __init__(self, access_id: str = "", access_secret: str = "", use_fixture: bool = True):
        self.access_id = access_id
        self.access_secret = access_secret
        self.use_fixture = use_fixture

    def list_remote(self) -> list[Device]:
        if self.access_id and self.access_secret and not self.use_fixture:
            return []  # live cloud API not implemented offline
        devices: list[Device] = []
        for row in TUYA_FIXTURE:
            domain = TUYA_CATEGORY_MAP.get(row["category"], "sensor")
            devices.append(
                Device(
                    id=f"{domain}.tuya_{row['id']}",
                    name=row["name"],
                    domain=domain,
                    manufacturer="Tuya",
                    model=row["category"],
                    area="home",
                    online=bool(row.get("online", True)),
                    state={"state": "off" if domain != "sensor" else "22.5"},
                    attributes={
                        "tuya_id": row["id"],
                        "category": row["category"],
                        "unit_of_measurement": "°C" if domain == "sensor" else None,
                    },
                    adapter="tuya",
                )
            )
        return devices

    def push_state(self, device: Device) -> None:
        return None

    @staticmethod
    def mapping_table() -> dict[str, str]:
        return dict(TUYA_CATEGORY_MAP)
