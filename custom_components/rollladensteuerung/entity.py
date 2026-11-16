"""Gemeinsame Basis der Entitäten."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .controller import Steuerung


class Basis(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, steuerung: Steuerung, schluessel: str, sid: str | None = None) -> None:
        self.steuerung = steuerung
        self.sid = sid
        self._attr_translation_key = schluessel
        eid = steuerung.entry.entry_id
        if sid is None:
            self._attr_unique_id = f"{eid}_{schluessel}"
            self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, eid)}, name="Rollladensteuerung",
                                                manufacturer="Rollladensteuerung", model="Zentrale")
        else:
            r = steuerung.rolllaeden[sid]
            self._attr_unique_id = f"{eid}_{sid}_{schluessel}"
            self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, sid)}, name=f"Automatik {r.e.name}",
                                                manufacturer="Rollladensteuerung", model="Rollladen")

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(async_dispatcher_connect(self.hass, self.steuerung.signal,
                                                      self.async_write_ha_state))
