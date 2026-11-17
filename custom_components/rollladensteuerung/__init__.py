"""Rollladensteuerung – Öffnen, Schließen, Lüften und Abschattung für Rollläden.

Nachbau der FHEM-Rollladensteuerung von Bernd Hermanns und Matthias Frintrop
(https://forum.fhem.de/index.php/topic,73964.0.html).
"""
from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, issue_registry as ir
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .controller import Steuerung
from .entitaeten import issue_id
from .websocket import async_registrieren

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
URL_JS = "/rollladensteuerung_frontend/rollladensteuerung.js"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Frontend (Karten, Einstell-Dialog, Dashboard-Vorlage), WebSocket-Befehle und Dienste."""
    datei = Path(__file__).parent / "frontend" / "rollladensteuerung.js"
    stand = int(await hass.async_add_executor_job(lambda: datei.stat().st_mtime))
    await hass.http.async_register_static_paths([StaticPathConfig(URL_JS, str(datei), False)])
    add_extra_js_url(hass, f"{URL_JS}?v={stand}")
    async_registrieren(hass)

    def _steuerungen():
        return [e.runtime_data for e in hass.config_entries.async_loaded_entries(DOMAIN)]

    async def _neu_berechnen(call: ServiceCall) -> None:
        for st in _steuerungen():
            await st.async_alle_neu_planen()

    async def _abschattung_pruefen(call: ServiceCall) -> None:
        for st in _steuerungen():
            await st.async_abschattung()

    async def _alle_oeffnen(call: ServiceCall) -> None:
        for st in _steuerungen():
            await st.async_alle("oeffnen")

    async def _alle_schliessen(call: ServiceCall) -> None:
        for st in _steuerungen():
            await st.async_alle("schliessen")

    async def _alle_lueften(call: ServiceCall) -> None:
        for st in _steuerungen():
            await st.async_alle("lueften")

    async def _alle_abschatten(call: ServiceCall) -> None:
        for st in _steuerungen():
            await st.async_alle("abschatten")

    async def _zusammenfassung(call: ServiceCall) -> None:
        for st in _steuerungen():
            await st.async_zusammenfassung(senden=True)

    hass.services.async_register(DOMAIN, "zusammenfassung_senden", _zusammenfassung)
    hass.services.async_register(DOMAIN, "alle_lueften", _alle_lueften)
    hass.services.async_register(DOMAIN, "alle_abschatten", _alle_abschatten)
    hass.services.async_register(DOMAIN, "neu_berechnen", _neu_berechnen)
    hass.services.async_register(DOMAIN, "abschattung_pruefen", _abschattung_pruefen)
    hass.services.async_register(DOMAIN, "alle_oeffnen", _alle_oeffnen)
    hass.services.async_register(DOMAIN, "alle_schliessen", _alle_schliessen)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    steuerung = Steuerung(hass, entry)
    entry.runtime_data = steuerung
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await steuerung.async_start()
    entry.async_on_unload(entry.add_update_listener(_neu_laden))
    return True


async def _neu_laden(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await entry.runtime_data.async_stop()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    ir.async_delete_issue(hass, DOMAIN, issue_id(entry))
