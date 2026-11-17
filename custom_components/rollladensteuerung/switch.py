"""Schalter: Automatik morgens/abends/Abschattung/Komfort, Partymodus, Gast – und je Rollladen „Automatik“."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import PUSH, SCHALTER
from .entity import Basis

SYMBOLE = {"morgens": "mdi:weather-sunset-up", "abends": "mdi:weather-sunset-down",
           "abschattung": "mdi:sun-angle", "komfort": "mdi:window-open-variant",
           "partymodus": "mdi:party-popper", "gast": "mdi:account-clock",
           "push_oeffnen": "mdi:bell-ring-outline", "push_schliessen": "mdi:bell-ring-outline",
           "push_warnungen": "mdi:bell-alert-outline", "push_lueften": "mdi:bell-outline",
           "push_abschatten": "mdi:bell-outline", "push_funktionen": "mdi:bell-cog-outline",
           "push_manuell": "mdi:bell-outline", "urlaub": "mdi:palm-tree",
           "push_zusammenfassung": "mdi:text-box-outline"}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    st = entry.runtime_data
    async_add_entities([GlobalSchalter(st, name) for name in (*SCHALTER, *PUSH)])
    for sid in st.rolllaeden:
        async_add_entities([RollladenAktiv(st, sid)], config_subentry_id=sid)


class GlobalSchalter(Basis, SwitchEntity):
    def __init__(self, steuerung, name: str) -> None:
        super().__init__(steuerung, f"auto_{name}")
        self._name = name
        self._attr_icon = SYMBOLE[name]

    @property
    def is_on(self) -> bool:
        return self.steuerung.schalter[self._name]

    async def async_turn_on(self, **kwargs) -> None:
        await self.steuerung.async_schalter(self._name, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.steuerung.async_schalter(self._name, False)


class RollladenAktiv(Basis, SwitchEntity):
    _attr_icon = "mdi:window-shutter-auto"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, steuerung, sid: str) -> None:
        super().__init__(steuerung, "automatik", sid)

    @property
    def is_on(self) -> bool:
        return self.steuerung.aktiv[self.sid]

    async def async_turn_on(self, **kwargs) -> None:
        await self.steuerung.async_rollladen_aktiv(self.sid, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.steuerung.async_rollladen_aktiv(self.sid, False)
