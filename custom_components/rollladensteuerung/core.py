"""Rollladensteuerung – die eigentliche Logik, ohne Home-Assistant-Abhängigkeit (testbar).

Nachbau der FHEM-Rollladensteuerung (99_myUtils_Shutter.pm, Bernd Hermanns & Matthias Frintrop):
Öffnen/Schließen nach Astro oder Zeit, Komfortfunktionen am Fenster (Lüften, Geöffnet, Nachtschließen,
Abschatten nach dem Schließen), Abschattung nach Sonnenstand und Helligkeit mit Vormerkung,
Sperrzeiten, Frostschutz, Partymodus, Gästezimmer und Aussperrschutz.

Positionen: 0 = geschlossen, 100 = offen (wie Home Assistant und Homematic „pct“).
Jede Methode ändert nur den Zustand und gibt die gewünschten Fahrten zurück; gefahren wird außerhalb.
"""
from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass, field, fields
from datetime import date, datetime, time, timedelta

TOLERANZ = 3  # Prozentpunkte – Aktoren melden gern 49 statt 50

ZU, GEKIPPT, OFFEN = "closed", "tilted", "open"

MODI = ("immer", "bei_abwesenheit", "bei_anwesenheit", "aus")
ABSCHATTUNG_MODI = ("nein", "ja", "verspaetet", "bei_abwesenheit", "bei_anwesenheit")


def gleich(a: float | None, b: float | None, toleranz: float = TOLERANZ) -> bool:
    return a is not None and b is not None and abs(a - b) <= toleranz


def winkel_abweichung(sonne: float, fenster: float) -> float:
    """Abweichung der Sonne von der Fensterrichtung in Grad, -180…180 (negativ = links/früher)."""
    return (sonne - fenster + 180) % 360 - 180


def als_zeit(wert: str | time) -> time:
    if isinstance(wert, time):
        return wert
    teile = [int(x) for x in str(wert).split(":")]
    while len(teile) < 3:
        teile.append(0)
    return time(teile[0], teile[1], teile[2])


@dataclass
class Einstellungen:
    """Einstellungen eines Rollladens (in FHEM die Attribute „Auto_…“)."""

    name: str
    cover: str
    aktiv: bool = True                      # Rollladensteuerung ja/nein
    modus_hoch: str = "immer"               # Auto_Modus_hoch
    modus_runter: str = "immer"             # Auto_Modus_runter
    hoch: str = "astro"                     # Auto_hoch: astro/zeit
    runter: str = "astro"                   # Auto_runter: astro/zeit
    zeit_hoch_frueh: str = "07:30:00"
    zeit_hoch_spaet: str = "09:00:00"
    zeit_hoch_we: str = "09:30:00"          # Wochenende/Feiertag/Urlaub
    zeit_runter_frueh: str = "16:30:00"
    zeit_runter_spaet: str = "21:30:00"
    offset_morgens: int = 0
    offset_abends: int = 0
    zufall_minuten: int = 20
    offen_pos: int = 100
    geschlossen_pos: int = 0
    lueften_pos: int = 30
    geoeffnet_pos: int = 80
    pos_nach_komfort_oeffnen: int = -1      # -1 vorherige Position, -2 Geöffnet-Position, sonst Wert
    luft_fenster_offen: bool = True
    aussperrschutz: bool = False
    frostschutz: bool = False               # morgens nicht öffnen bei Frost
    partymodus: bool = False                # bei Party abends nicht schließen
    gaestezimmer: bool = False              # bei Gast morgens nicht öffnen
    abschattung: str = "nein"
    himmelsrichtung: float = 178
    winkel_links: float = 85
    winkel_rechts: float = 85
    min_elevation: float = 0
    schwelle_sonnig: float = 60000
    schwelle_wolkig: float = 40000
    wartezeit: int = 20
    sperrzeit_nach_manuell: int = 20
    sperrzeit_vor_nacht: int = 45
    min_temp_aussen: float = 18
    abschattung_pos: int = 30
    pos_nach_abschattung: int = -1          # -1 = Position vor der Abschattung
    schnell_oeffnen: bool = False
    schnell_schliessen: bool = False
    # Erweiterungen gegenüber FHEM
    min_temp_vorhersage: float | None = None    # nur abschatten, wenn heute mehr erwartet wird
    min_temp_innen: float = 23                  # mit Raumtemperatur: darunter offen lassen (Sonne heizt mit)
    abschattung_dynamisch: bool = False         # Position nach Sonnenhöhe statt fest
    fensterhoehe: float = 130                   # cm, Höhe der Fensteröffnung
    bruestung: float = 90                       # cm, Abstand Fensterunterkante zum Boden
    eindringtiefe: float = 50                   # cm, so weit darf die Sonne in den Raum scheinen

    @classmethod
    def aus_dict(cls, daten: dict) -> "Einstellungen":
        namen = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in daten.items() if k in namen})


@dataclass
class Zustand:
    """Merker der Steuerung (in FHEM die Readings „Automatik_…“)."""

    hoch_zeit: datetime | None = None
    runter_zeit: datetime | None = None
    in_abschattung: bool = False
    abschatten_vorgemerkt: bool = False
    ende_vorgemerkt: bool = False
    abschatten_nach_schliessen: bool = False
    letzte_aktion: datetime | None = None       # Automatik_Abschattung_letzte_Uhrzeit
    sperrzeitpunkt: datetime | None = None      # letzte manuelle Fahrt
    pos_vor_abschattung: int = -1
    pos_vor_geoeffnet: int = -1
    pos_vor_lueften: int = -1
    nachtschliessen: bool = False
    party_level: int = -1                       # nach der Party anzufahren
    erwartet: int | None = None                 # Ziel der letzten automatischen Fahrt
    erwartet_bis: datetime | None = None
    zaehler_hoch: int = 0
    zaehler_runter: int = 0
    zaehler_hoch_gestern: int = 0
    zaehler_runter_gestern: int = 0
    letzte_meldung: str = ""
    oeffnen_nachholen: bool = False             # morgens nicht geöffnet, weil jemand schlief
    abschattung_ziel: int = -1                  # aktuell angefahrene Abschattungsposition

    def speichern(self) -> dict:
        daten = asdict(self)
        for k, v in daten.items():
            if isinstance(v, datetime):
                daten[k] = v.isoformat()
        return daten

    @classmethod
    def laden(cls, daten: dict | None) -> "Zustand":
        z = cls()
        for f in fields(cls):
            if not daten or f.name not in daten:
                continue
            v = daten[f.name]
            if isinstance(v, str) and f.name in ("hoch_zeit", "runter_zeit", "letzte_aktion",
                                                 "sperrzeitpunkt", "erwartet_bis"):
                try:
                    v = datetime.fromisoformat(v)
                except ValueError:
                    v = None
            setattr(z, f.name, v)
        return z


@dataclass
class Umgebung:
    """Was gerade im Haus und draußen los ist (für alle Rollläden gleich)."""

    jetzt: datetime
    anwesend: bool | None = None
    temperatur: float | None = None
    azimut: float | None = None
    elevation: float | None = None
    gast: bool = False
    party: bool = False
    auto_morgens: bool = True
    auto_abends: bool = True
    auto_abschattung: bool = True
    auto_komfort: bool = True
    frost_temp: float = 0
    vorhersage_max: float | None = None         # heutige Höchsttemperatur laut Wettervorhersage


@dataclass
class Lage:
    """Was gerade an diesem Rollladen los ist."""

    position: int | None
    faehrt: bool = False
    fenster: str | None = None      # closed/tilted/open, None = kein oder unbekannter Kontakt
    zweistufig: bool = True         # einfacher Kontakt: „offen“ zählt wie „gekippt“
    helligkeit: float | None = None
    raumtemperatur: float | None = None
    schlaeft: bool = False


@dataclass
class Fahrt:
    position: int
    grund: str


@dataclass
class Rollladen:
    e: Einstellungen
    z: Zustand = field(default_factory=Zustand)

    # ------------------------------------------------------------------ Hilfen
    def _fenster(self, lage: Lage) -> str:
        f = lage.fenster or ZU
        if lage.zweistufig and f == OFFEN:
            return GEKIPPT
        return f

    def _modus_passt(self, modus: str, u: Umgebung) -> bool:
        if modus == "immer":
            return True
        if modus == "bei_abwesenheit":
            return u.anwesend is False
        if modus == "bei_anwesenheit":
            return u.anwesend is True
        return False

    def _fahrt(self, u: Umgebung, lage: Lage, ziel: int, grund: str) -> list[Fahrt]:
        ziel = int(max(0, min(100, ziel)))
        # Aussperrschutz: bei offener Tür nie automatisch weiter herunterfahren
        if (self.e.aussperrschutz and lage.fenster not in (None, ZU)
                and lage.position is not None and ziel < lage.position):
            self.z.letzte_meldung = f"{grund}: wegen Aussperrschutz nicht gefahren (Tür offen)"
            return []
        self.z.erwartet = ziel
        self.z.erwartet_bis = u.jetzt + timedelta(minutes=3)
        self.z.letzte_meldung = f"{grund} → {ziel} %"
        return [Fahrt(ziel, grund)]

    def schattenpos(self, u: Umgebung) -> int:
        """Abschattungsposition – fest oder dynamisch nach Sonnenstand (nie dunkler als die feste)."""
        fest = self.e.abschattung_pos
        if not self.e.abschattung_dynamisch or u.elevation is None or u.azimut is None or u.elevation <= 0:
            return fest
        abweichung = abs(winkel_abweichung(u.azimut, self.e.himmelsrichtung))
        if abweichung >= 90:
            return fest
        # Sonnenstrahl durch die Oberkante der Öffnung trifft den Boden in d = H / tan(h) · cos(Abweichung)
        hoehe_max = self.e.eindringtiefe * math.tan(math.radians(u.elevation)) / max(math.cos(math.radians(abweichung)), 0.1)
        anteil = (hoehe_max - self.e.bruestung) / max(self.e.fensterhoehe, 1)
        pos = int(round(max(0.0, min(1.0, anteil)) * 100 / 5) * 5)
        return max(pos, fest)

    def _ziel(self) -> int:
        return self.z.abschattung_ziel if self.z.abschattung_ziel >= 0 else self.e.abschattung_pos

    def fahren(self, u: Umgebung, lage: Lage, ziel: int, grund: str) -> list[Fahrt]:
        """Von außen ausgelöste Fahrt (z. B. „Alle öffnen“) – mit Aussperrschutz, Merker bleiben."""
        return self._fahrt(u, lage, ziel, grund)

    def _reset_abschattung(self) -> None:
        self.z.abschatten_vorgemerkt = False
        self.z.ende_vorgemerkt = False
        self.z.in_abschattung = False
        self.z.pos_vor_abschattung = -1
        self.z.abschattung_ziel = -1

    def _minuten_seit(self, u: Umgebung, t: datetime | None) -> float:
        if t is None:
            return 10_000
        return (u.jetzt - t).total_seconds() / 60

    # ------------------------------------------------------------------ Zeiten
    def zeiten_berechnen(self, tag: date, werktag: bool, aufgang: datetime | None,
                         untergang: datetime | None, tz, rnd: random.Random | None = None
                         ) -> tuple[datetime, datetime]:
        """Öffnen-/Schließzeit für einen Tag (Auto_Rol_group_at)."""
        rnd = rnd or random
        z = max(0, self.e.zufall_minuten) * 60

        def um(t: str) -> datetime:
            return datetime.combine(tag, als_zeit(t), tz)

        def plus(sek: float) -> timedelta:
            return timedelta(seconds=sek)

        def begrenzen(t: datetime, unten: datetime, oben: datetime) -> datetime:
            return max(unten, min(oben, t))

        if not werktag:
            hoch = um(self.e.zeit_hoch_we) + plus(rnd.uniform(0, z))
        elif self.e.hoch == "astro" and aufgang is not None:
            hoch = begrenzen(aufgang + plus(rnd.uniform(-z, z)),
                             um(self.e.zeit_hoch_frueh) + plus(rnd.uniform(0, z)),
                             um(self.e.zeit_hoch_spaet) - plus(rnd.uniform(0, z)))
        else:
            hoch = um(self.e.zeit_hoch_frueh) + plus(rnd.uniform(0, z))
        hoch += timedelta(minutes=self.e.offset_morgens)

        if self.e.runter == "astro" and untergang is not None:
            runter = begrenzen(untergang + plus(rnd.uniform(-z, z)),
                               um(self.e.zeit_runter_frueh) + plus(rnd.uniform(0, z)),
                               um(self.e.zeit_runter_spaet) - plus(rnd.uniform(0, z)))
        else:
            runter = um(self.e.zeit_runter_spaet) - plus(rnd.uniform(0, z))
        runter += timedelta(minutes=self.e.offset_abends)
        return hoch.replace(microsecond=0), runter.replace(microsecond=0)

    def nacht_reset(self) -> None:
        """Täglich um 03:05: Merker zurücksetzen, Zähler weiterschieben."""
        self._reset_abschattung()
        self.z.letzte_aktion = None
        self.z.sperrzeitpunkt = None
        self.z.abschatten_nach_schliessen = False
        self.z.pos_vor_geoeffnet = -1
        self.z.pos_vor_lueften = -1
        self.z.nachtschliessen = False
        self.z.oeffnen_nachholen = False
        self.z.zaehler_hoch_gestern = self.z.zaehler_hoch
        self.z.zaehler_runter_gestern = self.z.zaehler_runter
        self.z.zaehler_hoch = 0
        self.z.zaehler_runter = 0

    # ------------------------------------------------------------------ Morgens
    def oeffnen(self, u: Umgebung, lage: Lage) -> list[Fahrt]:
        """Auto_Rollladen_oeffnen."""
        self.z.nachtschliessen = False
        if not u.auto_morgens or not self.e.aktiv:
            return []
        if self.e.modus_hoch == "aus":
            self.z.letzte_meldung = "Öffnen: ausgeschaltet"
            return []
        if u.gast and self.e.gaestezimmer:
            self.z.letzte_meldung = "Öffnen: Gast anwesend"
            return []
        if lage.schlaeft:
            self.z.oeffnen_nachholen = True
            self.z.letzte_meldung = "Öffnen: es wird noch geschlafen – öffnet beim Aufstehen"
            return []
        if self.e.frostschutz and u.temperatur is not None and u.temperatur <= u.frost_temp:
            self.z.letzte_meldung = f"Öffnen: Frostschutz ({u.temperatur:.1f} °C)"
            return []
        if not self._modus_passt(self.e.modus_hoch, u):
            self.z.letzte_meldung = "Öffnen: Anwesenheit passt nicht"
            return []
        if lage.position is not None and lage.position >= self.e.offen_pos - TOLERANZ:
            self.z.letzte_meldung = "Öffnen: steht schon höher"
            return []
        self.z.oeffnen_nachholen = False
        self._reset_abschattung()
        self.z.pos_vor_geoeffnet = -1
        self.z.pos_vor_lueften = -1
        return self._fahrt(u, lage, self.e.offen_pos, "Morgens öffnen")

    def aufgewacht(self, u: Umgebung, lage: Lage) -> list[Fahrt]:
        """Schlafschalter aus: das morgendliche Öffnen nachholen (nur wenn es ausgefallen war)."""
        if not self.z.oeffnen_nachholen:
            return []
        self.z.oeffnen_nachholen = False
        lage.schlaeft = False
        return self.oeffnen(u, lage)

    # ------------------------------------------------------------------ Abends
    def schliessen(self, u: Umgebung, lage: Lage) -> list[Fahrt]:
        """Auto_Rollladen_schliessen."""
        self.z.oeffnen_nachholen = False
        if not u.auto_abends or not self.e.aktiv:
            return []
        if self.e.partymodus and u.party:
            self.z.party_level = self.e.geschlossen_pos
            self.z.letzte_meldung = "Schließen: Partymodus – wird danach nachgeholt"
            return []
        if self.e.modus_runter == "aus":
            self.z.letzte_meldung = "Schließen: ausgeschaltet"
            return []
        if not self._modus_passt(self.e.modus_runter, u):
            self.z.letzte_meldung = "Schließen: Anwesenheit passt nicht"
            return []
        pos = lage.position
        fenster = self._fenster(lage)
        zweistufig_offen = lage.zweistufig and (lage.fenster == OFFEN)
        if fenster == ZU:
            if pos is None or pos > self.e.geschlossen_pos + TOLERANZ:
                self.z.pos_vor_geoeffnet = -1
                return self._fahrt(u, lage, self.e.geschlossen_pos, "Abends schließen")
            self.z.letzte_meldung = "Schließen: schon zu"
            return []
        # Fenster/Tür nicht zu → nach dem Schließen nachholen
        self.z.nachtschliessen = True
        if fenster == OFFEN:
            if pos is not None and pos > self.e.geoeffnet_pos + TOLERANZ and not self.e.aussperrschutz:
                return self._fahrt(u, lage, self.e.geoeffnet_pos, "Abends: Tür offen → Geöffnet-Position")
        elif fenster == GEKIPPT:
            if pos is not None and pos > self.e.lueften_pos + TOLERANZ and not (
                    self.e.aussperrschutz and zweistufig_offen):
                return self._fahrt(u, lage, self.e.lueften_pos, "Abends: Fenster offen → Lüften-Position")
        self.z.letzte_meldung = "Schließen: wartet, bis das Fenster zu ist"
        return []

    def party_ende(self, u: Umgebung, lage: Lage) -> list[Fahrt]:
        if self.z.party_level < 0:
            return []
        ziel, self.z.party_level = self.z.party_level, -1
        if self.e.partymodus:
            return self._fahrt(u, lage, ziel, "Partymodus beendet")
        return []

    # ------------------------------------------------------------------ Fenster
    def fenster_event(self, u: Umgebung, lage: Lage) -> list[Fahrt]:
        """Auto_Fenster_Komfort (Fensterkontakt-Teil)."""
        if not self.e.aktiv:
            return []
        fenster = self._fenster(lage)
        pos = lage.position
        steht = not lage.faehrt and pos is not None

        if fenster == ZU:
            if self.z.abschatten_nach_schliessen:
                vor = next((p for p in (self.z.pos_vor_geoeffnet, self.z.pos_vor_lueften) if p != -1),
                           pos if pos is not None else 100)
                self.z.pos_vor_abschattung = vor
                self.z.letzte_aktion = None if self.e.schnell_oeffnen else u.jetzt
                self.z.in_abschattung = True
                self.z.abschatten_vorgemerkt = False
                self.z.abschatten_nach_schliessen = False
                self.z.pos_vor_geoeffnet = -1
                self.z.pos_vor_lueften = -1
                self.z.zaehler_runter += 1
                self.z.abschattung_ziel = self.schattenpos(u)
                return self._fahrt(u, lage, self.z.abschattung_ziel, "Nachträglich abschatten")
            if self.z.nachtschliessen:
                self.z.nachtschliessen = False
                self.z.pos_vor_geoeffnet = -1
                self.z.pos_vor_lueften = -1
                if steht or pos is None:
                    return self._fahrt(u, lage, self.e.geschlossen_pos, "Fenster zu → Nachtschließen")
                return []
            ziel = []
            if self.z.pos_vor_geoeffnet != -1:
                if steht and gleich(pos, self.e.geoeffnet_pos) and not gleich(pos, self.z.pos_vor_geoeffnet):
                    ziel = self._fahrt(u, lage, self.z.pos_vor_geoeffnet, "Tür zu → zurück")
            elif self.z.pos_vor_lueften != -1:
                if steht and gleich(pos, self.e.lueften_pos) and not gleich(pos, self.z.pos_vor_lueften):
                    ziel = self._fahrt(u, lage, self.z.pos_vor_lueften, "Fenster zu → zurück")
            self.z.pos_vor_geoeffnet = -1
            self.z.pos_vor_lueften = -1
            return ziel

        if not u.auto_komfort or not self.e.luft_fenster_offen:
            return []

        if fenster == OFFEN:
            self.z.pos_vor_lueften = -1
            if steht and pos < self.e.geoeffnet_pos - TOLERANZ:
                if self.e.pos_nach_komfort_oeffnen == -1:
                    self.z.pos_vor_geoeffnet = pos
                elif self.e.pos_nach_komfort_oeffnen == -2:
                    self.z.pos_vor_geoeffnet = self.e.geoeffnet_pos
                else:
                    self.z.pos_vor_geoeffnet = self.e.pos_nach_komfort_oeffnen
                return self._fahrt(u, lage, self.e.geoeffnet_pos, "Tür offen → Geöffnet-Position")
            if pos is not None:
                self.z.pos_vor_geoeffnet = pos
            return []

        # gekippt (bzw. einfacher Kontakt offen)
        self.z.pos_vor_geoeffnet = -1
        if steht and pos < self.e.lueften_pos - TOLERANZ:
            self.z.pos_vor_lueften = pos
            return self._fahrt(u, lage, self.e.lueften_pos, "Fenster offen → Lüften-Position")
        self.z.pos_vor_lueften = -1
        return []

    # ------------------------------------------------------------------ Positionsmeldungen
    def positionsmeldung(self, u: Umgebung, pos: int | None) -> None:
        """Rollladen steht still an neuer Position: automatische oder manuelle Fahrt?"""
        if pos is None:
            return
        if self.z.erwartet is not None and self.z.erwartet_bis and u.jetzt <= self.z.erwartet_bis:
            if gleich(pos, self.z.erwartet, 5):
                self.z.erwartet = None
            return
        self.z.erwartet = None
        if gleich(pos, self._ziel()):
            return
        # manuelle Fahrt: Abschattung für die Sperrzeit aussetzen, Merker verwerfen
        self.z.sperrzeitpunkt = u.jetzt
        self._reset_abschattung()
        self.z.pos_vor_geoeffnet = -1
        self.z.pos_vor_lueften = -1
        self.z.nachtschliessen = False
        self.z.letzte_meldung = f"Manuell auf {pos} % gefahren"

    # ------------------------------------------------------------------ Abschattung
    def im_bereich(self, u: Umgebung) -> bool:
        if u.azimut is None:
            return False
        d = winkel_abweichung(u.azimut, self.e.himmelsrichtung)
        return (-self.e.winkel_links <= d <= self.e.winkel_rechts
                and (u.elevation is None or u.elevation >= self.e.min_elevation))

    def _abschattung_beenden(self, u: Umgebung, lage: Lage, grund: str) -> list[Fahrt]:
        vor = self.z.pos_vor_abschattung
        ziel_alt = self._ziel()
        ziel = self.e.pos_nach_abschattung if self.e.pos_nach_abschattung != -1 else vor
        self.z.letzte_aktion = None if self.e.schnell_schliessen else u.jetzt
        self._reset_abschattung()
        if ziel is None or ziel < 0:
            ziel = self.e.offen_pos
        fenster = self._fenster(lage)
        if fenster == OFFEN:
            self.z.pos_vor_geoeffnet = ziel
            return []
        if fenster == GEKIPPT and self.z.pos_vor_lueften != -1:
            self.z.pos_vor_lueften = ziel
            return []
        if gleich(lage.position, ziel_alt):
            self.z.zaehler_hoch += 1
            return self._fahrt(u, lage, ziel, grund)
        self.z.letzte_meldung = f"{grund}: zwischendurch bewegt – bleibt stehen"
        return []

    def abschattung(self, u: Umgebung, lage: Lage) -> list[Fahrt]:
        """Auto_Rol_group_Abschattung für diesen Rollladen."""
        if not u.auto_abschattung or not self.e.aktiv or u.azimut is None:
            return []
        modus = self.e.abschattung
        wartezeit = self.e.wartezeit / 2  # einmal bis zur Vormerkung, einmal bis zur Fahrt
        if modus == "verspaetet":
            wartezeit += 2
            modus = "ja"

        kalt = None
        if u.temperatur is not None and u.temperatur < self.e.min_temp_aussen:
            kalt = "zu kalt draußen"
        elif (self.e.min_temp_vorhersage is not None and u.vorhersage_max is not None
              and u.vorhersage_max < self.e.min_temp_vorhersage):
            kalt = f"heute nur {u.vorhersage_max:.0f} °C erwartet"
        elif lage.raumtemperatur is not None and lage.raumtemperatur < (
                self.e.min_temp_innen - (1 if self.z.in_abschattung else 0)):
            kalt = "Raum kühl – Sonne heizt mit"
        if kalt:
            if self.z.in_abschattung:
                return self._abschattung_beenden(u, lage, f"Abschattung Ende ({kalt})")
            if self.z.abschatten_vorgemerkt:
                self.z.letzte_meldung = f"Keine Abschattung: {kalt}"
            self.z.abschatten_vorgemerkt = self.z.ende_vorgemerkt = False
            return []
        if modus == "bei_abwesenheit" and u.anwesend is True:
            return []
        if modus == "bei_anwesenheit" and u.anwesend is False:
            return []
        if modus not in ("ja", "bei_abwesenheit", "bei_anwesenheit"):
            self.z.letzte_aktion = None
            return []

        h = lage.helligkeit
        if h is None:
            return []
        if self.z.ende_vorgemerkt and h >= self.e.schwelle_sonnig:
            self.z.ende_vorgemerkt = False
        if self.z.abschatten_vorgemerkt and h <= self.e.schwelle_wolkig:
            self.z.abschatten_vorgemerkt = False

        # kurz vor dem abendlichen Schließen nicht mehr öffnen
        if (self.e.sperrzeit_vor_nacht > 0 and self.z.in_abschattung and self.z.ende_vorgemerkt
                and self.z.runter_zeit is not None
                and (self.z.runter_zeit - u.jetzt).total_seconds() / 60 <= self.e.sperrzeit_vor_nacht):
            self._reset_abschattung()
            self.z.letzte_aktion = None
            self.z.letzte_meldung = "Abschattung bleibt bis zum Schließen"
            return []

        if self._minuten_seit(u, self.z.sperrzeitpunkt) <= self.e.sperrzeit_nach_manuell:
            return []
        if self._minuten_seit(u, self.z.letzte_aktion) < wartezeit:
            return []

        pos = lage.position if lage.position is not None else 100
        fenster = self._fenster(lage)
        ziel = self.schattenpos(u)

        if not self.im_bereich(u):
            if self.z.abschatten_nach_schliessen:
                self.z.abschatten_nach_schliessen = False
                return []
            if self.z.in_abschattung:
                return self._abschattung_beenden(u, lage, "Abschattung Ende (Sonne weg)")
            self.z.abschatten_vorgemerkt = self.z.ende_vorgemerkt = False
            return []

        if not self.z.in_abschattung and h >= self.e.schwelle_sonnig and not self.z.abschatten_vorgemerkt:
            if ziel < pos - TOLERANZ:
                self.z.abschatten_vorgemerkt = True
                self.z.ende_vorgemerkt = False
                self.z.letzte_aktion = u.jetzt
                self.z.letzte_meldung = "Abschatten vorgemerkt"
            elif self.z.pos_vor_geoeffnet != -1:
                self.z.abschatten_vorgemerkt = True
                self.z.ende_vorgemerkt = False
            return []

        if self.z.in_abschattung and h <= self.e.schwelle_wolkig and not self.z.ende_vorgemerkt:
            self.z.ende_vorgemerkt = True
            self.z.abschatten_vorgemerkt = False
            self.z.letzte_aktion = u.jetzt
            self.z.letzte_meldung = "Abschattungsende vorgemerkt"
            return []

        if self.z.abschatten_vorgemerkt and h >= self.e.schwelle_sonnig:
            if ziel < pos - TOLERANZ and self.z.pos_vor_geoeffnet == -1 and fenster != OFFEN:
                self.z.pos_vor_abschattung = pos
                self.z.abschattung_ziel = ziel
                self.z.letzte_aktion = None if self.e.schnell_oeffnen else u.jetzt
                self.z.in_abschattung = True
                self.z.abschatten_vorgemerkt = False
                self.z.zaehler_runter += 1
                return self._fahrt(u, lage, ziel, "Abschatten")
            if fenster == OFFEN and not self.z.abschatten_nach_schliessen:
                self.z.abschatten_nach_schliessen = True
                self.z.abschatten_vorgemerkt = False
                self.z.letzte_meldung = "Abschatten, sobald die Tür zu ist"
                return []
            self.z.letzte_aktion = u.jetzt
            return []

        if self.z.ende_vorgemerkt and h <= self.e.schwelle_wolkig:
            if self.z.abschatten_nach_schliessen:
                self.z.abschatten_nach_schliessen = False
                self.z.ende_vorgemerkt = False
                return []
            return self._abschattung_beenden(u, lage, "Abschattung Ende (Wolken)")

        # dynamische Abschattung: der Sonne nachführen, solange niemand von Hand gefahren ist
        if (self.e.abschattung_dynamisch and self.z.in_abschattung and not self.z.ende_vorgemerkt
                and gleich(lage.position, self._ziel(), 5) and abs(ziel - self._ziel()) >= 10):
            self.z.abschattung_ziel = ziel
            self.z.letzte_aktion = u.jetzt
            return self._fahrt(u, lage, ziel, "Abschattung nachgeführt")
        return []

    # ------------------------------------------------------------------ Anzeige
    def status(self, u: Umgebung | None = None) -> str:
        z = self.z
        if not self.e.aktiv:
            return "aus"
        if u and self._minuten_seit(u, z.sperrzeitpunkt) <= self.e.sperrzeit_nach_manuell:
            return "gesperrt"
        if z.abschatten_nach_schliessen:
            return "abschatten_nach_schliessen"
        if z.in_abschattung and z.ende_vorgemerkt:
            return "ende_vorgemerkt"
        if z.in_abschattung:
            return "abschattung"
        if z.abschatten_vorgemerkt:
            return "vorgemerkt"
        if z.nachtschliessen:
            return "nachtschliessen"
        if z.pos_vor_geoeffnet != -1:
            return "geoeffnet"
        if z.pos_vor_lueften != -1:
            return "lueften"
        if z.party_level >= 0:
            return "party"
        if z.oeffnen_nachholen:
            return "schlaf"
        return "bereit"
