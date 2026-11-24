# Changelog

Alle Änderungen der Rollladensteuerung. / All changes of the shutter control.

## 0.8.1 (2026-11-22)

**Neu:** Taste „Lüften“ auf jeder Rollladen-Karte – fährt den Rollladen auf seine eingestellte Lüften-Position (eigenes Symbol, Tooltip mit Position, ausgegraut wenn er schon dort steht).

## 0.8.0 (2026-11-22)

**Neu: Protokoll-Karte** `custom:rollladensteuerung-protokoll-card` – Zeitraum (Heute, Gestern, 7/30 Tage, Alles, Von–Bis), Filter nach Rollläden und Ereignissen, Suche, Anzeige auf der Karte und Download als CSV (Datum/Uhrzeit getrennt, Semikolon). Auf jedem Dashboard nutzbar, mit visuellem Editor; zusätzlich als automatischer Abschnitt `custom:rollladensteuerung-protokoll` (volle Breite, in der erzeugten Ansicht als eigene Gruppe unten).

**Geändert**
- Protokoll wird 90 statt 14 Tage aufbewahrt.

**Behoben**
- Öffnen/Schließen löste im Zufallsfenster teils mehrfach am selben Tag aus (doppelte Frostwarnungen bzw. „steht schon höher“/„schon zu“).

Enthält außerdem v0.7.8: eine Frostschutz-Push-Meldung für alle Rollläden statt einer je Rollladen.

## 0.7.8 (2026-11-22)

Frostschutz: eine Push-Meldung für alle zurückgehaltenen Rollläden statt einer je Rollladen. Die Sammelmeldung „Die Rollläden werden geöffnet“ zählt wegen Frost geschlossene Rollläden nicht mehr mit.

## 0.7.7 (2026-11-17)

Richtungswechsel schneller: nach dem Anhalten 1 Sekunde Pause, der Stopp zählt nicht mehr zum Abstand zwischen Funkbefehlen. / Faster reversal: 1 s pause after stopping; the stop no longer counts toward the command spacing.

## 0.7.6 (2026-11-17)

Fenster während einer Fahrt: Geht das Fenster in der kurzen Pause nach dem Anhalten wieder auf (oder zu), gilt die neueste Entscheidung – die vorher geplante Fahrt verfällt. / The newest decision wins: a pending move is dropped when the window changes again during the pause.

## 0.7.5 (2026-11-17)

Fenster während einer Fahrt: Geht ein Fenster auf, während der Rollladen unter die Lüften-/Geöffnet-Position fährt (oder zu, während er noch zum Lüften hochfährt), hält er an, wartet 2 Sekunden und fährt in die richtige Richtung. / Window changes while moving: the shutter stops, waits 2 s and reverses.

## 0.7.4 (2026-11-17)

Fix: with several window contacts on one shutter, a second window opening or closing while the first was still open erased the remembered position – the shutter stayed in the ventilation position after all windows were closed. / Behoben: Bei mehreren Fensterkontakten an einem Rollladen löschte das zweite Fenster die gemerkte Position – der Rollladen blieb nach dem Schließen aller Fenster in der Lüften-Position.

## 0.7.3 (2026-11-17)

Shutter card: opening and closing time stay together on one line, 12-hour times without leading zero, time format follows the HA profile. / Rollladenkarte: Öffnungs- und Schließzeit bleiben zusammen, 12-Stunden-Zeiten ohne führende Null, Zeitformat folgt dem HA-Profil.

## 0.7.2 (2026-11-17)

Dashboard: current sun position (direction, elevation, rising/setting) shown below the brightness history. / Dashboard: aktueller Sonnenstand (Richtung, Höhe, steigt/sinkt) unter dem Helligkeitsverlauf.

## 0.7.1 (2026-11-17)

Dashboard dialog: time fields (daily summary time, shutter times) are now shown reliably. / Dashboard-Dialog: Uhrzeit-Felder (Zeit der Tageszusammenfassung, Zeiten der Rollläden) werden jetzt zuverlässig angezeigt.

## 0.7.0 – Reparaturen, Umbenennungen, robuster bei Aussetzern (2026-11-17)

**Neu**
- **Umbenannte Entitäten** werden automatisch übernommen – auch Umbenennungen, während die Integration nicht lief.
- **Fehlende oder deaktivierte Entitäten** erscheinen unter *Einstellungen → Reparaturen*; dort direkt einen Ersatz wählen.
- **Startsicherheit:** Fahrbefehle warten nach einem Start, bis Home Assistant läuft und der Rollladen erreichbar ist (max. 5 Min.); beim Herunterfahren wird nichts gesendet.

**Behoben**
- Ein gekipptes Fenster, dessen Kontakt kurz nicht erreichbar war (Neustart, Funkaussetzer), ließ den Rollladen nach dem Schließen auf Lüften stehen. Der letzte gültige Kontaktzustand wird jetzt gemerkt, auch über Neustarts.
- Namen in den Karten werden HTML-sicher angezeigt.

---

**New:** renamed entities are followed automatically; missing/disabled entities are reported under *Repairs* with a replacement dialog; commands wait for HA and the shutter after a start and are not sent during shutdown.
**Fixed:** a tilted window whose contact was briefly unavailable no longer loses the return-from-ventilation position; names in the cards are HTML-escaped.

## 0.6.2 – Screenshot in der Anleitung (2026-11-17)

Anleitung mit Screenshot des Dashboards. Keine Änderung an der Funktion.

README with a dashboard screenshot. No functional changes.

## 0.6.1 – Marketplace-Button (2026-11-17)

Anleitung: Button „In Home Assistant öffnen“ für Marketplace/HACS. Keine Änderung an der Funktion.

README: "Open in Home Assistant" button for the Marketplace/HACS. No functional changes.

## 0.6.0 – Automatische Dashboard-Abschnitte (2026-11-17)

**Neu (ab Home Assistant 2026.11):** automatische Abschnitte für eigene, frei anordenbare Dashboards – *Abschnitt hinzufügen → Automatischer Abschnitt → Community*:
- **Rollläden (Rollladensteuerung):** alle Rollläden eines Stockwerks; neue Rollläden erscheinen automatisch
- **Rollladensteuerung – Automatik:** Zentrale mit Schaltern und Alle-Buttons
- **Rollladensteuerung – Benachrichtigungen:** Push-Schalter und Protokoll

Abschnitte frei verschieben und mit eigenen Karten mischen; die Anordnung übersteht Updates. Die Dashboard-Vorlage ist außerdem unter *Neues Dashboard → Community* auswählbar.

**New (Home Assistant 2026.11+):** automatic sections for your own, freely arranged dashboards – *Add section → Automatic section → Community*. New shutters still appear automatically in their floor's section.

## 0.5.1 – Kleinigkeiten (2026-11-17)

- Zentrale und Haupteinstellungen zeigen die Version: „Rollladensteuerung (0.5.1)“. / Version shown in the central card.
- Schalter heißt „Push Zusammenfassung“ (Anzeige „Zusammenfassung“); lange Namen in den Knöpfen werden abgeschnitten statt überzulaufen. / Shorter label, no overflow.

## 0.5.0 – Brandschutz, Hitzeschutz, Dämmerung, Urlaub, Zusammenfassung (2026-11-17)

Neu / New
- Brandschutz: bei Rauchalarm alle Rollläden öffnen, bis Alarmende nichts automatisch herunterfahren (Haupteinstellungen → Rauchmelder).
- Hitzeschutz bei Abwesenheit: ab X °C (außen oder Vorhersage) dunkler abschatten.
- Abends schließen, sobald es dunkler als X Lux ist (nicht vor „Schließen frühestens“).
- Urlaubsmodus (Schalter in der Zentrale): Wochenend-/Feiertagszeiten und zusätzliche Zufallsminuten.
- Tageszusammenfassung als Push (Schalter bei den Benachrichtigungen, Uhrzeit einstellbar, Dienst zusammenfassung_senden).
- Dashboard-Vorlage: Stockwerke zuerst, Zentrale dahinter (Option steuerung: vorne).

Behoben / Fixed
- Homematic meldet beim Losfahren kurz die Zielposition: Fahrten wurden doppelt bzw. automatische Fahrten als „von Hand“ erkannt. Jetzt wird erst ausgewertet, wenn der Rollladen steht.

## 0.4.0 – Benachrichtigungen und Protokoll (2026-11-17)

Neu / New
- Push-Dienst in den Haupteinstellungen (HA-App, Pushover, … / any notify service).
- Push-Schalter: Öffnen gestartet, Schließen gestartet (je eine Nachricht für alle), Warnhinweise, Lüften, Abschatten (Anfang/Ende), Funktionen, manuelle Fahrten.
- Warnhinweise: wegen Frost nicht geöffnet, Fenster beim Schließen offen, Aussperrschutz, Sensor/Rollladen 15 min nicht erreichbar (höchstens einmal am Tag), Zielposition nicht erreicht.
- Protokoll der letzten 14 Tage mit allen Aktionen – im Dashboard ansehen, filtern, als CSV speichern (auf dem Handy über Teilen).
- Karte „Benachrichtigungen & Protokoll“ (custom:rollladensteuerung-meldungen-card), in der Vorlage unter der Zentrale.

Push notifications, 14-day action log with CSV export, availability and target-position warnings.

## 0.3.4 – Anzeige bei ausgeschaltetem Öffnen/Schließen (2026-11-16)

Behoben / Fixed
- Ist „Automatisch öffnen“ bzw. „schließen“ auf „aus“ gestellt oder die Automatik des Rollladens aus, zeigen Karte, Dialog und Sensor keine Zeit mehr an, sondern „aus“. / No next time is shown when opening/closing is set to off or the shutter's automation is off.

## 0.3.3 – Alle abschatten, Neuberechnung (2026-11-16)

Neu / New
- Knopf und Dienst „Alle abschatten“ (rollladensteuerung.alle_abschatten): alle Rollläden mit eingeschalteter Abschattung fahren gestaffelt auf ihre Abschattungsposition – nur nach unten. / Button and service "Shade all".

Behoben / Fixed
- Nach Änderungen an Astro-Modus, Horizont, Zeiten, Versatz oder Zufall werden die nächsten Öffnen-/Schließzeiten sofort neu berechnet (bisher erst nach der nächsten Fahrt bzw. um 03:05). / Opening/closing times are recalculated immediately after settings change.

## 0.3.2 – Icon (2026-11-16)

Neu: eigenes Icon für die Integration (hell und dunkel). / New: integration icon (light and dark).

## 0.3.1 – erste Veröffentlichung / first release (2026-11-16)

Erste öffentliche Version der Rollladensteuerung für Home Assistant (Nachbau der FHEM-Rollladensteuerung). Anleitung: README.de.md

First public release of the shutter control for Home Assistant (port of the FHEM shutter control). Documentation: README.md
