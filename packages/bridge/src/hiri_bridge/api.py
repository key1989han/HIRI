from __future__ import annotations

from hiri_bridge import __version__
from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import DOMAINS, Device
from hiri_bridge.ha.discovery import export_discovery

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except ImportError as exc:  # pragma: no cover
    raise ImportError('pip install -e ".[api]"') from exc

app = FastAPI(title="HIRI Bridge", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_reg = DeviceRegistry()
_reg.load_or_seed()


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "hiri-bridge", "version": __version__, "domains": DOMAINS}


@app.get("/stats")
def stats() -> dict:
    return _reg.stats()


@app.get("/devices")
def list_devices(domain: str | None = None) -> list[dict]:
    devices = _reg.list()
    if domain:
        devices = [d for d in devices if d.domain == domain]
    return [d.model_dump() for d in devices]


@app.get("/devices/{device_id}")
def get_device(device_id: str) -> dict:
    d = _reg.get(device_id)
    if not d:
        raise HTTPException(404, "device not found")
    return d.model_dump()


@app.post("/devices/{device_id}/command")
def command_device(device_id: str, body: dict) -> dict:
    action = body.get("action") or body.get("service") or "turn_on"
    data = body.get("data") or {}
    try:
        dev = _reg.apply_command(device_id, action, data)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return dev.model_dump()


@app.post("/devices")
def upsert_device(device: Device) -> dict:
    return _reg.upsert(device).model_dump()


@app.get("/ha/discovery")
def ha_discovery() -> list[dict]:
    return export_discovery(_reg.list())


@app.post("/devices/seed")
def seed() -> dict:
    _reg.seed()
    return _reg.stats()
