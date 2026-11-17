"""Verweise auf andere Entitäten: Umbenennungen übernehmen, fehlende unter „Reparaturen“ melden."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, issue_registry as ir

from .const import (
    CONF_ANWESENHEIT,
    CONF_COVER,
    CONF_ENTITY,
    CONF_FENSTER,
    CONF_RAUCH,
    CONF_RAUMTEMPERATUR,
    CONF_SCHLAF,
    CONF_SONNE,
    CONF_TEMPERATUR,
    CONF_WERKTAG,
    CONF_WETTER,
    DOMAIN,
    SUB_HELLIGKEIT,
    SUB_ROLLLADEN,
)
from .core import verweis_ersetzen

_LOGGER = logging.getLogger(__name__)

# Felder, in denen Entitäten stehen
GLOBAL_FELDER = (CONF_ANWESENHEIT, CONF_TEMPERATUR, CONF_WERKTAG, CONF_SONNE, CONF_WETTER, CONF_RAUCH)
FELDER = {SUB_ROLLLADEN: (CONF_COVER, CONF_FENSTER, CONF_SCHLAF, CONF_RAUMTEMPERATUR),
          SUB_HELLIGKEIT: (CONF_ENTITY,)}
# ohne diese Felder geht es nicht – sie lassen sich nur ersetzen, nicht entfernen
PFLICHT = {CONF_COVER, CONF_ENTITY}


@dataclass
class Verweis:
    entity_id: str
    feld: str
    wo: str                 # „Haupteinstellungen“ oder Name des Rollladens/Sensors
    subentry: str | None    # None = Haupteinstellungen


def issue_id(entry: ConfigEntry) -> str:
    return f"fehlende_entitaeten_{entry.entry_id}"


def verweise(entry: ConfigEntry) -> list[Verweis]:
    aus: list[Verweis] = []
    cfg = {**entry.data, **entry.options}
    for feld in GLOBAL_FELDER:
        for eid in _liste(cfg.get(feld)):
            aus.append(Verweis(eid, feld, "Haupteinstellungen", None))
    for sid, sub in entry.subentries.items():
        for feld in FELDER.get(sub.subentry_type, ()):
            for eid in _liste(sub.data.get(feld)):
                aus.append(Verweis(eid, feld, sub.title, sid))
    return aus


def _liste(wert) -> list[str]:
    if isinstance(wert, list):
        return [w for w in wert if isinstance(w, str) and w]
    return [wert] if isinstance(wert, str) and wert else []


def ersetzen(hass: HomeAssistant, entry: ConfigEntry, alt: str, neu: str | None) -> bool:
    """Entität überall in den Einstellungen ersetzen (neu leer = entfernen, außer bei Pflichtfeldern)."""
    geaendert = False
    for sid, sub in list(entry.subentries.items()):
        felder = FELDER.get(sub.subentry_type, ())
        if not neu:
            felder = tuple(f for f in felder if f not in PFLICHT)
        if (daten := verweis_ersetzen(dict(sub.data), felder, alt, neu)) is not None:
            hass.config_entries.async_update_subentry(entry, sub, data=daten)
            geaendert = True
    for teil in ("data", "options"):
        quelle = dict(getattr(entry, teil))
        if (daten := verweis_ersetzen(quelle, GLOBAL_FELDER, alt, neu)) is not None:
            hass.config_entries.async_update_entry(entry, **{teil: daten})
            geaendert = True
    if geaendert:
        _LOGGER.info("Rollladensteuerung: %s → %s übernommen", alt, neu or "(entfernt)")
    return geaendert


def fehlende(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, tuple[str, list[Verweis]]]:
    """Entität → (Grund, Verweise) für alle Entitäten, die es nicht (mehr) gibt oder die deaktiviert sind.

    „Nicht erreichbar“ zählt nicht – das meldet die Erreichbarkeits-Warnung.
    """
    reg = er.async_get(hass)
    aus: dict[str, tuple[str, list[Verweis]]] = {}
    for v in verweise(entry):
        eintrag = reg.async_get(v.entity_id)
        if eintrag is not None:
            if eintrag.disabled_by is None:
                continue
            grund = "deaktiviert"
        elif hass.states.get(v.entity_id) is not None:
            continue
        else:
            grund = "gibt es nicht"
        aus.setdefault(v.entity_id, (grund, []))[1].append(v)
    return aus


def liste_text(fehl: dict[str, tuple[str, list[Verweis]]]) -> str:
    zeilen = []
    for eid, (grund, vs) in fehl.items():
        wo = ", ".join(sorted({v.wo for v in vs}))
        zeilen.append(f"- `{eid}` ({grund}) – {wo}")
    return "\n".join(zeilen)


def pruefen(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, tuple[str, list[Verweis]]]:
    """Reparaturen-Eintrag anlegen, aktualisieren oder löschen."""
    fehl = fehlende(hass, entry)
    if not fehl:
        ir.async_delete_issue(hass, DOMAIN, issue_id(entry))
        return fehl
    ir.async_create_issue(
        hass, DOMAIN, issue_id(entry), is_fixable=True, is_persistent=False,
        severity=ir.IssueSeverity.WARNING, translation_key="fehlende_entitaeten",
        translation_placeholders={"liste": liste_text(fehl)}, data={"entry_id": entry.entry_id})
    return fehl


def registry_ids(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, str]:
    """Entität → interne Registry-ID (bleibt bei Umbenennungen gleich)."""
    reg = er.async_get(hass)
    return {v.entity_id: e.id for v in verweise(entry) if (e := reg.async_get(v.entity_id)) is not None}


def umbenennungen_nachholen(hass: HomeAssistant, entry: ConfigEntry, ids: dict[str, str]) -> bool:
    """Umbenennungen übernehmen, die passiert sind, während die Steuerung nicht lief."""
    reg = er.async_get(hass)
    geaendert = False
    for eid, reg_id in ids.items():
        if reg.async_get(eid) is not None:
            continue
        eintrag = reg.entities.get_entry(reg_id) if hasattr(reg.entities, "get_entry") else None
        if eintrag is not None and eintrag.entity_id != eid:
            geaendert |= ersetzen(hass, entry, eid, eintrag.entity_id)
    return geaendert
