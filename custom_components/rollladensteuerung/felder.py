"""Eine Beschreibung aller Einstellfelder – genutzt vom Einrichtungsdialog und vom Dashboard-Dialog."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import (
    ASTRO_MODI,
    CONF_ANWESENHEIT,
    CONF_ASTRO_ABENDS,
    CONF_ASTRO_MORGENS,
    CONF_FROST_TEMP,
    CONF_HELLIGKEIT_MIN,
    CONF_HORIZONT_ABENDS,
    CONF_HORIZONT_MORGENS,
    CONF_SONNE,
    CONF_TEMPERATUR,
    CONF_WERKTAG,
    SUB_HELLIGKEIT,
)
from .core import ABSCHATTUNG_MODI, MODI, Einstellungen

# Standardwerte für neue Rollläden = Vorgaben der FHEM-Steuerung (Rollladensteuerung_update_device)
STANDARD: dict[str, Any] = {f.name: f.default for f in fields(Einstellungen) if f.name not in ("name", "cover")}
STANDARD.update({"fenster": [], "helligkeitssensor": "", "schlaf": "", "raumtemperatur": ""})

TABS = ("grundlagen", "zeiten", "positionen", "fenster", "abschattung")
OPTIONAL = {"fenster", "helligkeitssensor", "schlaf", "raumtemperatur", "min_temp_vorhersage",
            CONF_ANWESENHEIT, CONF_TEMPERATUR, CONF_WERKTAG, "wetter", "push_dienst", "rauchmelder",
            "hitzeschutz_temp", "dunkel_lux"}
GANZZAHL = {"offset_morgens", "offset_abends", "zufall_minuten", "offen_pos", "geschlossen_pos", "lueften_pos",
            "geoeffnet_pos", "pos_nach_komfort_oeffnen", "wartezeit", "sperrzeit_nach_manuell",
            "sperrzeit_vor_nacht", "abschattung_pos", "pos_nach_abschattung"}


def _zahl(minimum, maximum, schritt=1, einheit=None, box=True) -> dict:
    konfig = {"min": minimum, "max": maximum, "step": schritt, "mode": "box" if box else "slider"}
    if einheit:
        konfig["unit_of_measurement"] = einheit
    return {"number": konfig}


def _auswahl(optionen, schluessel) -> dict:
    return {"select": {"options": list(optionen), "translation_key": schluessel, "mode": "dropdown"}}


JA_NEIN = {"boolean": {}}
ZEIT = {"time": {}}
PROZENT = _zahl(0, 100, 5, "%", False)


def versteckte(hass: HomeAssistant, domains: tuple[str, ...]) -> list[str]:
    """Ausgeblendete und deaktivierte Entitäten – die sollen in den Auswahllisten nicht auftauchen."""
    reg = er.async_get(hass)
    return sorted(e.entity_id for e in reg.entities.values()
                  if e.domain in domains and (e.hidden_by is not None or e.disabled_by is not None))


def rollladen_felder(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, list[tuple[str, dict]]]:
    hell = [{"value": sid, "label": s.title} for sid, s in entry.subentries.items()
            if s.subentry_type == SUB_HELLIGKEIT]
    cover = {"entity": {"domain": "cover", "exclude_entities": versteckte(hass, ("cover",))}}
    schlaf = {"entity": {"domain": ["input_boolean", "binary_sensor", "switch"],
                         "exclude_entities": versteckte(hass, ("input_boolean", "binary_sensor", "switch"))}}
    raum = {"entity": {"domain": "sensor", "device_class": "temperature",
                       "exclude_entities": versteckte(hass, ("sensor",))}}
    fenster = {"entity": {"domain": ["binary_sensor", "sensor"], "multiple": True,
                          "exclude_entities": versteckte(hass, ("binary_sensor", "sensor"))}}
    return {
        "grundlagen": [
            ("name", {"text": {}}), ("cover", cover), ("aktiv", JA_NEIN),
            ("modus_hoch", _auswahl(MODI, "modus")), ("modus_runter", _auswahl(MODI, "modus")),
            ("frostschutz", JA_NEIN), ("gaestezimmer", JA_NEIN), ("partymodus", JA_NEIN), ("schlaf", schlaf)],
        "zeiten": [
            ("hoch", _auswahl(("astro", "zeit"), "zeitart")), ("zeit_hoch_frueh", ZEIT), ("zeit_hoch_spaet", ZEIT),
            ("zeit_hoch_we", ZEIT), ("offset_morgens", _zahl(-120, 120, 1, "min")),
            ("runter", _auswahl(("astro", "zeit"), "zeitart")), ("zeit_runter_frueh", ZEIT),
            ("zeit_runter_spaet", ZEIT), ("offset_abends", _zahl(-120, 120, 1, "min")),
            ("zufall_minuten", _zahl(0, 60, 1, "min"))],
        "positionen": [
            ("offen_pos", PROZENT), ("geschlossen_pos", PROZENT), ("lueften_pos", PROZENT),
            ("geoeffnet_pos", PROZENT), ("pos_nach_komfort_oeffnen", _zahl(-2, 100))],
        "fenster": [("fenster", fenster), ("luft_fenster_offen", JA_NEIN), ("aussperrschutz", JA_NEIN)],
        "abschattung": [
            ("abschattung", _auswahl(ABSCHATTUNG_MODI, "abschattung")),
            ("helligkeitssensor", {"select": {"options": hell, "mode": "dropdown"}}),
            ("himmelsrichtung", _zahl(0, 359, 1, "°")), ("winkel_links", _zahl(0, 90, 5, "°", False)),
            ("winkel_rechts", _zahl(0, 90, 5, "°", False)), ("min_elevation", _zahl(0, 60, 1, "°")),
            ("schwelle_sonnig", _zahl(0, 150000, 1000, "lx")), ("schwelle_wolkig", _zahl(0, 150000, 1000, "lx")),
            ("min_temp_aussen", _zahl(-20, 40, 0.5, "°C")), ("min_temp_vorhersage", _zahl(-20, 45, 0.5, "°C")),
            ("raumtemperatur", raum), ("min_temp_innen", _zahl(10, 35, 0.5, "°C")), ("abschattung_pos", PROZENT),
            ("abschattung_dynamisch", JA_NEIN), ("fensterhoehe", _zahl(20, 400, 1, "cm")),
            ("bruestung", _zahl(0, 300, 1, "cm")), ("eindringtiefe", _zahl(0, 500, 5, "cm")),
            ("pos_nach_abschattung", _zahl(-1, 100)), ("wartezeit", _zahl(0, 120, 1, "min")),
            ("sperrzeit_nach_manuell", _zahl(0, 240, 1, "min")), ("sperrzeit_vor_nacht", _zahl(0, 240, 1, "min")),
            ("schnell_oeffnen", JA_NEIN), ("schnell_schliessen", JA_NEIN)],
    }


def global_felder(hass: HomeAssistant) -> list[tuple[str, dict]]:
    sensoren = versteckte(hass, ("binary_sensor", "sensor", "person", "group", "input_boolean",
                                 "device_tracker", "switch"))
    return [
        (CONF_ANWESENHEIT, {"entity": {"domain": ["binary_sensor", "person", "group", "input_boolean",
                                                  "device_tracker", "switch"], "exclude_entities": sensoren}}),
        (CONF_TEMPERATUR, {"entity": {"domain": "sensor", "device_class": "temperature",
                                      "exclude_entities": sensoren}}),
        (CONF_WERKTAG, {"entity": {"domain": ["binary_sensor", "input_boolean"], "exclude_entities": sensoren}}),
        (CONF_SONNE, {"entity": {"domain": "sun"}}),
        (CONF_ASTRO_MORGENS, _auswahl(ASTRO_MODI, "astro")),
        (CONF_HORIZONT_MORGENS, _zahl(-18, 10, 0.5, "°")),
        (CONF_ASTRO_ABENDS, _auswahl(ASTRO_MODI, "astro")),
        (CONF_HORIZONT_ABENDS, _zahl(-18, 10, 0.5, "°")),
        (CONF_FROST_TEMP, _zahl(-20, 10, 0.5, "°C")),
        (CONF_HELLIGKEIT_MIN, _zahl(0, 20000, 100, "lx")),
        ("wetter", {"entity": {"domain": "weather"}}),
        ("abstand_sekunden", _zahl(0, 60, 1, "s")),
        ("push_dienst", {"select": {"options": push_dienste(hass), "mode": "dropdown", "custom_value": True}}),
        ("zusammenfassung_zeit", {"time": {}}),
        ("rauchmelder", {"entity": {"domain": "binary_sensor", "multiple": True,
                                    "exclude_entities": versteckte(hass, ("binary_sensor",))}}),
        ("hitzeschutz_temp", _zahl(15, 45, 0.5, "°C")),
        ("hitzeschutz_pos", _zahl(0, 100, 5, "%", False)),
        ("dunkel_lux", _zahl(0, 5000, 10, "lx")),
        ("urlaub_zufall", _zahl(0, 120, 5, "min")),
    ]


def push_dienste(hass: HomeAssistant) -> list[dict]:
    """Benachrichtigungsdienste (HA-App, Pushover, Telegram …). Ein Skript mit title/message kann man eintippen."""
    optionen = []
    for name in sorted(hass.services.async_services().get("notify", {})):
        if name in ("notify", "send_message", "persistent_notification"):
            continue   # „notify“ = alle Dienste gleichzeitig, die anderen sind keine Push-Dienste
        if name.startswith("mobile_app_"):
            label = f"HA-App: {name.removeprefix('mobile_app_').replace('_', ' ')}"
        else:
            label = name.replace("_", " ").title()
        optionen.append({"value": f"notify.{name}", "label": f"{label} (notify.{name})"})
    return optionen


GLOBAL_STANDARD = {CONF_SONNE: "sun.sun", CONF_ASTRO_MORGENS: "real", CONF_ASTRO_ABENDS: "real",
                   CONF_HORIZONT_MORGENS: 0, CONF_HORIZONT_ABENDS: 0, CONF_FROST_TEMP: 0,
                   CONF_HELLIGKEIT_MIN: 500, "abstand_sekunden": 5, "zusammenfassung_zeit": "21:00:00",
                   "hitzeschutz_pos": 10, "urlaub_zufall": 30}


def helligkeit_felder(hass: HomeAssistant) -> list[tuple[str, dict]]:
    return [("name", {"text": {}}),
            ("entity", {"entity": {"domain": "sensor", "device_class": "illuminance",
                                   "exclude_entities": versteckte(hass, ("sensor",))}})]


def bereinigen(daten: dict) -> dict:
    """Zahlen, die ganzzahlig sein sollen, als int ablegen."""
    aus = dict(daten)
    for k in GANZZAHL:
        if aus.get(k) is not None:
            aus[k] = int(aus[k])
    return aus
