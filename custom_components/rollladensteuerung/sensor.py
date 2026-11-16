"""Sensoren: nächstes Öffnen/Schließen (je Rollladen und gesamt) und Status mit allen Merkern."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import Basis

STATUS = ["aus", "bereit", "gesperrt", "vorgemerkt", "abschattung", "ende_vorgemerkt",
          "abschatten_nach_schliessen", "nachtschliessen", "geoeffnet", "lueften", "party", "schlaf"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    st = entry.runtime_data
    async_add_entities([NaechsteZeit(st, "hoch"), NaechsteZeit(st, "runter")])
    for sid in st.rolllaeden:
        async_add_entities([NaechsteZeit(st, "hoch", sid), NaechsteZeit(st, "runter", sid),
                            Status(st, sid)], config_subentry_id=sid)


class NaechsteZeit(Basis, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, steuerung, art: str, sid: str | None = None) -> None:
        super().__init__(steuerung, f"naechstes_{'oeffnen' if art == 'hoch' else 'schliessen'}", sid)
        self._art = art
        self._attr_icon = "mdi:weather-sunset-up" if art == "hoch" else "mdi:weather-sunset-down"

    @property
    def native_value(self) -> datetime | None:
        if self.sid is not None:
            return getattr(self.steuerung.rolllaeden[self.sid].z, f"{self._art}_zeit")
        modus = "modus_hoch" if self._art == "hoch" else "modus_runter"
        zeiten = [getattr(r.z, f"{self._art}_zeit") for sid, r in self.steuerung.rolllaeden.items()
                  if self.steuerung.aktiv.get(sid) and getattr(r.e, modus) != "aus"]
        zeiten = [z for z in zeiten if z]
        return min(zeiten) if zeiten else None


class Status(Basis, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = STATUS
    _attr_icon = "mdi:window-shutter-cog"

    def __init__(self, steuerung, sid: str) -> None:
        super().__init__(steuerung, "status", sid)

    @property
    def native_value(self) -> str:
        return self.steuerung.rolllaeden[self.sid].status(self.steuerung.umgebung())

    @property
    def extra_state_attributes(self) -> dict:
        r = self.steuerung.rolllaeden[self.sid]
        z, e = r.z, r.e
        lage = self.steuerung.lage(self.sid)
        u = self.steuerung.umgebung()
        return {
            "rollladen": e.cover,
            "letzte_meldung": z.letzte_meldung,
            "fenster": lage.fenster,
            "helligkeit": lage.helligkeit,
            "raumtemperatur": lage.raumtemperatur,
            "schlaeft": lage.schlaeft if self.steuerung.schlaf.get(self.sid) else None,
            "vorhersage_max": self.steuerung.vorhersage_max,
            "abschattung_ziel": r.schattenpos(u) if e.abschattung != "nein" else None,
            "im_abschattungsbereich": r.im_bereich(u) if e.abschattung != "nein" else None,
            "abschattungsbereich": f"{(e.himmelsrichtung - e.winkel_links) % 360:.0f}°…"
                                   f"{(e.himmelsrichtung + e.winkel_rechts) % 360:.0f}°",
            "in_abschattung": z.in_abschattung,
            "abschatten_vorgemerkt": z.abschatten_vorgemerkt,
            "abschattung_ende_vorgemerkt": z.ende_vorgemerkt,
            "abschatten_nach_schliessen": z.abschatten_nach_schliessen,
            "nachtschliessen": z.nachtschliessen,
            "pos_vor_abschattung": z.pos_vor_abschattung,
            "pos_vor_geoeffnet": z.pos_vor_geoeffnet,
            "pos_vor_lueften": z.pos_vor_lueften,
            "letzte_abschattungsaktion": z.letzte_aktion.isoformat() if z.letzte_aktion else None,
            "manuell_gefahren": z.sperrzeitpunkt.isoformat() if z.sperrzeitpunkt else None,
            "zaehler_hoch": z.zaehler_hoch,
            "zaehler_runter": z.zaehler_runter,
            "zaehler_hoch_gestern": z.zaehler_hoch_gestern,
            "zaehler_runter_gestern": z.zaehler_runter_gestern,
            "offen_pos": e.offen_pos,
            "geschlossen_pos": e.geschlossen_pos,
            "lueften_pos": e.lueften_pos,
            "geoeffnet_pos": e.geoeffnet_pos,
            "abschattung_pos": e.abschattung_pos,
        }
