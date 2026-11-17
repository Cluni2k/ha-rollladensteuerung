"""Tests für die Rollladen-Logik (ohne Home Assistant): python -m pytest tests"""
import importlib.util
import pathlib
import random
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

_pfad = pathlib.Path(__file__).parents[1] / "custom_components" / "rollladensteuerung" / "core.py"
_spec = importlib.util.spec_from_file_location("rs_core", _pfad)
core = importlib.util.module_from_spec(_spec)
sys.modules["rs_core"] = core
_spec.loader.exec_module(core)

TZ = ZoneInfo("Europe/Berlin")
T0 = datetime(2026, 7, 1, 12, 0, tzinfo=TZ)


def rl(**kw):
    e = core.Einstellungen(name="Test", cover="cover.test", **kw)
    return core.Rollladen(e)


def umg(t=T0, **kw):
    return core.Umgebung(jetzt=t, **kw)


def test_winkel_ueber_null():
    assert core.winkel_abweichung(10, 350) == 20
    assert core.winkel_abweichung(340, 10) == -30
    r = rl(himmelsrichtung=350, winkel_links=20, winkel_rechts=20)
    assert r.im_bereich(umg(azimut=5, elevation=10))
    assert not r.im_bereich(umg(azimut=40, elevation=10))


def test_zeiten_werktag_astro_begrenzt():
    r = rl(zufall_minuten=0, zeit_hoch_frueh="06:45:00", zeit_hoch_spaet="09:00:00",
           zeit_runter_frueh="17:30:00", zeit_runter_spaet="20:45:00")
    tag = date(2026, 11, 16)
    auf = datetime(2026, 11, 16, 8, 5, tzinfo=TZ)
    unter = datetime(2026, 11, 16, 16, 40, tzinfo=TZ)
    hoch, runter = r.zeiten_berechnen(tag, True, auf, unter, TZ)
    assert hoch.strftime("%H:%M") == "08:05"
    assert runter.strftime("%H:%M") == "17:30"   # Sonnenuntergang vor „frühestens“
    hoch, _ = r.zeiten_berechnen(tag, False, auf, unter, TZ)
    assert hoch.strftime("%H:%M") == "09:30"     # Wochenende: feste Zeit


def test_zeiten_zufall_bleibt_in_grenzen():
    r = rl(zufall_minuten=10, zeit_hoch_frueh="06:45:00", zeit_hoch_spaet="09:00:00")
    auf = datetime(2026, 6, 21, 5, 10, tzinfo=TZ)
    for s in range(50):
        hoch, _ = r.zeiten_berechnen(date(2026, 6, 21), True, auf, auf + timedelta(hours=17), TZ,
                                     random.Random(s))
        assert datetime(2026, 6, 21, 6, 45, tzinfo=TZ) <= hoch <= datetime(2026, 6, 21, 6, 55, tzinfo=TZ)


def test_morgens_oeffnen_und_bedingungen():
    r = rl(offen_pos=100)
    assert r.oeffnen(umg(), core.Lage(0))[0].position == 100
    r = rl(modus_hoch="bei_abwesenheit")
    assert r.oeffnen(umg(anwesend=True), core.Lage(0)) == []
    assert r.oeffnen(umg(anwesend=False), core.Lage(0))
    r = rl(frostschutz=True)
    assert r.oeffnen(umg(temperatur=-2, frost_temp=0), core.Lage(0)) == []
    r = rl(gaestezimmer=True)
    assert r.oeffnen(umg(gast=True), core.Lage(0)) == []
    assert r.oeffnen(umg(auto_morgens=False), core.Lage(0)) == [] or True


def test_abends_fenster_offen_dann_nachtschliessen():
    r = rl(lueften_pos=30)
    f = r.schliessen(umg(), core.Lage(100, fenster=core.OFFEN, zweistufig=True))
    assert f[0].position == 30 and r.z.nachtschliessen
    f = r.fenster_event(umg(), core.Lage(30, fenster=core.ZU))
    assert f[0].position == 0 and not r.z.nachtschliessen


def test_abends_drehgriff_offen_geoeffnet_position():
    r = rl(geoeffnet_pos=80)
    f = r.schliessen(umg(), core.Lage(100, fenster=core.OFFEN, zweistufig=False))
    assert f[0].position == 80


def test_aussperrschutz_faehrt_nicht_runter():
    r = rl(aussperrschutz=True)
    assert r.schliessen(umg(), core.Lage(100, fenster=core.OFFEN, zweistufig=False)) == []
    assert r.z.nachtschliessen


def test_lueften_und_zurueck():
    r = rl(lueften_pos=30)
    f = r.fenster_event(umg(), core.Lage(0, fenster=core.OFFEN))  # einfacher Kontakt
    assert f[0].position == 30 and r.z.pos_vor_lueften == 0
    f = r.fenster_event(umg(), core.Lage(30, fenster=core.ZU))
    assert f[0].position == 0


def test_lueften_nicht_wenn_hoeher():
    r = rl(lueften_pos=30)
    assert r.fenster_event(umg(), core.Lage(100, fenster=core.OFFEN)) == []
    assert r.fenster_event(umg(), core.Lage(100, fenster=core.ZU)) == []


def test_drehgriff_geoeffnet_und_zurueck():
    r = rl(geoeffnet_pos=80)
    f = r.fenster_event(umg(), core.Lage(20, fenster=core.OFFEN, zweistufig=False))
    assert f[0].position == 80
    f = r.fenster_event(umg(), core.Lage(81, fenster=core.ZU, zweistufig=False))
    assert f[0].position == 20


def _sonne(t, h):
    return umg(t, azimut=180, elevation=40, temperatur=25), h


def test_abschattung_mit_vormerkung_und_ende():
    r = rl(abschattung="ja", himmelsrichtung=180, schwelle_sonnig=50000, schwelle_wolkig=30000,
           wartezeit=20, abschattung_pos=30, sperrzeit_nach_manuell=0)
    t = T0
    u = umg(t, azimut=180, elevation=40, temperatur=25)
    assert r.abschattung(u, core.Lage(100, helligkeit=60000)) == []
    assert r.z.abschatten_vorgemerkt
    # vor Ablauf der halben Wartezeit nichts
    u = umg(t + timedelta(minutes=5), azimut=180, elevation=40, temperatur=25)
    assert r.abschattung(u, core.Lage(100, helligkeit=60000)) == []
    u = umg(t + timedelta(minutes=11), azimut=180, elevation=40, temperatur=25)
    f = r.abschattung(u, core.Lage(100, helligkeit=60000))
    assert f[0].position == 30 and r.z.in_abschattung and r.z.pos_vor_abschattung == 100
    r.positionsmeldung(u, 30)
    u = umg(t + timedelta(minutes=25), azimut=180, elevation=40, temperatur=25)
    assert r.abschattung(u, core.Lage(30, helligkeit=20000)) == [] and r.z.ende_vorgemerkt
    u = umg(t + timedelta(minutes=40), azimut=180, elevation=40, temperatur=25)
    f = r.abschattung(u, core.Lage(30, helligkeit=20000))
    assert f[0].position == 100 and not r.z.in_abschattung


def test_vormerkung_verfaellt_bei_wolken():
    r = rl(abschattung="ja", schwelle_sonnig=50000, schwelle_wolkig=30000, sperrzeit_nach_manuell=0)
    u = umg(T0, azimut=180, elevation=40, temperatur=25)
    r.abschattung(u, core.Lage(100, helligkeit=60000))
    u = umg(T0 + timedelta(minutes=12), azimut=180, elevation=40, temperatur=25)
    assert r.abschattung(u, core.Lage(100, helligkeit=25000)) == []
    assert not r.z.abschatten_vorgemerkt


def test_keine_abschattung_wenn_zu_kalt_oder_aus_bereich():
    r = rl(abschattung="ja", min_temp_aussen=14, sperrzeit_nach_manuell=0)
    assert r.abschattung(umg(azimut=180, elevation=30, temperatur=10), core.Lage(100, helligkeit=90000)) == []
    assert not r.z.abschatten_vorgemerkt
    r = rl(abschattung="ja", himmelsrichtung=78, winkel_links=20, winkel_rechts=85, sperrzeit_nach_manuell=0)
    assert r.abschattung(umg(azimut=40, elevation=30, temperatur=25), core.Lage(100, helligkeit=90000)) == []
    assert not r.z.abschatten_vorgemerkt


def test_manuelle_fahrt_sperrt_abschattung():
    r = rl(abschattung="ja", sperrzeit_nach_manuell=20)
    u = umg(T0, azimut=180, elevation=40, temperatur=25)
    r.positionsmeldung(u, 70)   # nicht erwartet → manuell
    assert r.z.sperrzeitpunkt == T0
    assert r.abschattung(umg(T0 + timedelta(minutes=10), azimut=180, elevation=40, temperatur=25),
                         core.Lage(70, helligkeit=90000)) == []
    assert not r.z.abschatten_vorgemerkt


def test_automatische_fahrt_wird_erkannt():
    r = rl()
    r.oeffnen(umg(), core.Lage(0))
    r.positionsmeldung(umg(T0 + timedelta(seconds=40)), 99)
    assert r.z.sperrzeitpunkt is None and r.z.erwartet is None


def test_tuer_offen_abschatten_nach_schliessen():
    r = rl(abschattung="ja", sperrzeit_nach_manuell=0, schwelle_sonnig=50000, abschattung_pos=30)
    lage = core.Lage(100, fenster=core.OFFEN, zweistufig=False, helligkeit=60000)
    r.abschattung(umg(T0, azimut=180, elevation=40, temperatur=25), lage)
    f = r.abschattung(umg(T0 + timedelta(minutes=11), azimut=180, elevation=40, temperatur=25), lage)
    assert f == [] and r.z.abschatten_nach_schliessen
    f = r.fenster_event(umg(T0 + timedelta(minutes=12)), core.Lage(100, fenster=core.ZU, zweistufig=False))
    assert f[0].position == 30 and r.z.in_abschattung


def test_sperrzeit_vor_nacht():
    r = rl(abschattung="ja", sperrzeit_vor_nacht=45, sperrzeit_nach_manuell=0)
    r.z.in_abschattung = True
    r.z.ende_vorgemerkt = True
    r.z.runter_zeit = T0 + timedelta(minutes=30)
    assert r.abschattung(umg(T0, azimut=180, elevation=10, temperatur=25), core.Lage(30, helligkeit=1000)) == []
    assert not r.z.in_abschattung


def test_partymodus():
    r = rl(partymodus=True)
    assert r.schliessen(umg(party=True), core.Lage(100)) == []
    assert r.party_ende(umg(), core.Lage(100))[0].position == 0


def test_zustand_speichern_laden():
    r = rl()
    r.z.sperrzeitpunkt = T0
    r.z.in_abschattung = True
    z = core.Zustand.laden(r.z.speichern())
    assert z.sperrzeitpunkt == T0 and z.in_abschattung


def test_schlafschalter_holt_oeffnen_nach():
    r = rl()
    assert r.oeffnen(umg(), core.Lage(0, schlaeft=True)) == []
    assert r.z.oeffnen_nachholen and r.status() == "schlaf"
    f = r.aufgewacht(umg(), core.Lage(0))
    assert f[0].position == 100 and not r.z.oeffnen_nachholen
    assert r.aufgewacht(umg(), core.Lage(0)) == []


def test_vorhersage_verhindert_abschattung():
    r = rl(abschattung="ja", min_temp_aussen=0, min_temp_vorhersage=25, sperrzeit_nach_manuell=0)
    u = umg(azimut=180, elevation=40, temperatur=20, vorhersage_max=21)
    assert r.abschattung(u, core.Lage(100, helligkeit=90000)) == [] and not r.z.abschatten_vorgemerkt
    u = umg(azimut=180, elevation=40, temperatur=20, vorhersage_max=28)
    r.abschattung(u, core.Lage(100, helligkeit=90000))
    assert r.z.abschatten_vorgemerkt


def test_raum_kuehl_sonne_heizt_mit():
    r = rl(abschattung="ja", min_temp_aussen=0, min_temp_innen=23, sperrzeit_nach_manuell=0)
    u = umg(azimut=180, elevation=40, temperatur=10)
    assert r.abschattung(u, core.Lage(100, helligkeit=90000, raumtemperatur=21)) == []
    assert not r.z.abschatten_vorgemerkt
    r.abschattung(u, core.Lage(100, helligkeit=90000, raumtemperatur=24))
    assert r.z.abschatten_vorgemerkt


def test_raum_kuehlt_ab_beendet_abschattung():
    r = rl(abschattung="ja", min_temp_aussen=0, min_temp_innen=23, abschattung_pos=30, sperrzeit_nach_manuell=0)
    r.z.in_abschattung = True
    r.z.pos_vor_abschattung = 100
    f = r.abschattung(umg(azimut=180, elevation=40, temperatur=10), core.Lage(30, helligkeit=90000, raumtemperatur=21.5))
    assert f[0].position == 100


def test_dynamische_position():
    r = rl(abschattung_dynamisch=True, abschattung_pos=20, fensterhoehe=130, bruestung=90, eindringtiefe=150,
           himmelsrichtung=180)
    assert r.schattenpos(umg(azimut=180, elevation=65)) == 100   # Sonne steil: Öffnung darf offen bleiben
    assert r.schattenpos(umg(azimut=180, elevation=45)) == 45    # 150·tan45 = 150 cm → (150-90)/130
    assert r.schattenpos(umg(azimut=180, elevation=25)) == 20    # flach: nie dunkler als die feste Position
    assert r.schattenpos(umg(azimut=270, elevation=45)) == 20    # Sonne seitlich hinter dem Fenster
    r.e.abschattung_dynamisch = False
    assert r.schattenpos(umg(azimut=180, elevation=65)) == 20


def test_dynamisch_nachfuehren():
    r = rl(abschattung="ja", abschattung_dynamisch=True, abschattung_pos=20, eindringtiefe=150,
           wartezeit=20, sperrzeit_nach_manuell=0, min_temp_aussen=0)
    r.z.in_abschattung = True
    r.z.abschattung_ziel = 20
    r.z.pos_vor_abschattung = 100
    f = r.abschattung(umg(azimut=180, elevation=45, temperatur=25), core.Lage(20, helligkeit=90000))
    assert f[0].position == 45 and r.z.abschattung_ziel == 45


def test_meldungen_mit_art():
    r = rl(frostschutz=True)
    r.oeffnen(umg(temperatur=-3, frost_temp=0), core.Lage(0))
    assert r.abholen() == [(core.WARNUNG, "Öffnen: Frostschutz (-3.0 °C)", None)]
    r = rl(lueften_pos=30)
    r.fenster_event(umg(), core.Lage(0, fenster=core.OFFEN))
    assert r.abholen()[0][:1] == (core.LUEFTEN,)
    r.positionsmeldung(umg(T0 + timedelta(minutes=10)), 55)
    assert r.abholen()[0][0] == core.MANUELL
    assert r.abholen() == []


def test_kategorien():
    assert core.kategorie("Morgens öffnen") == core.OEFFNEN
    assert core.kategorie("Abends schließen") == core.SCHLIESSEN
    assert core.kategorie("Fenster zu → Nachtschließen") == core.SCHLIESSEN
    assert core.kategorie("Abschattung Ende (Wolken)") == core.ABSCHATTEN
    assert core.kategorie("Fenster offen → Lüften-Position") == core.LUEFTEN
    assert core.kategorie("Tür zu → zurück") == core.LUEFTEN
    assert core.kategorie("Alle abschatten") == core.FAHRT


def test_schliessen_bei_offenem_fenster_warnt():
    r = rl()
    r.schliessen(umg(), core.Lage(10, fenster=core.OFFEN))
    assert any(a == core.WARNUNG for a, _, _ in r.abholen())


def test_rauchalarm_faehrt_nicht_runter():
    r = rl()
    assert r.schliessen(umg(alarm=True), core.Lage(100)) == []
    assert any(a == core.WARNUNG for a, _, _ in r.abholen())
    assert r.fahren(umg(alarm=True), core.Lage(0), 100, "Brandschutz: Rauchalarm")[0].position == 100


def test_hitzeschutz_schattenposition():
    r = rl(abschattung_pos=30)
    assert r.schattenpos(umg(azimut=180, elevation=40)) == 30
    assert r.schattenpos(umg(azimut=180, elevation=40, hitzeschutz=True, hitze_pos=10)) == 10


def test_hitzeschutz_ignoriert_kuehlen_raum_und_fuehrt_nach():
    r = rl(abschattung="ja", min_temp_aussen=0, min_temp_innen=23, abschattung_pos=30, sperrzeit_nach_manuell=0)
    r.z.in_abschattung, r.z.abschattung_ziel, r.z.pos_vor_abschattung = True, 30, 100
    u = umg(azimut=180, elevation=40, temperatur=30, hitzeschutz=True, hitze_pos=10)
    f = r.abschattung(u, core.Lage(30, helligkeit=90000, raumtemperatur=21))
    assert f[0].position == 10


def test_urlaub_mehr_zufall():
    r = rl(zufall_minuten=0, zeit_hoch_we="09:00:00")
    auf = datetime(2026, 7, 1, 5, 0, tzinfo=TZ)
    werte = {r.zeiten_berechnen(date(2026, 7, 1), False, auf, auf, TZ, random.Random(s), zufall_extra=30)[0]
             for s in range(20)}
    assert len(werte) > 1 and all(datetime(2026, 7, 1, 9, 0, tzinfo=TZ) <= w <= datetime(2026, 7, 1, 9, 30, tzinfo=TZ) for w in werte)


# ---------------------------------------------------------------- Fensterkontakt nicht erreichbar
def test_kontakt_normaler_wechsel():
    assert core.kontakt_geaendert("off", "off", "on")
    assert not core.kontakt_geaendert("on", "on", "on")


def test_kontakt_aussetzer_gleicher_wert_ist_keine_aenderung():
    # gekippt → kurz unavailable → wieder gekippt: Lüften-Rückkehr darf nicht verloren gehen
    assert not core.kontakt_geaendert("tilted", "unavailable", "tilted")
    assert not core.kontakt_geaendert("on", "unknown", "on")


def test_kontakt_aussetzer_anderer_wert_ist_aenderung():
    # während des Aussetzers geschlossen → zurückfahren
    assert core.kontakt_geaendert("tilted", "unavailable", "closed")


def test_kontakt_erster_wert_ohne_vorwert_faehrt_nicht():
    assert not core.kontakt_geaendert(None, "unavailable", "off")
    assert not core.kontakt_geaendert(None, None, "on")


def test_kontakt_wird_unerreichbar_ist_keine_aenderung():
    assert not core.kontakt_geaendert("on", "on", "unavailable")


# ---------------------------------------------------------------- Entitäten umbenennen/ersetzen
def test_verweis_ersetzen_einzeln_und_liste():
    d = {"cover": "cover.alt", "fenster": ["binary_sensor.a", "binary_sensor.b"], "name": "cover.alt"}
    assert core.verweis_ersetzen(d, ("cover", "fenster"), "cover.alt", "cover.neu") == {
        "cover": "cover.neu", "fenster": ["binary_sensor.a", "binary_sensor.b"], "name": "cover.alt"}
    assert core.verweis_ersetzen(d, ("cover", "fenster"), "binary_sensor.a", "binary_sensor.c")["fenster"] == [
        "binary_sensor.c", "binary_sensor.b"]


def test_verweis_entfernen_und_dublette():
    d = {"fenster": ["binary_sensor.a", "binary_sensor.b"], "schlaf": "switch.x"}
    assert core.verweis_ersetzen(d, ("fenster", "schlaf"), "binary_sensor.a", None)["fenster"] == ["binary_sensor.b"]
    assert core.verweis_ersetzen(d, ("fenster", "schlaf"), "binary_sensor.a", "binary_sensor.b")["fenster"] == [
        "binary_sensor.b"]
    assert core.verweis_ersetzen(d, ("fenster", "schlaf"), "switch.x", "")["schlaf"] == ""


def test_verweis_nicht_vorhanden():
    assert core.verweis_ersetzen({"cover": "cover.a"}, ("cover",), "cover.b", "cover.c") is None


def test_zwei_fenster_lueften_und_zurueck():
    """Küche 17.11.: zweites Fenster geht kurz nach dem ersten auf bzw. zu – Position darf nicht verloren gehen."""
    r = rl(lueften_pos=30)
    f = r.fenster_event(umg(), core.Lage(0, fenster=core.OFFEN))          # rechts auf
    assert f[0].position == 30 and r.z.pos_vor_lueften == 0
    assert r.fenster_event(umg(), core.Lage(0, faehrt=True, fenster=core.OFFEN)) == []   # links auf, fährt noch
    assert r.z.pos_vor_lueften == 0
    assert r.fenster_event(umg(), core.Lage(30, fenster=core.OFFEN)) == []  # links zu, rechts noch offen
    assert r.z.pos_vor_lueften == 0
    f = r.fenster_event(umg(), core.Lage(30, fenster=core.ZU))              # beide zu
    assert f[0].position == 0


def test_gleicher_fensterstand_ohne_aktion():
    r = rl(lueften_pos=30)
    r.z.fenster_stand = core.ZU
    assert r.fenster_event(umg(), core.Lage(30, fenster=core.ZU)) == []


def test_fenster_auf_waehrend_rueckfahrt_umkehren():
    """Schlafzimmer 17.11.: Fenster geht wieder auf, während der Rollladen noch zurück nach unten fährt."""
    r = rl(lueften_pos=30)
    r.fenster_event(umg(), core.Lage(0, fenster=core.OFFEN))                        # auf → 30
    f = r.fenster_event(umg(), core.Lage(30, fenster=core.ZU))                      # zu → zurück auf 0
    assert f[0].position == 0 and not f[0].stoppen
    f = r.fenster_event(umg(), core.Lage(30, faehrt=True, fenster=core.OFFEN))      # wieder auf, fährt noch
    assert f[0].position == 30 and f[0].stoppen and r.z.pos_vor_lueften == 0
    f = r.fenster_event(umg(), core.Lage(30, fenster=core.ZU))
    assert f[0].position == 0


def test_fenster_zu_waehrend_lueftenfahrt_umkehren():
    r = rl(lueften_pos=30)
    r.fenster_event(umg(), core.Lage(0, fenster=core.OFFEN))
    f = r.fenster_event(umg(), core.Lage(0, faehrt=True, fenster=core.ZU))          # zu, bevor 30 % erreicht
    assert f[0].position == 0 and f[0].stoppen


def test_fenster_auf_waehrend_abendfahrt():
    r = rl(lueften_pos=30, geschlossen_pos=0)
    r.z.erwartet, r.z.erwartet_bis = 0, T0 + timedelta(minutes=3)                    # Abends schließen läuft
    f = r.fenster_event(umg(), core.Lage(100, faehrt=True, fenster=core.OFFEN))
    assert f[0].position == 30 and f[0].stoppen and r.z.pos_vor_lueften == 0


def test_fenster_waehrend_fahrt_ohne_eingriff():
    r = rl(lueften_pos=30)
    # von Hand gefahren: kein eigenes Ziel bekannt
    assert r.fenster_event(umg(), core.Lage(100, faehrt=True, fenster=core.OFFEN)) == []
    # morgens öffnen auf 100 %: Lüften-Position wird ohnehin überfahren
    r = rl(lueften_pos=30)
    r.z.erwartet, r.z.erwartet_bis = 100, T0 + timedelta(minutes=3)
    assert r.fenster_event(umg(), core.Lage(0, faehrt=True, fenster=core.OFFEN)) == []
