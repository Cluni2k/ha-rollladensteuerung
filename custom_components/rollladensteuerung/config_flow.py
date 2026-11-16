"""Einrichtung: Zentrale (globale Einstellungen) plus Unterpunkte „Rollladen“ und „Helligkeitssensor“.

Ein Rollladen wird in EINEM Dialog eingestellt; die Bereiche (Zeiten, Positionen, Fenster, Abschattung)
sind aufklappbare Abschnitte.
"""
from __future__ import annotations

from typing import Any

try:  # HA ab 2026.x validiert mit probatio (Nachfolger von voluptuous)
    import probatio as vol
except ImportError:  # ältere HA-Versionen
    import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers import selector as sel

from .const import CONF_COVER, DOMAIN, SUB_HELLIGKEIT, SUB_ROLLLADEN
from .felder import (
    GLOBAL_STANDARD,
    OPTIONAL,
    STANDARD,
    TABS,
    bereinigen,
    global_felder,
    helligkeit_felder,
    rollladen_felder,
)


def _schluessel(name: str, wert: Any):
    if name in OPTIONAL:
        return vol.Optional(name, description={"suggested_value": wert} if wert not in (None, "", []) else {})
    if wert is None:
        return vol.Required(name)
    return vol.Required(name, default=wert)


def flaches_schema(liste: list[tuple[str, dict]], daten: dict) -> vol.Schema:
    return vol.Schema({_schluessel(n, daten.get(n)): sel.selector(s) for n, s in liste})


def rollladen_schema(hass: HomeAssistant, entry: ConfigEntry, daten: dict, mit_abschnitten: bool = True):
    felder = rollladen_felder(hass, entry)
    if not mit_abschnitten:
        return flaches_schema([f for tab in TABS for f in felder[tab]], daten)
    return vol.Schema({
        vol.Required(tab): section(flaches_schema(felder[tab], daten), {"collapsed": tab != "grundlagen"})
        for tab in TABS
    })


def global_schema(hass: HomeAssistant, daten: dict) -> vol.Schema:
    return flaches_schema(global_felder(hass), {**GLOBAL_STANDARD, **daten})


class RollladensteuerungFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title="Rollladensteuerung", data=user_input)
        return self.async_show_form(step_id="user", data_schema=global_schema(self.hass, {}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return GlobalOptionen()

    @classmethod
    @callback
    def async_get_supported_subentry_types(cls, config_entry: ConfigEntry) -> dict[str, type[ConfigSubentryFlow]]:
        return {SUB_ROLLLADEN: RollladenFlow, SUB_HELLIGKEIT: HelligkeitFlow}


class GlobalOptionen(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        d = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=global_schema(self.hass, d))


class HelligkeitFlow(ConfigSubentryFlow):
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return await self._formular("user", user_input, None)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return await self._formular("reconfigure", user_input, self._get_reconfigure_subentry())

    async def _formular(self, step_id, user_input, sub) -> SubentryFlowResult:
        if user_input is not None:
            name = user_input.pop("name")
            if sub is None:
                return self.async_create_entry(title=name, data=user_input)
            return self.async_update_and_abort(self._get_entry(), sub, title=name, data=user_input)
        d = {**(sub.data if sub else {}), "name": sub.title if sub else ""}
        return self.async_show_form(step_id=step_id, data_schema=flaches_schema(helligkeit_felder(self.hass), d))


class RollladenFlow(ConfigSubentryFlow):
    """Ein Rollladen in einem Dialog mit aufklappbaren Abschnitten."""

    async def async_step_user(self, user_input=None) -> SubentryFlowResult:
        if user_input is not None:
            daten = self._flach(user_input)
            name = daten.pop("name")
            return self.async_create_entry(title=name, data=daten, unique_id=daten[CONF_COVER])
        entry = self._get_entry()
        vorgabe = dict(STANDARD)
        hell = [sid for sid, s in entry.subentries.items() if s.subentry_type == SUB_HELLIGKEIT]
        if hell:
            vorgabe["helligkeitssensor"] = hell[0]
        vorgabe["name"] = None
        return self.async_show_form(step_id="user", data_schema=rollladen_schema(self.hass, entry, vorgabe))

    async def async_step_reconfigure(self, user_input=None) -> SubentryFlowResult:
        sub = self._get_reconfigure_subentry()
        entry = self._get_entry()
        if user_input is not None:
            daten = self._flach(user_input)
            name = daten.pop("name")
            return self.async_update_and_abort(entry, sub, title=name, data=daten)
        d = {**STANDARD, **sub.data, "name": sub.title}
        return self.async_show_form(step_id="reconfigure", data_schema=rollladen_schema(self.hass, entry, d))

    @staticmethod
    def _flach(user_input: dict) -> dict:
        daten: dict[str, Any] = {}
        for tab in TABS:
            daten.update(user_input.get(tab) or {})
        daten.setdefault("fenster", [])
        for k in ("helligkeitssensor", "schlaf", "raumtemperatur"):
            daten.setdefault(k, "")
        return bereinigen(daten)
