"""WebSocket-Befehle für die Dashboard-Karten: Konfiguration lesen und speichern."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

try:
    import probatio as vol
except ImportError:
    import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .config_flow import global_schema, rollladen_schema
from .const import DOMAIN, SCHALTER, SUB_HELLIGKEIT, SUB_ROLLLADEN
from .felder import GLOBAL_STANDARD, OPTIONAL, STANDARD, TABS, bereinigen, global_felder, rollladen_felder

_TEXTE: dict[str, dict] = {}


async def _texte(hass: HomeAssistant) -> dict:
    sprache = (hass.config.language or "en").split("-")[0]
    if sprache not in _TEXTE:
        ordner = Path(__file__).parent / "translations"
        datei = ordner / f"{sprache}.json"
        if not datei.exists():
            datei = ordner / "en.json"
        _TEXTE[sprache] = await hass.async_add_executor_job(lambda: json.loads(datei.read_text("utf-8")))
    return _TEXTE[sprache]


@callback
def async_registrieren(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_konfig)
    websocket_api.async_register_command(hass, ws_rollladen_speichern)
    websocket_api.async_register_command(hass, ws_global_speichern)


def _eintrag(hass: HomeAssistant):
    eintraege = hass.config_entries.async_loaded_entries(DOMAIN)
    return eintraege[0] if eintraege else None


@websocket_api.websocket_command({vol.Required("type"): "rollladensteuerung/konfig"})
@websocket_api.async_response
async def ws_konfig(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    entry = _eintrag(hass)
    if entry is None:
        connection.send_error(msg["id"], "nicht_geladen", "Rollladensteuerung ist nicht eingerichtet")
        return
    t = await _texte(hass)
    abschnitte = t["config_subentries"]["rollladen"]["step"]["reconfigure"]["sections"]
    optionen = {k: v.get("options", {}) for k, v in t.get("selector", {}).items()}

    def schema(liste):
        aus = []
        for name, s in liste:
            s = copy.deepcopy(s)
            if "select" in s and (key := s["select"].pop("translation_key", None)):
                s["select"]["options"] = [{"value": o, "label": optionen.get(key, {}).get(o, o)}
                                          for o in s["select"]["options"]]
            aus.append({"name": name, "selector": s, "required": name not in OPTIONAL})
        return aus

    felder = rollladen_felder(hass, entry)
    reg = er.async_get(hass)

    def eid(domain: str, uid: str) -> str | None:
        return reg.async_get_entity_id(domain, DOMAIN, uid)

    rolllaeden = []
    for sid, sub in entry.subentries.items():
        if sub.subentry_type != SUB_ROLLLADEN:
            continue
        basis = f"{entry.entry_id}_{sid}"
        rolllaeden.append({
            "sid": sid, "name": sub.title, "cover": sub.data.get("cover"),
            "daten": {**STANDARD, **sub.data, "name": sub.title},
            "entities": {"status": eid("sensor", f"{basis}_status"),
                         "oeffnen": eid("sensor", f"{basis}_naechstes_oeffnen"),
                         "schliessen": eid("sensor", f"{basis}_naechstes_schliessen"),
                         "automatik": eid("switch", f"{basis}_automatik")}})
    zentrale = {k: eid("switch", f"{entry.entry_id}_auto_{k}") for k in SCHALTER}
    zentrale["oeffnen"] = eid("sensor", f"{entry.entry_id}_naechstes_oeffnen")
    zentrale["schliessen"] = eid("sensor", f"{entry.entry_id}_naechstes_schliessen")
    connection.send_result(msg["id"], {
        "entry_id": entry.entry_id,
        "tabs": [{"key": tab, "titel": abschnitte[tab]["name"], "schema": schema(felder[tab])} for tab in TABS],
        "labels": {feld: text for tab in abschnitte.values() for feld, text in tab.get("data", {}).items()},
        "global": {"schema": schema(global_felder(hass)),
                   "labels": t["config"]["step"]["user"]["data"],
                   "daten": {**GLOBAL_STANDARD, **entry.data, **entry.options}},
        "status_texte": t["entity"]["sensor"]["status"]["state"],
        "rolllaeden": rolllaeden,
        "helligkeit": [{"sid": sid, "name": s.title, "entity": s.data.get("entity")}
                       for sid, s in entry.subentries.items() if s.subentry_type == SUB_HELLIGKEIT],
        "zentrale": zentrale,
    })


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "rollladensteuerung/rollladen/speichern",
                                  vol.Required("sid"): str, vol.Required("daten"): dict})
@websocket_api.async_response
async def ws_rollladen_speichern(hass: HomeAssistant, connection: websocket_api.ActiveConnection,
                                 msg: dict[str, Any]) -> None:
    entry = _eintrag(hass)
    sub = entry.subentries.get(msg["sid"]) if entry else None
    if sub is None:
        connection.send_error(msg["id"], "unbekannt", "Rollladen nicht gefunden")
        return
    daten = {**STANDARD, **sub.data, "name": sub.title, **msg["daten"]}
    daten = {k: v for k, v in daten.items() if v not in (None, "")}
    try:
        daten = rollladen_schema(hass, entry, {}, mit_abschnitten=False)(daten)
    except vol.Invalid as err:
        connection.send_error(msg["id"], "ungueltig", str(err))
        return
    daten = bereinigen(daten)
    daten.setdefault("fenster", [])
    for k in ("helligkeitssensor", "schlaf", "raumtemperatur"):
        daten.setdefault(k, "")
    name = daten.pop("name")
    hass.config_entries.async_update_subentry(entry, sub, title=name, data=daten)
    connection.send_result(msg["id"], {"ok": True})


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "rollladensteuerung/global/speichern",
                                  vol.Required("daten"): dict})
@websocket_api.async_response
async def ws_global_speichern(hass: HomeAssistant, connection: websocket_api.ActiveConnection,
                              msg: dict[str, Any]) -> None:
    entry = _eintrag(hass)
    if entry is None:
        connection.send_error(msg["id"], "nicht_geladen", "Rollladensteuerung ist nicht eingerichtet")
        return
    daten = {k: v for k, v in msg["daten"].items() if v not in (None, "")}
    try:
        daten = global_schema(hass, {})(daten)
    except vol.Invalid as err:
        connection.send_error(msg["id"], "ungueltig", str(err))
        return
    hass.config_entries.async_update_entry(entry, options=daten)
    connection.send_result(msg["id"], {"ok": True})
