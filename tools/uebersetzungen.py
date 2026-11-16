"""Erzeugt strings.json und translations/de.json + en.json: python tools/uebersetzungen.py"""
import json
import pathlib

ZIEL = pathlib.Path(__file__).parents[1] / "custom_components" / "rollladensteuerung"


def L(de, en):
    return (de, en)


GLOBAL = {
    "anwesenheit": L("Anwesenheit (an/zu Hause = jemand da)", "Presence (on/home = someone at home)"),
    "temperatur": L("Außentemperatur", "Outdoor temperature"),
    "werktag": L("Arbeitstag-Sensor (z. B. Workday)", "Workday sensor"),
    "sonne": L("Sonne", "Sun"),
    "astro_morgens": L("Astro-Modus morgens", "Astro mode (morning)"),
    "horizont_morgens": L("Horizont morgens (nur bei „Eigener Horizont“)", "Horizon morning (custom horizon only)"),
    "astro_abends": L("Astro-Modus abends", "Astro mode (evening)"),
    "horizont_abends": L("Horizont abends (nur bei „Eigener Horizont“)", "Horizon evening (custom horizon only)"),
    "frost_temp": L("Frostschutz-Temperatur", "Frost protection temperature"),
    "helligkeit_min": L("Abschattung erst prüfen ab Helligkeit", "Check shading only above brightness"),
    "wetter": L("Wettervorhersage (optional, für „heute erwartet“)", "Weather forecast (optional)"),
    "abstand_sekunden": L("Abstand zwischen Rollladenfahrten (schont den Funk-Duty-Cycle)", "Delay between shutter moves"),
}
ABSCHNITTE = {
    "grundlagen": (L("Grundlagen", "Basics"), {
        "name": L("Name", "Name"), "cover": L("Rollladen", "Cover"), "aktiv": L("Automatik aktiv", "Automation active"),
        "modus_hoch": L("Automatisch öffnen", "Open automatically"),
        "modus_runter": L("Automatisch schließen", "Close automatically"),
        "frostschutz": L("Frostschutz: morgens nicht öffnen bei Frost", "Frost protection: don't open when freezing"),
        "gaestezimmer": L("Gästezimmer: nicht öffnen, wenn Gast da", "Guest room: don't open while guest present"),
        "partymodus": L("Partymodus: abends erst nach der Party schließen", "Party mode: close after the party"),
        "schlaf": L("Schlafschalter (optional): morgens erst öffnen, wenn aus", "Sleep switch (optional): open only once off")}),
    "zeiten": (L("Zeiten", "Times"), {
        "hoch": L("Öffnen nach", "Open by"),
        "zeit_hoch_frueh": L("Öffnen frühestens (Arbeitstag)", "Open earliest (workday)"),
        "zeit_hoch_spaet": L("Öffnen spätestens (Arbeitstag)", "Open latest (workday)"),
        "zeit_hoch_we": L("Öffnen am Wochenende/Feiertag", "Open on weekends/holidays"),
        "offset_morgens": L("Versatz morgens", "Offset morning"), "runter": L("Schließen nach", "Close by"),
        "zeit_runter_frueh": L("Schließen frühestens", "Close earliest"),
        "zeit_runter_spaet": L("Schließen spätestens", "Close latest"),
        "offset_abends": L("Versatz abends", "Offset evening"),
        "zufall_minuten": L("Zufall (± Minuten)", "Random (± minutes)")}),
    "positionen": (L("Positionen", "Positions"), {
        "offen_pos": L("Offen (morgens)", "Open (morning)"), "geschlossen_pos": L("Geschlossen (abends)", "Closed (evening)"),
        "lueften_pos": L("Lüften (Fenster gekippt)", "Ventilation (window tilted)"),
        "geoeffnet_pos": L("Geöffnet (Tür/Fenster offen)", "Opened (door/window open)"),
        "pos_nach_komfort_oeffnen": L("Nach Schließen der Tür (-1 = vorherige, -2 = Geöffnet-Position)",
                                      "After door closes (-1 = previous, -2 = opened position)")}),
    "fenster": (L("Fenster", "Window"), {
        "fenster": L("Fensterkontakte bzw. Drehgriff", "Window contacts or handle sensor"),
        "luft_fenster_offen": L("Bei offenem Fenster auf Lüften/Geöffnet fahren", "Move to ventilation/opened when window opens"),
        "aussperrschutz": L("Aussperrschutz (bei offener Tür nie herunterfahren)", "Lock-out protection (never lower while door open)")}),
    "abschattung": (L("Abschattung", "Sun protection"), {
        "abschattung": L("Abschattung", "Sun protection"), "helligkeitssensor": L("Helligkeitssensor", "Brightness sensor"),
        "himmelsrichtung": L("Himmelsrichtung des Fensters (90 = Ost, 180 = Süd, 270 = West)", "Window direction (90 = east, 180 = south, 270 = west)"),
        "winkel_links": L("Winkel links (Sonne vor dem Fenster)", "Angle left (sun before window)"),
        "winkel_rechts": L("Winkel rechts (Sonne nach dem Fenster)", "Angle right (sun after window)"),
        "min_elevation": L("Mindest-Sonnenhöhe", "Minimum sun elevation"),
        "schwelle_sonnig": L("Schwelle sonnig (abschatten ab)", "Sunny threshold (shade above)"),
        "schwelle_wolkig": L("Schwelle wolkig (Ende unter)", "Cloudy threshold (end below)"),
        "min_temp_aussen": L("Mindest-Außentemperatur", "Minimum outdoor temperature"),
        "min_temp_vorhersage": L("Nur abschatten, wenn heute mindestens erwartet (optional)", "Shade only if today's forecast reaches (optional)"),
        "raumtemperatur": L("Raumtemperatur (optional, Winter: Sonne heizt mit)", "Room temperature (optional, winter sun heating)"),
        "min_temp_innen": L("Nur abschatten ab Raumtemperatur", "Shade only above room temperature"),
        "abschattung_dynamisch": L("Position nach Sonnenhöhe anpassen (dynamisch)", "Adjust position to sun elevation (dynamic)"),
        "fensterhoehe": L("Fensterhöhe (Öffnung)", "Window height"),
        "bruestung": L("Abstand Fenster–Boden (Brüstung)", "Sill height above floor"),
        "eindringtiefe": L("Sonne darf so weit in den Raum scheinen", "Allowed sun penetration into room"),
        "abschattung_pos": L("Abschattungsposition", "Shading position"),
        "pos_nach_abschattung": L("Position nach der Abschattung (-1 = vorherige)", "Position after shading (-1 = previous)"),
        "wartezeit": L("Wartezeit zwischen Fahrten", "Wait time between moves"),
        "sperrzeit_nach_manuell": L("Sperrzeit nach manueller Fahrt", "Lock time after manual move"),
        "sperrzeit_vor_nacht": L("Sperrzeit vor dem Schließen am Abend", "Lock time before evening close"),
        "schnell_oeffnen": L("Nach Abschatten schnell wieder öffnen", "Open quickly after shading"),
        "schnell_schliessen": L("Nach Öffnen schnell wieder abschatten", "Shade quickly after opening")}),
}
AUSWAHL = {
    "astro": {"real": L("Sonnenauf-/-untergang", "Sunrise/sunset"), "civil": L("Bürgerliche Dämmerung", "Civil twilight"),
              "nautic": L("Nautische Dämmerung", "Nautical twilight"), "astronomic": L("Astronomische Dämmerung", "Astronomical twilight"),
              "horizon": L("Eigener Horizont", "Custom horizon")},
    "modus": {"immer": L("Immer", "Always"), "bei_abwesenheit": L("Nur wenn niemand zu Hause ist", "Only when nobody is home"),
              "bei_anwesenheit": L("Nur wenn jemand zu Hause ist", "Only when someone is home"), "aus": L("Aus", "Off")},
    "zeitart": {"astro": L("Sonnenstand (mit Grenzen)", "Sun (with limits)"), "zeit": L("Feste Zeit", "Fixed time")},
    "abschattung": {"nein": L("Aus", "Off"), "ja": L("Ein", "On"), "verspaetet": L("Ein, etwas verzögert", "On, slightly delayed"),
                    "bei_abwesenheit": L("Nur wenn niemand zu Hause ist", "Only when nobody is home"),
                    "bei_anwesenheit": L("Nur wenn jemand zu Hause ist", "Only when someone is home")},
}
STATUS = {"aus": L("Aus", "Off"), "bereit": L("Bereit", "Ready"), "gesperrt": L("Gesperrt (manuell gefahren)", "Locked (moved manually)"),
          "vorgemerkt": L("Abschattung vorgemerkt", "Shading scheduled"), "abschattung": L("Abgeschattet", "Shaded"),
          "ende_vorgemerkt": L("Abschattungsende vorgemerkt", "Shading end scheduled"),
          "abschatten_nach_schliessen": L("Abschatten nach Schließen der Tür", "Shade after door closes"),
          "nachtschliessen": L("Schließt, sobald Fenster zu", "Closes once window is closed"),
          "geoeffnet": L("Geöffnet wegen offener Tür", "Opened for open door"), "lueften": L("Lüften", "Ventilating"),
          "party": L("Wartet auf Party-Ende", "Waiting for party end"),
          "schlaf": L("Wartet aufs Aufstehen", "Waiting for wake-up")}
ENTITAETEN = {
    "sensor": {"naechstes_oeffnen": L("Nächstes Öffnen", "Next opening"), "naechstes_schliessen": L("Nächstes Schließen", "Next closing"),
               "status": L("Status", "Status")},
    "switch": {"auto_morgens": L("Automatik morgens", "Automatic morning"), "auto_abends": L("Automatik abends", "Automatic evening"),
               "auto_abschattung": L("Abschattung", "Sun protection"), "auto_komfort": L("Komfort (Fenster)", "Comfort (windows)"),
               "auto_partymodus": L("Partymodus", "Party mode"), "auto_gast": L("Gast anwesend", "Guest present"),
               "automatik": L("Automatik", "Automation")}}
DIENSTE = {
    "neu_berechnen": (L("Zeiten neu berechnen", "Recalculate times"), L("Berechnet die nächsten Öffnen- und Schließzeiten aller Rollläden neu.", "Recalculates next open/close times.")),
    "abschattung_pruefen": (L("Abschattung jetzt prüfen", "Check sun protection now"), L("Prüft die Abschattung sofort für alle Rollläden.", "Runs the sun protection check now.")),
    "alle_oeffnen": (L("Alle öffnen", "Open all"), L("Fährt jeden Rollladen auf seine eingestellte Offen-Position.", "Moves every shutter to its configured open position.")),
    "alle_lueften": (L("Alle lüften", "Ventilate all"), L("Fährt jeden Rollladen auf seine eingestellte Lüften-Position.", "Moves every shutter to its ventilation position.")),
    "alle_schliessen": (L("Alle schließen", "Close all"), L("Fährt jeden Rollladen auf seine eingestellte Geschlossen-Position.", "Moves every shutter to its configured closed position.")),
}


def bauen(i):
    def t(p):
        return p[i]
    g = {k: t(v) for k, v in GLOBAL.items()}
    abschnitte = {k: {"name": t(titel), "data": {f: t(v) for f, v in felder.items()}}
                  for k, (titel, felder) in ABSCHNITTE.items()}
    rl_schritt = {"title": t(L("Rollladen", "Shutter")), "data": {k: t(titel) for k, (titel, _) in ABSCHNITTE.items()},
                  "sections": abschnitte}
    hell_schritt = {"title": t(L("Helligkeitssensor", "Brightness sensor")),
                    "data": {"name": t(L("Name", "Name")), "entity": t(L("Sensor", "Sensor"))}}
    gespeichert = {"reconfigure_successful": t(L("Gespeichert.", "Saved."))}
    return {
        "config": {"step": {"user": {"title": t(L("Rollladensteuerung", "Shutter control")),
                                     "description": t(L("Globale Einstellungen. Rollläden und Helligkeitssensoren fügst du danach als Einträge hinzu.",
                                                        "Global settings. Add shutters and brightness sensors afterwards.")),
                                     "data": g}},
                   "abort": {"already_configured": t(L("Die Rollladensteuerung ist bereits eingerichtet.", "Already configured."))}},
        "options": {"step": {"init": {"title": t(L("Globale Einstellungen", "Global settings")), "data": g}}},
        "config_subentries": {
            "rollladen": {"entry_type": t(L("Rollladen", "Shutter")),
                          "initiate_flow": {"user": t(L("Rollladen hinzufügen", "Add shutter")),
                                            "reconfigure": t(L("Rollladen bearbeiten", "Edit shutter"))},
                          "step": {"user": rl_schritt, "reconfigure": rl_schritt}, "abort": gespeichert},
            "helligkeit": {"entry_type": t(L("Helligkeitssensor", "Brightness sensor")),
                           "initiate_flow": {"user": t(L("Helligkeitssensor hinzufügen", "Add brightness sensor")),
                                             "reconfigure": t(L("Helligkeitssensor bearbeiten", "Edit brightness sensor"))},
                           "step": {"user": hell_schritt, "reconfigure": hell_schritt}, "abort": gespeichert}},
        "selector": {k: {"options": {o: t(v) for o, v in opts.items()}} for k, opts in AUSWAHL.items()},
        "entity": {"sensor": {**{k: {"name": t(v)} for k, v in ENTITAETEN["sensor"].items()}},
                   "switch": {k: {"name": t(v)} for k, v in ENTITAETEN["switch"].items()}},
        "services": {k: {"name": t(n), "description": t(b)} for k, (n, b) in DIENSTE.items()},
    } | {"entity": {"sensor": {**{k: {"name": t(v)} for k, v in ENTITAETEN["sensor"].items()},
                               "status": {"name": t(ENTITAETEN["sensor"]["status"]),
                                          "state": {k: t(v) for k, v in STATUS.items()}}},
                    "switch": {k: {"name": t(v)} for k, v in ENTITAETEN["switch"].items()}}}


(ZIEL / "translations").mkdir(exist_ok=True)
for datei, i in (("translations/de.json", 0), ("translations/en.json", 1), ("strings.json", 1)):
    (ZIEL / datei).write_text(json.dumps(bauen(i), ensure_ascii=False, indent=2) + "\n", "utf-8")
print("ok")
