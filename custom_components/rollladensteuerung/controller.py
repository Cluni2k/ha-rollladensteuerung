"""Verbindet die Logik (core.py) mit Home Assistant: Zustände lesen, Zeitpläne, Fahrten auslösen."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import date, datetime, timedelta
from typing import Any

from astral import SunDirection, sun as astral_sun

from homeassistant.components.cover import ATTR_CURRENT_POSITION, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_SUPPORTED_FEATURES, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_point_in_time,
    async_track_state_change_event,
    async_track_time_change,
    async_track_time_interval,
)
from homeassistant.helpers.storage import Store
from homeassistant.helpers.sun import get_astral_observer
from homeassistant.util import dt as dt_util

from .const import (
    ABSCHATTUNG_INTERVALL_MIN,
    ASTRO_MODI,
    CONF_ABSTAND,
    CONF_ANWESENHEIT,
    CONF_ASTRO_ABENDS,
    CONF_ASTRO_MORGENS,
    CONF_COVER,
    CONF_ENTITY,
    CONF_FENSTER,
    CONF_FROST_TEMP,
    CONF_HELLIGKEIT_MIN,
    CONF_HELLIGKEITSSENSOR,
    CONF_HORIZONT_ABENDS,
    CONF_HORIZONT_MORGENS,
    CONF_PUSH,
    CONF_RAUMTEMPERATUR,
    CONF_SCHLAF,
    CONF_SONNE,
    CONF_TEMPERATUR,
    CONF_WERKTAG,
    CONF_WETTER,
    DOMAIN,
    EVENT_FAHRT,
    AUSFALL_MINUTEN,
    NACHT_RESET,
    SCHALTER_STANDARD,
    SIGNAL_UPDATE,
    SUB_HELLIGKEIT,
    SUB_ROLLLADEN,
)
from .protokoll import Protokoll
from .core import ABSCHATTEN, LUEFTEN, MANUELL, OEFFNEN, SCHLIESSEN, WARNUNG, GEKIPPT, OFFEN, ZU, Einstellungen, Fahrt, Lage, Rollladen, Umgebung, Zustand

_LOGGER = logging.getLogger(__name__)
_REIHENFOLGE = {ZU: 0, GEKIPPT: 1, OFFEN: 2}
SCHALTER_NAMEN = {"morgens": "Automatik morgens", "abends": "Automatik abends", "abschattung": "Abschattung",
                  "komfort": "Komfort (Fenster)", "partymodus": "Partymodus", "gast": "Gast anwesend",
                  "push_oeffnen": "Push Öffnen", "push_schliessen": "Push Schließen",
                  "push_warnungen": "Push Warnhinweise", "push_lueften": "Push Lüften",
                  "push_abschatten": "Push Abschatten", "push_funktionen": "Push Funktionen",
                  "push_manuell": "Push manuelle Fahrten"}
_DREHGRIFF = {"closed": ZU, "geschlossen": ZU, "tilted": GEKIPPT, "gekippt": GEKIPPT,
              "open": OFFEN, "offen": OFFEN, "geoeffnet": OFFEN, "geöffnet": OFFEN}


def _zahl(hass: HomeAssistant, entity_id: str | None) -> float | None:
    if not entity_id:
        return None
    st = hass.states.get(entity_id)
    if st is None or st.state in (STATE_UNKNOWN, STATE_UNAVAILABLE, ""):
        return None
    try:
        return float(st.state)
    except ValueError:
        return None


class Steuerung:
    """Eine Instanz pro Config-Entry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.cfg: dict[str, Any] = {**entry.data, **entry.options}
        self.signal = SIGNAL_UPDATE.format(entry.entry_id)
        self.store: Store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}")
        self.schalter: dict[str, bool] = dict(SCHALTER_STANDARD)
        self.rolllaeden: dict[str, Rollladen] = {}
        self.fenster: dict[str, list[str]] = {}
        self.helligkeit: dict[str, str | None] = {}      # Rollladen-ID → Sensor-Entity
        self.aktiv: dict[str, bool] = {}                  # Schalter „Automatik“ je Rollladen
        self._timer: dict[str, list] = {}
        self._abmelden: list = []
        self._letzte_abschattung: datetime | None = None
        self.schlaf: dict[str, str | None] = {}
        self.raum: dict[str, str | None] = {}
        self.vorhersage_max: float | None = None
        self._sende_sperre = asyncio.Lock()
        self._letzte_sendung = 0.0
        self._aufgaben: set[asyncio.Task] = set()
        self._zeitbasis: dict[str, str] = {}   # Einstellungen, mit denen die geplanten Zeiten berechnet wurden
        self.protokoll = Protokoll(hass, entry.entry_id)
        self._tagesmeldung: dict[str, str] = {}   # Sammelmeldung Öffnen/Schließen nur einmal am Tag
        self._ausfall: dict[str, Any] = {}        # Entität → Abmelde-Funktion des 15-Minuten-Timers
        self._gewarnt: dict[str, str] = {}        # Entität → Datum der letzten Ausfall-Warnung

        hell = {sid: s.data.get(CONF_ENTITY) for sid, s in entry.subentries.items()
                if s.subentry_type == SUB_HELLIGKEIT}
        for sid, sub in entry.subentries.items():
            if sub.subentry_type != SUB_ROLLLADEN:
                continue
            e = Einstellungen.aus_dict({**sub.data, "name": sub.title, "cover": sub.data[CONF_COVER]})
            self.rolllaeden[sid] = Rollladen(e)
            self.fenster[sid] = list(sub.data.get(CONF_FENSTER) or [])
            self.helligkeit[sid] = hell.get(sub.data.get(CONF_HELLIGKEITSSENSOR) or "")
            self.aktiv[sid] = bool(sub.data.get("aktiv", True))
            self.schlaf[sid] = sub.data.get(CONF_SCHLAF) or None
            self.raum[sid] = sub.data.get(CONF_RAUMTEMPERATUR) or None

    # ------------------------------------------------------------------ Start/Stopp
    async def async_start(self) -> None:
        daten = await self.store.async_load() or {}
        self.schalter.update({k: v for k, v in (daten.get("schalter") or {}).items() if k in self.schalter})
        for sid, r in self.rolllaeden.items():
            r.z = Zustand.laden((daten.get("rolllaeden") or {}).get(sid))
            self.aktiv[sid] = (daten.get("aktiv") or {}).get(sid, self.aktiv[sid])
            self._zeitbasis[sid] = (daten.get("zeitbasis") or {}).get(sid, "")
            r.e.aktiv = self.aktiv[sid]
        self._tagesmeldung = dict(daten.get("tagesmeldung") or {})
        self._gewarnt = dict(daten.get("gewarnt") or {})

        covers = [r.e.cover for r in self.rolllaeden.values()]
        fenster = sorted({f for liste in self.fenster.values() for f in liste})
        hell = sorted({h for h in self.helligkeit.values() if h})
        if covers:
            self._abmelden.append(async_track_state_change_event(self.hass, covers, self._cover_geaendert))
        if fenster:
            self._abmelden.append(async_track_state_change_event(self.hass, fenster, self._fenster_geaendert))
        if hell:
            self._abmelden.append(async_track_state_change_event(self.hass, hell, self._helligkeit_geaendert))
        schlaf = sorted({s for s in self.schlaf.values() if s})
        if schlaf:
            self._abmelden.append(async_track_state_change_event(self.hass, schlaf, self._schlaf_geaendert))
        if self.cfg.get(CONF_WETTER):
            self._abmelden.append(async_track_time_interval(self.hass, self._vorhersage_holen, timedelta(minutes=30)))
            self.hass.async_create_task(self._vorhersage_holen())
        self._abmelden.append(async_track_time_change(
            self.hass, self._nacht, hour=NACHT_RESET[0], minute=NACHT_RESET[1], second=NACHT_RESET[2]))
        self._abmelden.append(async_track_time_interval(
            self.hass, self._abschattung_takt, timedelta(minutes=ABSCHATTUNG_INTERVALL_MIN)))
        # Erreichbarkeit aller beteiligten Sensoren und Rollläden überwachen
        ueberwacht = self._ueberwachte()
        if ueberwacht:
            self._abmelden.append(async_track_state_change_event(self.hass, list(ueberwacht), self._erreichbarkeit))
            for eid in ueberwacht:
                st = self.hass.states.get(eid)
                if st is None or st.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                    self._ausfall_beginnt(eid)
        self.protokoll.eintragen("Zentrale", "info", f"Steuerung gestartet ({len(self.rolllaeden)} Rollläden)")
        for sid in self.rolllaeden:
            # nach einem Neustart die geplanten Zeiten behalten – nach geänderten Einstellungen neu rechnen
            await self.async_zeiten_planen(sid, behalten=self._zeitbasis.get(sid) == self._basis(sid))
        self._melden()

    async def async_stop(self) -> None:
        for aufgabe in list(self._aufgaben):
            aufgabe.cancel()
        for ab in self._ausfall.values():
            if ab:
                ab()
        self._ausfall.clear()
        for ab in self._abmelden:
            ab()
        self._abmelden.clear()
        for liste in self._timer.values():
            for ab in liste:
                ab()
        self._timer.clear()
        await self._speichern_jetzt()

    @callback
    def _speichern(self) -> None:
        self.store.async_delay_save(self._daten, 5)

    async def _speichern_jetzt(self) -> None:
        await self.store.async_save(self._daten())

    def _daten(self) -> dict:
        return {"schalter": self.schalter, "aktiv": self.aktiv, "zeitbasis": self._zeitbasis,
                "tagesmeldung": self._tagesmeldung, "gewarnt": self._gewarnt,
                "rolllaeden": {sid: r.z.speichern() for sid, r in self.rolllaeden.items()}}

    @callback
    def _melden(self) -> None:
        self._speichern()
        async_dispatcher_send(self.hass, self.signal)

    # ------------------------------------------------------------------ Lage und Umgebung
    def umgebung(self) -> Umgebung:
        jetzt = dt_util.now()
        anw = None
        if (e := self.cfg.get(CONF_ANWESENHEIT)) and (st := self.hass.states.get(e)):
            if st.state in ("on", "home"):
                anw = True
            elif st.state in ("off", "not_home"):
                anw = False
        az = el = None
        if st := self.hass.states.get(self.cfg.get(CONF_SONNE) or "sun.sun"):
            az = st.attributes.get("azimuth")
            el = st.attributes.get("elevation")
        return Umgebung(
            jetzt=jetzt, anwesend=anw, temperatur=_zahl(self.hass, self.cfg.get(CONF_TEMPERATUR)),
            azimut=az, elevation=el, gast=self.schalter["gast"], party=self.schalter["partymodus"],
            auto_morgens=self.schalter["morgens"], auto_abends=self.schalter["abends"],
            auto_abschattung=self.schalter["abschattung"], auto_komfort=self.schalter["komfort"],
            frost_temp=float(self.cfg.get(CONF_FROST_TEMP, 0)), vorhersage_max=self.vorhersage_max)

    def lage(self, sid: str) -> Lage:
        r = self.rolllaeden[sid]
        st = self.hass.states.get(r.e.cover)
        pos = None
        faehrt = False
        if st is not None and st.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            pos = st.attributes.get(ATTR_CURRENT_POSITION)
            if pos is None:
                pos = 100 if st.state == "open" else 0 if st.state == "closed" else None
            faehrt = st.state in ("opening", "closing")
        fenster = None
        zweistufig = True
        for eid in self.fenster.get(sid, []):
            fst = self.hass.states.get(eid)
            if fst is None or fst.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                continue
            if eid.startswith("binary_sensor."):
                w = OFFEN if fst.state == "on" else ZU
            else:
                w = _DREHGRIFF.get(fst.state.lower())
                if w is None:
                    continue
                zweistufig = False
            if fenster is None or _REIHENFOLGE[w] > _REIHENFOLGE[fenster]:
                fenster = w
        schlaf = self.hass.states.get(self.schlaf.get(sid) or "")
        return Lage(position=None if pos is None else int(pos), faehrt=faehrt, fenster=fenster,
                    zweistufig=zweistufig, helligkeit=_zahl(self.hass, self.helligkeit.get(sid)),
                    raumtemperatur=_zahl(self.hass, self.raum.get(sid)),
                    schlaeft=schlaf is not None and schlaf.state in ("on", "home"))

    # ------------------------------------------------------------------ Fahren
    async def _ausfuehren(self, sid: str, fahrten: list[Fahrt]) -> None:
        """Fahrten einreihen – sie werden mit Abstand nacheinander gesendet (schont den Funk-Duty-Cycle)."""
        for f in fahrten:
            aufgabe = self.hass.async_create_task(self._senden(sid, f))
            self._aufgaben.add(aufgabe)
            aufgabe.add_done_callback(self._aufgaben.discard)
        self._verarbeiten(sid)
        self._melden()

    # ------------------------------------------------------------------ Protokoll und Push
    @callback
    def _verarbeiten(self, sid: str) -> None:
        """Meldungen der Logik ins Protokoll schreiben und – je nach Push-Schalter – verschicken."""
        r = self.rolllaeden.get(sid)
        if r is None:
            return
        for art, text, _ziel in r.abholen():
            self.protokoll.eintragen(r.e.name, art, text)
            if art == LUEFTEN and self.schalter["push_lueften"]:
                self._push(f"{r.e.name}: {text}")
            elif art == ABSCHATTEN and self.schalter["push_abschatten"] and "→" in text:
                self._push(f"{r.e.name}: {text}")
            elif art == WARNUNG and self.schalter["push_warnungen"]:
                self._push(f"⚠️ {r.e.name}: {text}")
            elif art == MANUELL and self.schalter["push_manuell"]:
                self._push(f"{r.e.name}: {text}")
            elif art in (OEFFNEN, SCHLIESSEN) and "→" in text:
                self._sammelmeldung(art)

    @callback
    def _sammelmeldung(self, art: str) -> None:
        """Öffnen/Schließen: eine Nachricht für alle Rollläden, beim ersten Rollladen des Tages."""
        heute = dt_util.now().date().isoformat()
        schalter = "push_oeffnen" if art == OEFFNEN else "push_schliessen"
        if self._tagesmeldung.get(art) == heute:
            return
        self._tagesmeldung[art] = heute
        if not self.schalter[schalter]:
            return
        feld, modus = ("hoch_zeit", "modus_hoch") if art == OEFFNEN else ("runter_zeit", "modus_runter")
        jetzt = dt_util.now()
        zeiten = [getattr(x.z, feld) for sid, x in self.rolllaeden.items()
                  if self.aktiv.get(sid) and getattr(x.e, modus) != "aus" and getattr(x.z, feld)
                  and getattr(x.z, feld).date() == jetzt.date()]
        bis = max(zeiten, default=jetzt)
        anzahl = max(len(zeiten), 1)
        if art == OEFFNEN:
            text = f"Die Rollläden werden geöffnet ({anzahl} Rollläden, bis ca. {bis:%H:%M} Uhr)."
        else:
            text = f"Die Rollläden werden geschlossen ({anzahl} Rollläden, bis ca. {bis:%H:%M} Uhr)."
        self._push(text)

    @callback
    def _push(self, text: str) -> None:
        dienst = self.cfg.get(CONF_PUSH)
        if not dienst or "." not in dienst:
            return
        domain, name = dienst.split(".", 1)
        daten = {"title": "Rollladensteuerung", "message": text}

        async def _senden() -> None:
            try:
                await self.hass.services.async_call(domain, name, daten, blocking=False)
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Push über %s fehlgeschlagen: %s", dienst, err)
        self.hass.async_create_task(_senden())

    @callback
    def funktion(self, text: str, rollladen: str = "Zentrale", push: bool = True) -> None:
        self.protokoll.eintragen(rollladen, "funktion", text)
        if push and self.schalter["push_funktionen"]:
            self._push(text if rollladen == "Zentrale" else f"{rollladen}: {text}")

    # ------------------------------------------------------------------ Erreichbarkeit
    def _ueberwachte(self) -> dict[str, str]:
        """Entität → wofür sie gebraucht wird (für die Warnung)."""
        aus: dict[str, str] = {}
        for sid, r in self.rolllaeden.items():
            aus[r.e.cover] = f"Rollladen {r.e.name}"
            for f in self.fenster.get(sid, []):
                aus.setdefault(f, f"Fensterkontakt ({r.e.name})")
            for eid, was in ((self.helligkeit.get(sid), "Helligkeitssensor"), (self.raum.get(sid), "Raumtemperatur"),
                             (self.schlaf.get(sid), "Schlafschalter")):
                if eid:
                    aus.setdefault(eid, f"{was} ({r.e.name})" if was != "Helligkeitssensor" else was)
        if t := self.cfg.get(CONF_TEMPERATUR):
            aus.setdefault(t, "Außentemperatur")
        return aus

    def _name(self, eid: str) -> str:
        st = self.hass.states.get(eid)
        return (st.attributes.get("friendly_name") if st else None) or eid

    @callback
    def _ausfall_beginnt(self, eid: str) -> None:
        if eid in self._ausfall:
            return

        @callback
        def _pruefen(_now) -> None:
            self._ausfall[eid] = None
            st = self.hass.states.get(eid)
            if st is not None and st.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                return
            was = self._ueberwachte().get(eid, eid)
            text = f"{was} „{self._name(eid)}“ ist seit {AUSFALL_MINUTEN} Minuten nicht erreichbar."
            self.protokoll.eintragen("Zentrale", WARNUNG, text)
            heute = dt_util.now().date().isoformat()
            if self._gewarnt.get(eid) != heute:   # höchstens eine Warnung pro Tag und Entität
                self._gewarnt[eid] = heute
                if self.schalter["push_warnungen"]:
                    self._push(f"⚠️ {text}")
                self._speichern()
        self._ausfall[eid] = async_call_later(self.hass, AUSFALL_MINUTEN * 60, _pruefen)

    async def _erreichbarkeit(self, event: Event) -> None:
        eid = event.data["entity_id"]
        neu = event.data.get("new_state")
        weg = neu is None or neu.state in (STATE_UNKNOWN, STATE_UNAVAILABLE)
        if weg:
            self._ausfall_beginnt(eid)
            return
        if eid in self._ausfall:
            ab = self._ausfall.pop(eid)
            if ab:
                ab()   # kam innerhalb der 15 Minuten zurück – keine Meldung
            elif self._gewarnt.get(eid):
                text = f"{self._ueberwachte().get(eid, eid)} „{self._name(eid)}“ ist wieder erreichbar."
                self.protokoll.eintragen("Zentrale", "info", text)
                if self.schalter["push_warnungen"]:
                    self._push(text)
                self._gewarnt.pop(eid, None)
                self._speichern()

    @callback
    def _ziele_pruefen(self) -> None:
        """Hat ein Rollladen sein Ziel nicht erreicht (Funkstörung, Hindernis, Aktor)? Dann warnen."""
        jetzt = dt_util.now()
        for sid, r in self.rolllaeden.items():
            if r.z.erwartet is None or r.z.erwartet_bis is None or jetzt <= r.z.erwartet_bis + timedelta(minutes=1):
                continue
            ziel, r.z.erwartet = r.z.erwartet, None
            pos = self.lage(sid).position
            if pos is not None and abs(pos - ziel) > 5:
                r._melde(WARNUNG, f"hat {ziel} % nicht erreicht (steht auf {pos} %)")
                self._verarbeiten(sid)

    async def _senden(self, sid: str, f: Fahrt) -> None:
        r = self.rolllaeden.get(sid)
        if r is None:
            return
        abstand = float(self.cfg.get(CONF_ABSTAND, 5))
        async with self._sende_sperre:
            warten = abstand - (time.monotonic() - self._letzte_sendung)
            if warten > 0:
                await asyncio.sleep(warten)
            self._letzte_sendung = time.monotonic()
            r.z.erwartet_bis = dt_util.now() + timedelta(minutes=3)
            st = self.hass.states.get(r.e.cover)
            merkmale = (st.attributes.get(ATTR_SUPPORTED_FEATURES, 0) if st else 0) or 0
            _LOGGER.info("%s: %s → %s %%", r.e.name, f.grund, f.position)
            if merkmale & CoverEntityFeature.SET_POSITION:
                await self.hass.services.async_call(
                    "cover", "set_cover_position", {"entity_id": r.e.cover, "position": f.position},
                    blocking=False)
            else:
                await self.hass.services.async_call(
                    "cover", "open_cover" if f.position >= 50 else "close_cover",
                    {"entity_id": r.e.cover}, blocking=False)
            self.hass.bus.async_fire(EVENT_FAHRT, {"rollladen": r.e.name, "entity_id": r.e.cover,
                                                   "position": f.position, "grund": f.grund})

    # ------------------------------------------------------------------ Zeitpläne
    async def _werktag(self, tag: date) -> bool:
        eid = self.cfg.get(CONF_WERKTAG)
        heute = dt_util.now().date()
        if eid and tag == heute and (st := self.hass.states.get(eid)) and st.state in ("on", "off"):
            return st.state == "on"
        if eid and self.hass.services.has_service("workday", "check_date"):
            try:
                antwort = await self.hass.services.async_call(
                    "workday", "check_date", {"entity_id": eid, "check_date": tag},
                    blocking=True, return_response=True)
                return bool(antwort[eid]["workday"])
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("workday.check_date fehlgeschlagen: %s", err)
        return tag.weekday() < 5

    def _astro(self, tag: date, morgens: bool) -> datetime | None:
        modus = self.cfg.get(CONF_ASTRO_MORGENS if morgens else CONF_ASTRO_ABENDS, "real")
        hoehe = ASTRO_MODI.get(modus, -0.833)
        if hoehe is None:
            hoehe = float(self.cfg.get(CONF_HORIZONT_MORGENS if morgens else CONF_HORIZONT_ABENDS, 0))
        try:
            t = astral_sun.time_at_elevation(
                get_astral_observer(self.hass), hoehe, tag,
                SunDirection.RISING if morgens else SunDirection.SETTING, tzinfo=dt_util.UTC)
        except ValueError:
            return None
        return dt_util.as_local(t)

    def _basis(self, sid: str) -> str:
        """Alles, was die Öffnen-/Schließzeit beeinflusst – ändert es sich, wird neu gerechnet."""
        e = self.rolllaeden[sid].e
        werte = {k: self.cfg.get(k) for k in (CONF_ASTRO_MORGENS, CONF_ASTRO_ABENDS, CONF_HORIZONT_MORGENS,
                                              CONF_HORIZONT_ABENDS, CONF_WERKTAG, CONF_SONNE)}
        werte.update({k: getattr(e, k) for k in ("hoch", "runter", "zeit_hoch_frueh", "zeit_hoch_spaet",
                                                 "zeit_hoch_we", "zeit_runter_frueh", "zeit_runter_spaet",
                                                 "offset_morgens", "offset_abends", "zufall_minuten")})
        return json.dumps(werte, sort_keys=True, default=str)

    async def async_zeiten_planen(self, sid: str, behalten: bool = False) -> None:
        """Nächste Öffnen- und Schließzeit dieses Rollladens bestimmen und Timer stellen."""
        r = self.rolllaeden[sid]
        jetzt = dt_util.now()
        tz = dt_util.get_default_time_zone()
        neu: dict[str, datetime] = {}
        for art in ("hoch", "runter"):
            alt = getattr(r.z, f"{art}_zeit")
            if behalten and alt is not None and alt > jetzt + timedelta(seconds=30) \
                    and alt.date() <= jetzt.date() + timedelta(days=1):
                neu[art] = alt
                continue
            for plus in (0, 1, 2):
                tag = jetzt.date() + timedelta(days=plus)
                hoch, runter = r.zeiten_berechnen(
                    tag, await self._werktag(tag), self._astro(tag, True), self._astro(tag, False), tz)
                t = hoch if art == "hoch" else runter
                if t > jetzt + timedelta(minutes=1):
                    neu[art] = t
                    break
        r.z.hoch_zeit = neu.get("hoch")
        r.z.runter_zeit = neu.get("runter")
        self._zeitbasis[sid] = self._basis(sid)
        for ab in self._timer.pop(sid, []):
            ab()
        timer = []
        if r.z.hoch_zeit:
            timer.append(async_track_point_in_time(self.hass, self._timer_cb(sid, "hoch"), r.z.hoch_zeit))
        if r.z.runter_zeit:
            timer.append(async_track_point_in_time(self.hass, self._timer_cb(sid, "runter"), r.z.runter_zeit))
        self._timer[sid] = timer
        self._melden()

    def _timer_cb(self, sid: str, art: str):
        async def _ausloesen(_now: datetime) -> None:
            r = self.rolllaeden.get(sid)
            if r is None:
                return
            u, lage = self.umgebung(), self.lage(sid)
            fahrten = r.oeffnen(u, lage) if art == "hoch" else r.schliessen(u, lage)
            if not fahrten and r.z.letzte_meldung:
                _LOGGER.info("%s: %s", r.e.name, r.z.letzte_meldung)
            await self._ausfuehren(sid, fahrten)
            setattr(r.z, f"{art}_zeit", None)
            await self.async_zeiten_planen(sid)
        return _ausloesen

    async def async_alle_neu_planen(self) -> None:
        for sid in self.rolllaeden:
            await self.async_zeiten_planen(sid)

    async def _nacht(self, _now: datetime) -> None:
        for r in self.rolllaeden.values():
            r.nacht_reset()
        await self.protokoll.bereinigen()
        await self.async_alle_neu_planen()

    # ------------------------------------------------------------------ Ereignisse
    async def _cover_geaendert(self, event: Event) -> None:
        neu = event.data.get("new_state")
        if neu is None or neu.state in ("opening", "closing", STATE_UNKNOWN, STATE_UNAVAILABLE):
            return
        alt = event.data.get("old_state")
        # nach einem Neustart oder Verbindungsabbruch meldet sich der Rollladen nur zurück – keine Fahrt
        if alt is None or alt.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return
        pos_neu = neu.attributes.get(ATTR_CURRENT_POSITION)
        pos_alt = alt.attributes.get(ATTR_CURRENT_POSITION)
        if pos_neu is None:
            pos_neu = 100 if neu.state == "open" else 0 if neu.state == "closed" else None
        if pos_neu == pos_alt and alt.state == neu.state:
            return
        u = self.umgebung()
        for sid, r in self.rolllaeden.items():
            if r.e.cover == neu.entity_id:
                r.positionsmeldung(u, pos_neu)
                self._verarbeiten(sid)
        self._melden()

    async def _fenster_geaendert(self, event: Event) -> None:
        eid = event.data["entity_id"]
        neu, alt = event.data.get("new_state"), event.data.get("old_state")
        if neu is None or neu.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return
        if alt is not None and alt.state == neu.state:
            return
        u = self.umgebung()
        for sid, liste in self.fenster.items():
            if eid in liste:
                await self._ausfuehren(sid, self.rolllaeden[sid].fenster_event(u, self.lage(sid)))

    async def _helligkeit_geaendert(self, event: Event) -> None:
        jetzt = dt_util.now()
        if self._letzte_abschattung and (jetzt - self._letzte_abschattung).total_seconds() < 30:
            return
        await self.async_abschattung()

    async def _abschattung_takt(self, _now: datetime) -> None:
        self._ziele_pruefen()
        await self.async_abschattung()

    async def async_abschattung(self) -> None:
        self._letzte_abschattung = dt_util.now()
        minimum = float(self.cfg.get(CONF_HELLIGKEIT_MIN, 500))
        werte = [_zahl(self.hass, h) for h in set(self.helligkeit.values()) if h]
        if not any(w is not None and w > minimum for w in werte):
            return
        u = self.umgebung()
        for sid, r in self.rolllaeden.items():
            await self._ausfuehren(sid, r.abschattung(u, self.lage(sid)))

    async def async_schalter(self, name: str, wert: bool) -> None:
        alt = self.schalter.get(name)
        self.schalter[name] = wert
        if alt != wert:
            bezeichnung = SCHALTER_NAMEN.get(name, name)
            # Push-Schalter selbst nur protokollieren, alle anderen Funktionen auch melden
            self.funktion(f"{bezeichnung} {'eingeschaltet' if wert else 'ausgeschaltet'}",
                          push=not name.startswith("push_"))
        if name == "partymodus" and alt and not wert:
            u = self.umgebung()
            for sid, r in self.rolllaeden.items():
                await self._ausfuehren(sid, r.party_ende(u, self.lage(sid)))
        self._melden()

    async def async_alle(self, art: str) -> None:
        """„Alle öffnen/schließen/lüften/abschatten“ – jeder Rollladen auf seine eigene Position, gestaffelt.

        Abschatten: nur Rollläden mit eingeschalteter Abschattung, auf ihre (ggf. dynamische) Abschattungsposition,
        und nur nach unten – ein geschlossener Rollladen wird dafür nicht geöffnet.
        """
        u = self.umgebung()
        for sid, r in self.rolllaeden.items():
            if art == "abschatten" and r.e.abschattung == "nein":
                continue
            ziel, grund = {"oeffnen": (r.e.offen_pos, "Alle öffnen"),
                           "schliessen": (r.e.geschlossen_pos, "Alle schließen"),
                           "lueften": (r.e.lueften_pos, "Alle lüften"),
                           "abschatten": (r.schattenpos(u), "Alle abschatten")}[art]
            lage = self.lage(sid)
            if lage.position is not None and abs(lage.position - ziel) <= 2:
                continue
            if art == "abschatten" and lage.position is not None and lage.position < ziel:
                continue
            await self._ausfuehren(sid, r.fahren(u, lage, ziel, grund))

    async def _schlaf_geaendert(self, event: Event) -> None:
        neu, alt = event.data.get("new_state"), event.data.get("old_state")
        if neu is None or alt is None or neu.state == alt.state or neu.state in ("on", "home"):
            return
        u = self.umgebung()
        for sid, eid in self.schlaf.items():
            if eid == event.data["entity_id"]:
                await self._ausfuehren(sid, self.rolllaeden[sid].aufgewacht(u, self.lage(sid)))

    async def _vorhersage_holen(self, _now=None) -> None:
        eid = self.cfg.get(CONF_WETTER)
        if not eid:
            return
        try:
            antwort = await self.hass.services.async_call(
                "weather", "get_forecasts", {"entity_id": eid, "type": "daily"}, blocking=True, return_response=True)
            liste = (antwort or {}).get(eid, {}).get("forecast") or []
            heute = dt_util.now().date()
            werte = [t.get("temperature") for t in liste
                     if t.get("temperature") is not None and dt_util.as_local(dt_util.parse_datetime(t["datetime"])).date() == heute]
            if not werte and liste and liste[0].get("temperature") is not None:
                werte = [liste[0]["temperature"]]
            self.vorhersage_max = float(max(werte)) if werte else None
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Wettervorhersage nicht abrufbar: %s", err)
        self._melden()

    async def async_rollladen_aktiv(self, sid: str, wert: bool) -> None:
        if self.aktiv.get(sid) != wert:
            self.funktion(f"Automatik {'eingeschaltet' if wert else 'ausgeschaltet'}", self.rolllaeden[sid].e.name)
        self.aktiv[sid] = wert
        self.rolllaeden[sid].e.aktiv = wert
        self._melden()
