"""Reparaturen: fehlende oder deaktivierte Entitäten direkt durch andere ersetzen."""
from __future__ import annotations

from typing import Any

try:
    import probatio as vol
except ImportError:  # ältere Home-Assistant-Versionen
    import voluptuous as vol

from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from . import entitaeten


class FehlendeEntitaetenFlow(RepairsFlow):
    def __init__(self, entry_id: str) -> None:
        self.entry_id = entry_id

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        entry = self.hass.config_entries.async_get_entry(self.entry_id)
        if entry is None:
            return self.async_abort(reason="entfernt")
        fehl = entitaeten.fehlende(self.hass, entry)
        if not fehl:
            entitaeten.pruefen(self.hass, entry)
            return self.async_create_entry(data={})

        if user_input is not None:
            for alt in fehl:
                neu = user_input.get(alt) or None
                if neu and neu != alt:
                    entitaeten.ersetzen(self.hass, entry, alt, neu)
                elif not neu:
                    entitaeten.ersetzen(self.hass, entry, alt, None)   # Pflichtfelder bleiben stehen
            entitaeten.pruefen(self.hass, entry)
            return self.async_create_entry(data={})

        schema = {}
        for eid, (_grund, vs) in fehl.items():
            domains = sorted({eid.split(".", 1)[0]})
            mehrfach_pflicht = any(v.feld in entitaeten.PFLICHT for v in vs)
            schluessel = vol.Required(eid, default=eid) if mehrfach_pflicht else vol.Optional(eid, default=eid)
            schema[schluessel] = EntitySelector(EntitySelectorConfig(domain=domains))
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(schema),
            description_placeholders={"liste": entitaeten.liste_text(fehl)})


async def async_create_fix_flow(hass: HomeAssistant, issue_id: str, data: dict[str, Any] | None) -> RepairsFlow:
    return FehlendeEntitaetenFlow((data or {}).get("entry_id", ""))
