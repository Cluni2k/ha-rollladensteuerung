# Rollladensteuerung für Home Assistant

🇬🇧 [English documentation](README.md)

Automatische Rollladensteuerung mit Abschattung und Komfortfunktionen für Home Assistant – der Nachbau der
bekannten FHEM-Rollladensteuerung von Bernd Hermanns und Matthias Frintrop
([Thread im FHEM-Forum](https://forum.fhem.de/index.php/topic,73964.0.html)) als eigene Integration.
Alles wird in der Oberfläche eingestellt, ein passendes Dashboard ist dabei.

## Funktionen

**Öffnen und Schließen**
- Morgens öffnen / abends schließen nach **Sonnenstand** (Sonnenauf-/-untergang, bürgerliche, nautische
  oder astronomische Dämmerung, eigener Horizont) mit **Früh-/Spät-Grenzen** oder zu einer **festen Zeit**.
- Eigene Zeit für **Wochenende und Feiertage** (über einen Arbeitstag-Sensor).
- **Versatz** und **Zufallsminuten** je Rollladen, damit das Haus nicht automatisch wirkt.
- Modus je Rollladen: *immer*, *nur wenn jemand zu Hause ist*, *nur wenn niemand zu Hause ist*, *aus*.
- **Frostschutz** (bei Frost morgens nicht öffnen), **Gästezimmer** (zu lassen, solange ein Gast da ist),
  **Partymodus** (erst nach der Party schließen), optionaler **Schlafschalter** (erst öffnen, wenn er aus ist –
  das Öffnen wird dann nachgeholt).

**Fenster und Türen**
- Fenster **gekippt** → Lüften-Position, Tür **offen** (Drehgriff) → Geöffnet-Position, danach zurück.
  Mehrere Kontakte je Rollladen sind möglich.
- Ist das Fenster beim abendlichen Schließen offen, schließt der Rollladen, **sobald es zu ist**.
- **Aussperrschutz:** bei offener Tür nie automatisch herunterfahren.

**Abschattung**
- Abschattung, wenn die Sonne in **Fensterrichtung ± Winkel** und über einer Mindesthöhe steht – mit
  **zwei Helligkeitsschwellen** (sonnig/wolkig) und **Vormerkung + Wartezeit**, damit Wolken den Rollladen
  nicht ständig hoch und runter fahren lassen.
- Nur ab einer **Mindest-Außentemperatur**; optional nur, wenn heute laut **Wettervorhersage** X °C erwartet
  werden; optional nur ab einer **Raumtemperatur** von X °C (im Winter heizt die Sonne mit).
- **Dynamische Abschattungsposition** (optional) aus Sonnenhöhe, Fensterhöhe, Brüstungshöhe und erlaubter
  Eindringtiefe – folgt der Sonne, nie dunkler als die feste Abschattungsposition.
- **Sperrzeit nach manueller Fahrt** und **vor dem abendlichen Schließen**; zurück auf die vorherige Position
  nur, wenn zwischendurch niemand gefahren ist.
- Steht Abschattung an, während die Tür offen ist, wird **nach dem Schließen der Tür** abgeschattet.

**Extras (Haupteinstellungen, alle optional)**
- **Brandschutz:** Bei Rauchalarm öffnen alle Rollläden (Fluchtweg), und bis zum Ende des Alarms fährt nichts automatisch herunter.
- **Hitzeschutz bei Abwesenheit:** Ab X °C (gemessen oder vorhergesagt) und wenn niemand zu Hause ist, wird dunkler abgeschattet.
- **Schließen bei Dunkelheit:** Abends schließen die Rollläden, sobald es dunkler als X Lux ist – nicht vor *Schließen frühestens*.
- **Urlaubsmodus** (Schalter in der Zentrale): jeden Tag Wochenend-/Feiertagszeiten und zusätzliche Zufallsminuten.
- **Tageszusammenfassung** (Schalter bei den Benachrichtigungen): abends ein Push mit dem, was heute passiert ist.

**Benachrichtigungen und Protokoll**
- **Push-Dienst** wählbar (HA-App, Pushover, … – jeder `notify`-Dienst; ein Skript mit `title`/`message` lässt sich eintippen).
- Schalter, was als Push kommen soll: **Öffnen gestartet** und **Schließen gestartet** (eine Nachricht für alle Rollläden),
  **Warnhinweise** (wegen Frost nicht geöffnet, Fenster beim Schließen offen, Aussperrschutz, Sensor oder Rollladen
  15 Minuten nicht erreichbar, Zielposition nicht erreicht), **Lüften**, **Abschatten** (Anfang und Ende),
  **Funktionen** (Automatik ein/aus) und **manuelle Fahrten**.
- **Protokoll der letzten 14 Tage** mit allen Aktionen – automatische und manuelle Fahrten, ausgelassene Fahrten mit Grund,
  geschaltete Funktionen, Warnungen – im Dashboard ansehen, filtern und als CSV speichern.

**Allgemein**
- **Gestaffelte Fahrten** mit einstellbarem Abstand (schont z. B. den Homematic-Duty-Cycle) – auch bei
  **Alle öffnen / lüften / abschatten / schließen**, jeder Rollladen auf seine eigene Position.
- Rollläden und Helligkeitssensoren werden in der Oberfläche **hinzugefügt, geändert und gelöscht**;
  ausgeblendete Entitäten werden nicht angeboten.
- Sensoren für **nächstes Öffnen/Schließen**, ein **Status-Sensor** mit allen Merkern und das Ereignis
  `rollladensteuerung_fahrt` für eigene Benachrichtigungen.
- **Dashboard inklusive:** Rollladen-Karten mit Zahnrad (Status und alle Einstellungen als Karteikarten),
  eine Zentrale-Karte für die globalen Schalter und Einstellungen und eine Dashboard-Vorlage, die die
  Ansicht selbst aufbaut (nach Stockwerk gruppiert, neue Rollläden erscheinen automatisch), dazu automatische
  Abschnitte für eigene, frei angeordnete Dashboards.

## Voraussetzungen

- Home Assistant **2025.6** oder neuer.
- Rollläden als `cover` mit Position (0 % = zu, 100 % = offen). Ohne Position wird nur auf/zu gefahren.
- Optional: Helligkeitssensor(en) in Lux, Außentemperatur, Anwesenheit (`binary_sensor`, `person`, `group` …),
  Arbeitstag-Sensor, Wetter-Entität, Raumtemperaturen, Fensterkontakte oder Drehgriffe.

## Installation

### HACS (benutzerdefiniertes Repository)
1. HACS → ⋮ → *Benutzerdefinierte Repositories* → `https://github.com/Cluni2k/ha-rollladensteuerung`
   hinzufügen, Kategorie **Integration**.
2. **Rollladensteuerung** installieren und Home Assistant neu starten.

### Von Hand
Ordner `custom_components/rollladensteuerung` nach `/config/custom_components/` kopieren und
Home Assistant neu starten.

## Einrichtung

1. *Einstellungen → Geräte & Dienste → Integration hinzufügen → Rollladensteuerung*:
   Anwesenheit, Außentemperatur, Arbeitstag-Sensor und (optional) Wetter wählen.
2. In der Integration **Helligkeitssensor hinzufügen** (einer oder mehrere).
3. **Rollladen hinzufügen** – ein Dialog mit den Abschnitten *Grundlagen, Zeiten, Positionen, Fenster,
   Abschattung*. Neue Rollläden bekommen sinnvolle Standardwerte (die Vorgaben der FHEM-Steuerung).

Alles lässt sich später ändern – in der Integration (⋮ → *Neu konfigurieren*) oder direkt im Dashboard.

## Dashboard

Die Integration bringt ihre Karten und eine Dashboard-Vorlage selbst mit – nichts weiter zu installieren.

**Ganzes Dashboard:** neues Dashboard anlegen → ⋮ → *Rohkonfigurationseditor*:
```yaml
strategy:
  type: custom:rollladensteuerung
```

**Als Ansicht in einem bestehenden Dashboard:**
```yaml
views:
  - strategy:
      type: custom:rollladensteuerung
      title: Rollläden
```

Standardmäßig kommen die Stockwerke zuerst und die Zentrale dahinter; `steuerung: vorne` stellt sie an den Anfang.

**Einzelne Karten:**
```yaml
type: custom:rollladensteuerung-card
entity: cover.wohnzimmer
```
```yaml
type: custom:rollladensteuerung-zentrale-card
```

Das Zahnrad auf einer Rollladen-Karte öffnet einen Dialog mit den Karteikarten *Status, Grundlagen, Zeiten,
Positionen, Fenster, Abschattung*. Das Zahnrad der Zentrale öffnet die Haupteinstellungen. Ändern dürfen
nur Administratoren.

**Selbst anordnen (empfohlen, ab HA 2026.11): automatische Abschnitte.** In einer normalen Abschnitts-Ansicht
*Abschnitt hinzufügen → Automatischer Abschnitt → Community* wählen. Es gibt drei Abschnitte:

| Abschnitt | Inhalt | Einstellungen |
|---|---|---|
| *Rollläden (Rollladensteuerung)* | alle Rollläden eines Stockwerks, nach Namen sortiert | Stockwerk (oder *Alle Rollläden* / *ohne Stockwerk*), Überschrift |
| *Rollladensteuerung – Automatik* | Zentrale mit Schaltern, Alle-Buttons und Zahnrad | Überschrift, Helligkeitsverlauf an/aus |
| *Rollladensteuerung – Benachrichtigungen* | Push-Schalter und Protokoll | Überschrift |

Die Abschnitte lassen sich frei verschieben und mit eigenen Karten mischen; die Anordnung liegt im eigenen Dashboard
und übersteht Updates. Neue Rollläden erscheinen trotzdem automatisch im Abschnitt ihres Stockwerks (Stockwerk über den
Bereich des Rollladens bzw. seines Geräts). Nur für ein ganz neues Stockwerk fügt man einmal einen Abschnitt hinzu.
In YAML:
```yaml
type: sections
sections:
  - strategy:
      type: custom:rollladensteuerung
      stockwerk: erdgeschoss
  - strategy:
      type: custom:rollladensteuerung-steuerung
  - strategy:
      type: custom:rollladensteuerung-meldungen
```

Die Ansicht aus der Dashboard-Vorlage oben wird dagegen erzeugt und ist schreibgeschützt.

## Einstellungen je Rollladen

| Abschnitt | Einstellung | Bedeutung |
|---|---|---|
| Grundlagen | Automatisch öffnen / schließen | immer, nur bei Anwesenheit, nur bei Abwesenheit, aus |
| | Frostschutz | morgens bei Frost nicht öffnen |
| | Gästezimmer / Partymodus | zu lassen, solange ein Gast da ist / erst nach der Party schließen |
| | Schlafschalter | erst öffnen, wenn der Schalter aus ist (wird nachgeholt) |
| Zeiten | Öffnen / Schließen nach | Sonnenstand (mit Grenzen) oder feste Zeit |
| | frühestens / spätestens | Grenzen an Arbeitstagen; eigene Zeit für Wochenende/Feiertag |
| | Versatz, Zufall | Verschiebung in Minuten, Zufall ± Minuten |
| Positionen | Offen, Geschlossen, Lüften, Geöffnet | Zielpositionen in % |
| | Nach Schließen der Tür | -1 = vorherige Position, -2 = Geöffnet-Position oder ein Wert |
| Fenster | Kontakte | Binärsensoren (offen = gekippt) oder Drehgriffe (zu/gekippt/offen) |
| | Aussperrschutz | bei offener Tür nie herunterfahren |
| Abschattung | Modus, Helligkeitssensor | aus, ein, verzögert, nur bei (Ab-)Anwesenheit |
| | Himmelsrichtung, Winkel links/rechts | Richtung des Fensters (90 = Ost, 180 = Süd, 270 = West) und Bereich |
| | Schwellen sonnig/wolkig | abschatten ab / beenden unter (Lux) |
| | Mindest-Außen-/Vorhersage-/Raumtemperatur | Bedingungen für die Abschattung |
| | Abschattungsposition, dynamisch | feste Position oder berechnet aus Sonnenhöhe und Fenstermaßen |
| | Wartezeit, Sperrzeiten | zwischen Fahrten, nach manueller Fahrt, vor dem Schließen am Abend |

Haupteinstellungen: Anwesenheit, Außentemperatur, Arbeitstag-Sensor, Sonne, Astro-Modus morgens/abends,
Frostschutz-Temperatur, Mindesthelligkeit für die Abschattungsprüfung, Wetter, Abstand zwischen Fahrten.

## Dienste

| Dienst | Beschreibung |
|---|---|
| `rollladensteuerung.alle_oeffnen` | jeder Rollladen auf seine Offen-Position (gestaffelt) |
| `rollladensteuerung.alle_lueften` | jeder Rollladen auf seine Lüften-Position (gestaffelt) |
| `rollladensteuerung.alle_abschatten` | jeder Rollladen mit eingeschalteter Abschattung auf seine Abschattungsposition (gestaffelt, nur nach unten) |
| `rollladensteuerung.alle_schliessen` | jeder Rollladen auf seine Geschlossen-Position (gestaffelt) |
| `rollladensteuerung.zusammenfassung_senden` | heutige Zusammenfassung sofort als Push senden |
| `rollladensteuerung.neu_berechnen` | nächste Öffnen-/Schließzeiten neu berechnen |
| `rollladensteuerung.abschattung_pruefen` | Abschattung sofort prüfen |

Bei jeder automatischen Fahrt wird das Ereignis `rollladensteuerung_fahrt` mit `rollladen`, `entity_id`,
`position` und `grund` ausgelöst.

## Entwicklung

Die Logik steckt ohne Home-Assistant-Abhängigkeit in `custom_components/rollladensteuerung/core.py` und
ist mit Tests abgedeckt: `python -m pytest tests`. Übersetzungen erzeugt `python tools/uebersetzungen.py`.

## Urheber und Lizenz

Ursprüngliche FHEM-Rollladensteuerung © 2018 Bernd Hermanns und Matthias Frintrop.
Nach Home Assistant portiert von Bernd Hermanns zusammen mit Claude (KI-Assistent von Anthropic).
Siehe [LICENSE](LICENSE).

Nutzung auf eigene Gefahr – automatisch fahrende Rollläden können aussperren oder Finger einklemmen;
für Türen den Aussperrschutz prüfen.
