/*
 * Rollladensteuerung – Frontend
 *  - custom:rollladensteuerung-card          Rollladen mit Tasten, Regler, Automatik-Zeile und Zahnrad
 *  - custom:rollladensteuerung-zentrale-card Globale Schalter, nächste Zeiten, Alle öffnen/schließen, Zahnrad
 *  - custom:rollladensteuerung-sonne-card    Sonnenstand als Textzeile (unter dem Helligkeitsverlauf)
 *  - Ansichts-/Dashboard-Vorlage (strategy) custom:rollladensteuerung – baut die Ansicht aus allen
 *    eingerichteten Rollläden (nach Stockwerk gruppiert), neue Rollläden erscheinen automatisch.
 *  - Abschnitts-Vorlagen (section strategies, ab HA 2026.11) für frei anordenbare Dashboards:
 *    custom:rollladensteuerung (Rollläden eines Stockwerks), custom:rollladensteuerung-steuerung,
 *    custom:rollladensteuerung-meldungen
 */
const VERSION = "0.8.0";

const TEXTE = {
  de: {
    speichern: "Speichern", abbrechen: "Abbrechen", schliessen: "Schließen", status: "Status",
    einstellungen: "Einstellungen", alle_oeffnen: "Alle öffnen", alle_schliessen: "Alle schließen", alle_lueften: "Alle lüften", alle_abschatten: "Alle abschatten",
    raumtemp: "Raumtemperatur", vorhersage: "Heute erwartet (max.)", schlaeft: "Schläft noch", schatten_ziel: "Abschattungsposition jetzt",
    oeffnet: "Öffnet", schliesst: "Schließt", automatik: "Automatik", zentrale: "Rollladensteuerung",
    gespeichert: "Gespeichert", fehler: "Fehler", hinzufuegen: "Rollladen oder Helligkeitssensor hinzufügen/löschen",
    helligkeit: "Helligkeitssensoren", rolllaeden: "Rollläden", allgemein: "Allgemein",
    letzte_meldung: "Letzte Meldung", fenster: "Fenster", helligkeit_akt: "Helligkeit",
    bereich: "Abschattungsbereich", im_bereich: "Sonne im Bereich", in_abschattung: "Abgeschattet",
    vorgemerkt: "Abschatten vorgemerkt", ende_vorgemerkt: "Abschattungsende vorgemerkt",
    nach_schliessen: "Abschatten nach Schließen", nachtschliessen: "Nachtschließen ausstehend",
    manuell: "Zuletzt von Hand gefahren", zaehler: "Abschattungsfahrten heute (runter/hoch)",
    zaehler_gestern: "Abschattungsfahrten gestern", ja: "ja", nein: "nein", unbekannt: "–",
    offen: "offen", zu: "zu", gekippt: "gekippt", laedt: "Lädt …", naechstes_oeffnen: "Nächstes Öffnen",
    naechstes_schliessen: "Nächstes Schließen", keine_konfig: "Rollladensteuerung ist nicht eingerichtet.",
    nur_admin: "Nur Administratoren können Einstellungen ändern.", aus: "aus", auswaehlen: "Entität wählen oder tippen …", entfernen: "Entfernen", meldungen: "Benachrichtigungen & Protokoll",
    kein_push: "Kein Push-Dienst gewählt – Zahnrad der Rollladensteuerung → Allgemein → Push-Dienst.", push_ueber: "Push über",
    protokoll: "Protokoll", protokoll_anzeigen: "Protokoll anzeigen", protokoll_speichern: "Protokoll speichern",
    p_heute: "Heute", p_gestern: "Gestern", p_7t: "7 Tage", p_30t: "30 Tage", p_alles: "Alles", p_von: "Von", p_bis: "Bis",
    p_anzeigen: "Anzeigen", p_ausblenden: "Ausblenden", p_herunterladen: "Herunterladen (CSV)", p_rolllaeden: "Rollläden",
    p_arten: "Ereignisse", p_alle: "Alle", p_leer: "Keine Einträge für diese Auswahl.", p_zeitraum_fehlt: "Bitte Von und Bis angeben.",
    p_mehr: "Angezeigt werden die neuesten 2000 Einträge – die CSV-Datei enthält alle.", datum: "Datum", uhrzeit: "Uhrzeit",
    f_zeitraum: "Zeitraum beim Öffnen", f_rolllaeden: "Nur diese Rollläden (leer = alle)", f_arten: "Nur diese Ereignisse (leer = alle)",
    f_anzeigen: "Einträge sofort anzeigen", f_filter: "Filter auf der Karte anzeigen",
    v_protokoll: "Rollladensteuerung – Protokoll", v_protokoll_text: "Protokoll mit Zeitraum, Filtern und CSV-Download",
    alle_rolllaeden: "Alle Rollläden", alle_arten: "Alle Arten", suchen: "Suchen …", zeit: "Zeit", rollladen: "Rollladen",
    art: "Art", meldung: "Meldung", eintraege: "Einträge",
    f_stockwerk: "Stockwerk", f_titel: "Überschrift (leer = automatisch)", f_verlauf: "Helligkeitsverlauf anzeigen", sonne_titel: "Sonne", sonne_hoehe: "Höhe", sonne_steigt: "steigt", sonne_sinkt: "sinkt", sonne_unter: "unter dem Horizont", sonne_stand: "Stand",
    richtungen: "N,NNO,NO,ONO,O,OSO,SO,SSO,S,SSW,SW,WSW,W,WNW,NW,NNW",
    alle_stockwerke: "Alle Rollläden", ohne_stockwerk: "Rollläden ohne Stockwerk", stock_fehlt: "Dieses Stockwerk gibt es nicht mehr.",
    keine_rolllaeden: "Keine Rollläden in diesem Stockwerk.",
    v_rolllaeden: "Rollläden (Rollladensteuerung)", v_rolllaeden_text: "Alle Rollläden eines Stockwerks – neue erscheinen automatisch",
    v_steuerung: "Rollladensteuerung – Automatik", v_steuerung_text: "Globale Schalter, Alle-Buttons, Einstellungen",
    v_meldungen: "Rollladensteuerung – Benachrichtigungen", v_meldungen_text: "Push-Schalter und Protokoll",
    v_dashboard_text: "Alle Rollläden nach Stockwerk mit Automatik und Benachrichtigungen",
  },
  en: {
    speichern: "Save", abbrechen: "Cancel", schliessen: "Close", status: "Status",
    einstellungen: "Settings", alle_oeffnen: "Open all", alle_schliessen: "Close all", alle_lueften: "Ventilate all", alle_abschatten: "Shade all",
    raumtemp: "Room temperature", vorhersage: "Forecast today (max)", schlaeft: "Still asleep", schatten_ziel: "Shading position now",
    oeffnet: "Opens", schliesst: "Closes", automatik: "Automation", zentrale: "Shutter control",
    gespeichert: "Saved", fehler: "Error", hinzufuegen: "Add/remove shutters or brightness sensors",
    helligkeit: "Brightness sensors", rolllaeden: "Shutters", allgemein: "General",
    letzte_meldung: "Last message", fenster: "Window", helligkeit_akt: "Brightness",
    bereich: "Shading range", im_bereich: "Sun in range", in_abschattung: "Shaded",
    vorgemerkt: "Shading scheduled", ende_vorgemerkt: "Shading end scheduled",
    nach_schliessen: "Shade after closing", nachtschliessen: "Night close pending",
    manuell: "Last moved manually", zaehler: "Shading moves today (down/up)",
    zaehler_gestern: "Shading moves yesterday", ja: "yes", nein: "no", unbekannt: "–",
    offen: "open", zu: "closed", gekippt: "tilted", laedt: "Loading …", naechstes_oeffnen: "Next opening",
    naechstes_schliessen: "Next closing", keine_konfig: "Shutter control is not set up.",
    nur_admin: "Only administrators can change settings.", aus: "off", auswaehlen: "Pick or type an entity …", entfernen: "Remove", meldungen: "Notifications & log",
    kein_push: "No push service selected – gear of the shutter control → General → push service.", push_ueber: "Push via",
    protokoll: "Log", protokoll_anzeigen: "Show log", protokoll_speichern: "Save log",
    p_heute: "Today", p_gestern: "Yesterday", p_7t: "7 days", p_30t: "30 days", p_alles: "All", p_von: "From", p_bis: "To",
    p_anzeigen: "Show", p_ausblenden: "Hide", p_herunterladen: "Download (CSV)", p_rolllaeden: "Shutters",
    p_arten: "Events", p_alle: "All", p_leer: "No entries for this selection.", p_zeitraum_fehlt: "Please enter from and to.",
    p_mehr: "Showing the newest 2000 entries – the CSV file contains all of them.", datum: "Date", uhrzeit: "Time",
    f_zeitraum: "Period when opened", f_rolllaeden: "Only these shutters (empty = all)", f_arten: "Only these events (empty = all)",
    f_anzeigen: "Show entries right away", f_filter: "Show filters on the card",
    v_protokoll: "Shutter control – log", v_protokoll_text: "Log with period, filters and CSV download",
    alle_rolllaeden: "All shutters", alle_arten: "All types", suchen: "Search …", zeit: "Time", rollladen: "Shutter",
    art: "Type", meldung: "Message", eintraege: "entries",
    f_stockwerk: "Floor", f_titel: "Heading (empty = automatic)", f_verlauf: "Show brightness history", sonne_titel: "Sun", sonne_hoehe: "elevation", sonne_steigt: "rising", sonne_sinkt: "setting", sonne_unter: "below the horizon", sonne_stand: "as of",
    richtungen: "N,NNE,NE,ENE,E,ESE,SE,SSE,S,SSW,SW,WSW,W,WNW,NW,NNW",
    alle_stockwerke: "All shutters", ohne_stockwerk: "Shutters without floor", stock_fehlt: "This floor no longer exists.",
    keine_rolllaeden: "No shutters on this floor.",
    v_rolllaeden: "Shutters (Rollladensteuerung)", v_rolllaeden_text: "All shutters of a floor – new ones appear automatically",
    v_steuerung: "Shutter control – automation", v_steuerung_text: "Global switches, all buttons, settings",
    v_meldungen: "Shutter control – notifications", v_meldungen_text: "Push switches and log",
    v_dashboard_text: "All shutters by floor with automation and notifications",
  },
};
// Text sicher ins HTML einsetzen (Namen kommen aus Einstellungen und anderen Integrationen)
const esc = (text) => String(text ?? "").replace(/[&<>"']/g, (z) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[z]);
const tx = (hass, key) => (TEXTE[(hass?.language || "en").split("-")[0]] || TEXTE.en)[key] || key;

/* ---------------------------------------------------------------- Konfiguration (zwischengespeichert) */
let _konfig = null;
function ladeKonfig(hass, neu = false) {
  if (!_konfig || neu) {
    _konfig = hass.callWS({ type: "rollladensteuerung/konfig" }).catch((e) => { _konfig = null; throw e; });
  }
  return _konfig;
}
let _konfigZeit = 0;
function frischeKonfig(hass) {
  const neu = Date.now() - _konfigZeit > 3000;
  if (neu) _konfigZeit = Date.now();
  return ladeKonfig(hass, neu);
}
function konfigNeu(hass) {
  return ladeKonfig(hass, true).then((k) => {
    window.dispatchEvent(new CustomEvent("rollladensteuerung-konfig", { detail: k }));
    return k;
  });
}

async function haFormBereit() {
  if (customElements.get("ha-form")) return;
  try {
    const helfer = await window.loadCardHelpers();
    const karte = await helfer.createCardElement({ type: "entities", entities: [] });
    if (karte?.constructor?.getConfigElement) await karte.constructor.getConfigElement();
  } catch (e) { /* weiter versuchen */ }
  if (!customElements.get("ha-form")) {
    try { await customElements.get("hui-tile-card")?.getConfigElement?.(); } catch (e) { /* egal */ }
  }
  await Promise.race([customElements.whenDefined("ha-form"), new Promise((r) => setTimeout(r, 6000))]);
}

function zeit(hass, wert) {
  if (!wert || ["unknown", "unavailable"].includes(wert)) return "–";
  const d = new Date(wert);
  if (isNaN(d)) return "–";
  const sprache = hass?.locale?.language || hass?.language || "de";
  const heute = new Date();
  // Zeitformat aus dem HA-Profil (12/24 h); bei 12 h ohne führende Null, damit die Zeile kurz bleibt
  const tf = hass?.locale?.time_format;
  const hour12 = tf === "12" ? true : tf === "24" ? false : undefined;
  const zwoelf = new Intl.DateTimeFormat(sprache, { hour: "numeric", hour12 }).resolvedOptions().hour12;
  const uhr = d.toLocaleTimeString(sprache, { hour: zwoelf ? "numeric" : "2-digit", minute: "2-digit", hour12 });
  if (d.toDateString() === heute.toDateString()) return uhr;
  return `${d.toLocaleDateString(sprache, { weekday: "short" })} ${uhr}`;
}

// [Öffnen aus, Schließen aus] – Automatik des Rollladens aus oder Modus „aus“
function automatikAus(hass, rl) {
  const aus = hass.states[rl?.entities?.automatik]?.state === "off";
  return [aus || rl?.daten?.modus_hoch === "aus", aus || rl?.daten?.modus_runter === "aus"];
}

function navigieren(pfad) {
  history.pushState(null, "", pfad);
  window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
}

function mehrInfo(element, entityId) {
  element.dispatchEvent(new CustomEvent("hass-more-info", { bubbles: true, composed: true, detail: { entityId } }));
}

const GEMEINSAM_CSS = `
  :host { display: block; }
  ha-card { padding: 12px; box-sizing: border-box; height: 100%; display: flex; flex-direction: column; gap: 10px; }
  .kopf { display: flex; align-items: center; gap: 10px; min-height: 40px; }
  .symbol { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    background: rgba(var(--rgb-farbe, 158,158,158), 0.2); color: rgb(var(--rgb-farbe, 158,158,158)); cursor: pointer; flex: none; }
  .text { flex: 1; min-width: 0; cursor: pointer; }
  .name { font-weight: 500; font-size: 14px; line-height: 20px; color: var(--primary-text-color);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .zustand { font-size: 12px; line-height: 16px; color: var(--secondary-text-color);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  button.rund { border: none; background: rgba(var(--rgb-primary-text-color, 0,0,0), 0.05); color: var(--primary-text-color);
    width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; cursor: pointer; flex: none; }
  button.rund:hover { background: rgba(var(--rgb-primary-text-color, 0,0,0), 0.1); }
  .tasten { display: flex; gap: 10px; flex-wrap: wrap; }
  .tasten button { flex: 1 1 0; min-width: 0; height: 42px; white-space: nowrap; font: inherit; font-size: 13px; padding: 0 8px; border: none; border-radius: 12px; cursor: pointer;
    background: rgba(var(--rgb-primary-text-color, 0,0,0), 0.05); color: var(--primary-text-color);
    display: flex; align-items: center; justify-content: center; }
  .tasten button:disabled { color: var(--disabled-text-color); cursor: default; }
  .tasten button:not(:disabled):hover { background: rgba(var(--rgb-primary-text-color, 0,0,0), 0.1); }
  .regler { position: relative; height: 42px; border-radius: 12px; overflow: hidden; cursor: pointer; touch-action: none;
    background: rgba(var(--rgb-farbe, 146,107,199), 0.2); }
  .fuellung { position: absolute; left: 0; top: 0; bottom: 0; background: rgba(var(--rgb-farbe, 146,107,199), 0.35); }
  .griff { position: absolute; top: 9px; bottom: 9px; width: 4px; margin-left: -10px; border-radius: 2px;
    background: rgb(var(--rgb-farbe, 146,107,199)); }
  .auto { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--secondary-text-color); flex-wrap: wrap; }
  .auto ha-icon { --mdc-icon-size: 16px; }
  .auto .status { font-weight: 500; color: var(--primary-text-color); }
  .auto .zeiten { display: inline-flex; gap: 8px; white-space: nowrap; }
`;

/* ---------------------------------------------------------------- Rollladen-Karte */
class RollladenKarte extends HTMLElement {
  setConfig(config) {
    if (!config.entity && !config.sid) throw new Error("entity (Rollladen) fehlt");
    this._config = config;
  }
  static getStubConfig(hass) {
    const cover = Object.keys(hass.states).find((e) => e.startsWith("cover."));
    return { entity: cover || "" };
  }
  getCardSize() { return 4; }
  getGridOptions() { return { columns: 6, min_columns: 6, rows: "auto" }; }

  connectedCallback() {
    this._aktualisieren = (ev) => { this._rl = this._finde(ev.detail); this._zeichnen(); };
    window.addEventListener("rollladensteuerung-konfig", this._aktualisieren);
  }
  disconnectedCallback() { window.removeEventListener("rollladensteuerung-konfig", this._aktualisieren); }

  _finde(k) {
    if (!k) return null;
    return k.rolllaeden.find((r) => (this._config.sid ? r.sid === this._config.sid : r.cover === this._config.entity)) || null;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._aufgebaut) this._aufbauen();
    if (this._rl === undefined) {
      this._rl = null;
      ladeKonfig(hass).then((k) => { this._konfig = k; this._rl = this._finde(k); this._zeichnen(); }).catch(() => {});
    }
    this._zeichnen();
  }

  get _cover() { return this._rl?.cover || this._config.entity; }

  _aufbauen() {
    this._aufgebaut = true;
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `
      <style>${GEMEINSAM_CSS}</style>
      <ha-card>
        <div class="kopf">
          <div class="symbol"><ha-state-icon></ha-state-icon></div>
          <div class="text"><div class="name"></div><div class="zustand"></div></div>
          <button class="rund zahnrad" title="${tx(this._hass, "einstellungen")}"><ha-icon icon="mdi:cog"></ha-icon></button>
        </div>
        <div class="tasten">
          <button data-dienst="open_cover"><ha-icon icon="mdi:arrow-up"></ha-icon></button>
          <button data-dienst="stop_cover"><ha-icon icon="mdi:stop"></ha-icon></button>
          <button data-dienst="close_cover"><ha-icon icon="mdi:arrow-down"></ha-icon></button>
        </div>
        <div class="regler"><div class="fuellung"></div><div class="griff"></div></div>
        <div class="auto"><ha-icon icon="mdi:window-shutter-auto"></ha-icon><span class="status"></span>
          <span class="zeiten"><span class="hoch"></span><span class="runter"></span></span></div>
      </ha-card>`;
    root.querySelector(".symbol").addEventListener("click", () => mehrInfo(this, this._cover));
    root.querySelector(".text").addEventListener("click", () => mehrInfo(this, this._cover));
    root.querySelector(".zahnrad").addEventListener("click", () => this._dialog());
    root.querySelectorAll(".tasten button").forEach((b) =>
      b.addEventListener("click", () => this._hass.callService("cover", b.dataset.dienst, { entity_id: this._cover })));
    const regler = root.querySelector(".regler");
    const wert = (ev) => {
      const r = regler.getBoundingClientRect();
      return Math.round(Math.min(100, Math.max(0, ((ev.clientX - r.left) / r.width) * 100)));
    };
    regler.addEventListener("pointerdown", (ev) => {
      regler.setPointerCapture(ev.pointerId);
      this._ziehen = wert(ev);
      this._regler(this._ziehen);
    });
    regler.addEventListener("pointermove", (ev) => {
      if (this._ziehen === undefined) return;
      this._ziehen = wert(ev);
      this._regler(this._ziehen);
    });
    const ende = () => {
      if (this._ziehen === undefined) return;
      const p = this._ziehen;
      this._ziehen = undefined;
      this._hass.callService("cover", "set_cover_position", { entity_id: this._cover, position: p });
    };
    regler.addEventListener("pointerup", ende);
    regler.addEventListener("pointercancel", ende);
  }

  _regler(p) {
    const r = this.shadowRoot;
    r.querySelector(".fuellung").style.width = `${p}%`;
    r.querySelector(".griff").style.left = `calc(${p}% + ${p < 3 ? 10 : 0}px)`;
  }

  _zeichnen() {
    if (!this._hass || !this.shadowRoot) return;
    const r = this.shadowRoot;
    const st = this._hass.states[this._cover];
    const name = this._config.name || this._rl?.name || st?.attributes?.friendly_name || this._cover;
    r.querySelector(".name").textContent = name;
    if (!st) { r.querySelector(".zustand").textContent = this._cover; return; }
    const pos = st.attributes.current_position;
    const offen = st.state !== "closed";
    this.style.setProperty("--rgb-farbe", offen ? "146, 107, 199" : "158, 158, 158");
    const icon = r.querySelector("ha-state-icon");
    icon.hass = this._hass;
    icon.stateObj = st;
    const text = this._hass.formatEntityState ? this._hass.formatEntityState(st) : st.state;
    r.querySelector(".zustand").textContent = pos !== undefined ? `${text} · ${pos} %` : text;
    const [hoch, halt, runter] = r.querySelectorAll(".tasten button");
    hoch.disabled = pos === 100 || st.state === "opening";
    runter.disabled = pos === 0 || st.state === "closing";
    halt.disabled = false;
    if (this._ziehen === undefined) this._regler(pos ?? (offen ? 100 : 0));
    const auto = r.querySelector(".auto");
    if (!this._rl) { auto.style.display = "none"; return; }
    auto.style.display = "";
    const ents = this._rl.entities;
    const s = this._hass.states[ents.status];
    const texte = this._konfig?.status_texte || {};
    r.querySelector(".status").textContent = s ? (texte[s.state] || s.state) : "–";
    const [hochAus, runterAus] = automatikAus(this._hass, this._rl);
    r.querySelector(".hoch").textContent = `↑ ${hochAus ? tx(this._hass, "aus") : zeit(this._hass, this._hass.states[ents.oeffnen]?.state)}`;
    r.querySelector(".runter").textContent = `↓ ${runterAus ? tx(this._hass, "aus") : zeit(this._hass, this._hass.states[ents.schliessen]?.state)}`;
  }

  async _dialog() {
    const k = await ladeKonfig(this._hass).catch(() => null);
    this._konfig = k;
    this._rl = this._finde(k);
    if (!this._rl) { mehrInfo(this, this._cover); return; }
    oeffneDialog(this._hass, k, "rollladen", this._rl);
  }
}

/* ---------------------------------------------------------------- Zentrale-Karte */
const SCHALTER_SYMBOL = { morgens: "mdi:weather-sunset-up", abends: "mdi:weather-sunset-down", abschattung: "mdi:sun-angle",
  komfort: "mdi:window-open-variant", partymodus: "mdi:party-popper", gast: "mdi:account-clock", urlaub: "mdi:palm-tree" };

class ZentraleKarte extends HTMLElement {
  setConfig(config) { this._config = config || {}; }
  connectedCallback() {
    this._neu = (ev) => { this._konfig = ev.detail; if (this.shadowRoot) { this._schalterBauen(); this._zeichnen(); } };
    window.addEventListener("rollladensteuerung-konfig", this._neu);
  }
  disconnectedCallback() { window.removeEventListener("rollladensteuerung-konfig", this._neu); }
  static getStubConfig() { return {}; }
  getCardSize() { return 5; }
  getGridOptions() { return { columns: 12, min_columns: 6, rows: "auto" }; }

  set hass(hass) {
    this._hass = hass;
    if (!this._aufgebaut) this._aufbauen();
    if (!this._konfig && !this._laedt) {
      this._laedt = true;
      ladeKonfig(hass).then((k) => { this._konfig = k; this._schalterBauen(); this._zeichnen(); })
        .catch(() => { this.shadowRoot.querySelector(".schalter").textContent = tx(hass, "keine_konfig"); });
    }
    this._zeichnen();
  }

  _aufbauen() {
    this._aufgebaut = true;
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `
      <style>${GEMEINSAM_CSS}
        .schalter { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
        .schalter button span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
        .schalter button ha-icon { flex: none; }
        .schalter button { display: flex; align-items: center; gap: 8px; padding: 0 10px; height: 44px; border: none; min-width: 0;
          border-radius: 12px; cursor: pointer; text-align: left; font: inherit; font-size: 13px;
          background: rgba(var(--rgb-primary-text-color, 0,0,0), 0.05); color: var(--primary-text-color); }
        .schalter button.an { background: rgba(var(--rgb-primary-color, 3,169,244), 0.18); }
        .schalter button.an ha-icon { color: var(--primary-color); }
        .alle button { min-width: 130px; }
        .zeiten { display: flex; gap: 16px; font-size: 13px; color: var(--secondary-text-color); flex-wrap: wrap; }
        .zeiten b { color: var(--primary-text-color); font-weight: 500; }
      </style>
      <ha-card>
        <div class="kopf">
          <div class="symbol" style="--rgb-farbe: var(--rgb-primary-color, 3,169,244)"><ha-icon icon="mdi:window-shutter-auto"></ha-icon></div>
          <div class="text"><div class="name titel">${this._config.title || tx(this._hass, "zentrale")}</div>
            <div class="zustand zeiten"></div></div>
          <button class="rund zahnrad" title="${tx(this._hass, "einstellungen")}"><ha-icon icon="mdi:cog"></ha-icon></button>
        </div>
        <div class="schalter"></div>
        <div class="tasten alle">
          <button data-dienst="alle_oeffnen"><ha-icon icon="mdi:arrow-up-box"></ha-icon>&nbsp;${tx(this._hass, "alle_oeffnen")}</button>
          <button data-dienst="alle_abschatten"><ha-icon icon="mdi:sun-angle"></ha-icon>&nbsp;${tx(this._hass, "alle_abschatten")}</button>
          <button data-dienst="alle_lueften"><ha-icon icon="mdi:window-open-variant"></ha-icon>&nbsp;${tx(this._hass, "alle_lueften")}</button>
          <button data-dienst="alle_schliessen"><ha-icon icon="mdi:arrow-down-box"></ha-icon>&nbsp;${tx(this._hass, "alle_schliessen")}</button>
        </div>
      </ha-card>`;
    root.querySelector(".zahnrad").addEventListener("click", async () => {
      const k = await konfigNeu(this._hass);
      oeffneDialog(this._hass, k, "global");
    });
    root.querySelectorAll(".tasten button").forEach((b) =>
      b.addEventListener("click", () => this._hass.callService("rollladensteuerung", b.dataset.dienst, {})));
  }

  _schalterBauen() {
    const feld = this.shadowRoot.querySelector(".schalter");
    feld.innerHTML = "";
    for (const [name, eid] of Object.entries(this._konfig.zentrale)) {
      if (!SCHALTER_SYMBOL[name] || !eid) continue;
      const b = document.createElement("button");
      b.dataset.entity = eid;
      b.innerHTML = `<ha-icon icon="${SCHALTER_SYMBOL[name]}"></ha-icon><span></span>`;
      b.addEventListener("click", () => this._hass.callService("switch", "toggle", { entity_id: eid }));
      feld.appendChild(b);
    }
  }

  _zeichnen() {
    if (!this._konfig || !this.shadowRoot) return;
    const r = this.shadowRoot;
    r.querySelectorAll(".schalter button").forEach((b) => {
      const st = this._hass.states[b.dataset.entity];
      b.classList.toggle("an", st?.state === "on");
      b.querySelector("span").textContent = st?.attributes?.friendly_name?.replace(/^Rollladensteuerung\s*/i, "") || b.dataset.entity;
    });
    const z = this._konfig.zentrale;
    const titel = this._config.title || tx(this._hass, "zentrale");
    r.querySelector(".titel").textContent = this._konfig.version ? `${titel} (${this._konfig.version})` : titel;
    r.querySelector(".zeiten").innerHTML =
      `<span>${tx(this._hass, "oeffnet")} <b>${zeit(this._hass, this._hass.states[z.oeffnen]?.state)}</b></span>` +
      `<span>${tx(this._hass, "schliesst")} <b>${zeit(this._hass, this._hass.states[z.schliessen]?.state)}</b></span>`;
  }
}

/* ---------------------------------------------------------------- Dialog mit Karteikarten */
function oeffneDialog(hass, konfig, art, rollladen) {
  const d = document.createElement("rollladensteuerung-dialog");
  d.einrichten(hass, konfig, art, rollladen);
  document.body.appendChild(d);
}

class EinstellDialog extends HTMLElement {
  einrichten(hass, konfig, art, rollladen) {
    this.hass = hass;
    this._k = konfig;
    this._art = art;
    this._rl = rollladen;
    if (art === "rollladen") {
      this._daten = { ...rollladen.daten };
      this._tabs = [{ key: "status", titel: tx(hass, "status") }, ...konfig.tabs];
    } else {
      this._daten = { ...konfig.global.daten };
      this._tabs = [{ key: "allgemein", titel: tx(hass, "allgemein") },
        { key: "liste", titel: `${tx(hass, "rolllaeden")} & ${tx(hass, "helligkeit")}` }];
    }
    this._tab = art === "rollladen" ? "status" : "allgemein";
  }

  connectedCallback() {
    const root = this.attachShadow({ mode: "open" });
    const titel = this._art === "rollladen" ? this._rl.name
      : `${tx(this.hass, "zentrale")}${this._k.version ? ` (${this._k.version})` : ""}`;
    root.innerHTML = `
      <style>
        .hinter { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 1000; display: flex;
          align-items: center; justify-content: center; padding: 16px; box-sizing: border-box; }
        .fenster { background: var(--ha-card-background, var(--card-background-color, #fff)); color: var(--primary-text-color);
          border-radius: 24px; width: 100%; max-width: 620px; max-height: 92vh; display: flex; flex-direction: column;
          box-shadow: 0 8px 32px rgba(0,0,0,0.3); overflow: hidden; font-family: var(--paper-font-body1_-_font-family, inherit); }
        .kopf { display: flex; align-items: center; padding: 16px 16px 4px 24px; gap: 8px; }
        .kopf h2 { flex: 1; margin: 0; font-size: 22px; font-weight: 400; }
        .kopf button { border: none; background: none; color: var(--primary-text-color); cursor: pointer; padding: 8px; border-radius: 50%; }
        .reiter { display: flex; gap: 4px; padding: 0 16px; overflow-x: auto; border-bottom: 1px solid var(--divider-color); flex: none; }
        .reiter button { border: none; background: none; padding: 12px 12px 10px; cursor: pointer; font: inherit; font-size: 14px;
          color: var(--secondary-text-color); border-bottom: 2px solid transparent; white-space: nowrap; }
        .reiter button.aktiv { color: var(--primary-color); border-bottom-color: var(--primary-color); font-weight: 500; }
        .inhalt { padding: 16px 24px; overflow-y: auto; flex: 1; min-height: 200px; }
        .fuss { display: flex; justify-content: flex-end; gap: 8px; padding: 12px 24px 20px; align-items: center; }
        .fuss .meldung { flex: 1; font-size: 13px; color: var(--error-color); }
        .fuss button { border: none; border-radius: 20px; padding: 10px 20px; font: inherit; font-weight: 500; cursor: pointer; }
        .fuss .neben { background: none; color: var(--primary-color); }
        .fuss .haupt { background: var(--primary-color); color: var(--text-primary-color, #fff); }
        .fuss .haupt:disabled { opacity: 0.5; cursor: default; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        td { padding: 7px 0; border-bottom: 1px solid var(--divider-color); vertical-align: top; }
        td:first-child { color: var(--secondary-text-color); padding-right: 12px; width: 48%; }
        .zeile { display: flex; align-items: center; justify-content: space-between; padding: 6px 0 12px; font-size: 15px; }
        ul { margin: 4px 0 16px; padding-left: 20px; }
        a { color: var(--primary-color); cursor: pointer; }
        h3 { font-size: 15px; font-weight: 500; margin: 12px 0 4px; }
        .auswahl { margin: 4px 0 20px; }
        .auswahl label { display: block; font-size: 14px; margin-bottom: 6px; color: var(--primary-text-color); }
        .auswahl .eingabe { display: flex; gap: 6px; align-items: center; }
        .auswahl input { flex: 1; font: inherit; font-size: 14px; padding: 12px; border-radius: 8px; box-sizing: border-box;
          border: 1px solid var(--outline-color, var(--divider-color)); background: var(--secondary-background-color, transparent);
          color: var(--primary-text-color); min-width: 0; }
        .auswahl .leeren { border: none; background: none; cursor: pointer; color: var(--secondary-text-color); }
        .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 6px; }
        .chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 4px 4px 12px; border-radius: 16px;
          background: rgba(var(--rgb-primary-color, 3,169,244), 0.15); font-size: 13px; }
        .chip small { color: var(--secondary-text-color); }
        .chip button { border: none; background: none; cursor: pointer; font-size: 16px; color: var(--primary-text-color); padding: 0 6px; }
        .info { font-size: 12px; color: var(--secondary-text-color); }
      </style>
      <div class="hinter">
        <div class="fenster" role="dialog" aria-modal="true">
          <div class="kopf"><h2></h2><button class="zu" title="${tx(this.hass, "schliessen")}"><ha-icon icon="mdi:close"></ha-icon></button></div>
          <div class="reiter"></div>
          <div class="inhalt"></div>
          <div class="fuss"><span class="meldung"></span>
            <button class="neben abbrechen">${tx(this.hass, "abbrechen")}</button>
            <button class="haupt speichern">${tx(this.hass, "speichern")}</button></div>
        </div>
      </div>`;
    root.querySelector("h2").textContent = titel;
    root.querySelector(".zu").addEventListener("click", () => this.remove());
    root.querySelector(".abbrechen").addEventListener("click", () => this.remove());
    root.querySelector(".hinter").addEventListener("click", (ev) => { if (ev.target === ev.currentTarget) this.remove(); });
    root.querySelector(".speichern").addEventListener("click", () => this._speichern());
    this._taste = (ev) => { if (ev.key === "Escape") this.remove(); };
    window.addEventListener("keydown", this._taste);
    const reiter = root.querySelector(".reiter");
    for (const t of this._tabs) {
      const b = document.createElement("button");
      b.textContent = t.titel;
      b.dataset.key = t.key;
      b.addEventListener("click", () => { this._tab = t.key; this._zeigen(); });
      reiter.appendChild(b);
    }
    if (!this.hass.user?.is_admin) {
      root.querySelector(".speichern").disabled = true;
      root.querySelector(".meldung").textContent = tx(this.hass, "nur_admin");
    }
    haFormBereit().then(() => this._zeigen());
    this._zeigen();
  }

  disconnectedCallback() { window.removeEventListener("keydown", this._taste); }

  _zeigen() {
    const root = this.shadowRoot;
    root.querySelectorAll(".reiter button").forEach((b) => b.classList.toggle("aktiv", b.dataset.key === this._tab));
    const inhalt = root.querySelector(".inhalt");
    inhalt.innerHTML = "";
    if (this._tab === "status") return this._status(inhalt);
    if (this._tab === "liste") return this._liste(inhalt);
    const schema = this._art === "global" ? this._k.global.schema : this._k.tabs.find((t) => t.key === this._tab)?.schema;
    const labels = this._art === "global" ? this._k.global.labels : this._k.labels;
    if (!customElements.get("ha-form")) { inhalt.textContent = tx(this.hass, "laedt"); return; }
    // Entitäten-Felder mit eigener Auswahl (HA lädt seine Entitäten-Auswahl nicht zuverlässig nach),
    // alle anderen Felder über ha-form – in der Reihenfolge des Schemas.
    let block = [];
    const blockSchreiben = () => {
      if (!block.length) return;
      const form = document.createElement("ha-form");
      form.hass = this.hass;
      form.schema = block;
      form.data = this._daten;
      form.computeLabel = (s) => labels[s.name] || s.name;
      form.addEventListener("value-changed", (ev) => { this._daten = { ...this._daten, ...ev.detail.value }; form.data = this._daten; });
      inhalt.appendChild(form);
      block = [];
    };
    for (const s of schema) {
      if (s.selector?.entity) {
        blockSchreiben();
        inhalt.appendChild(this._entitaetAuswahl(s, labels[s.name] || s.name));
      } else if (s.selector?.time) {
        blockSchreiben();
        inhalt.appendChild(this._zeitFeld(s, labels[s.name] || s.name));
      } else {
        block.push(s);
      }
    }
    blockSchreiben();
  }

  // Uhrzeit als eigenes Feld – HAs Zeitauswahl wird im Dashboard-Dialog nicht zuverlässig nachgeladen.
  _zeitFeld(s, label) {
    const box = document.createElement("div");
    box.className = "auswahl";
    box.innerHTML = `<label>${esc(label)}${s.required ? " *" : ""}</label>
      <div class="eingabe"><input type="time" step="1"></div>`;
    const eingabe = box.querySelector("input");
    const v = this._daten[s.name];
    eingabe.value = typeof v === "string" ? (v.length === 5 ? `${v}:00` : v.slice(0, 8)) : "";
    eingabe.addEventListener("change", () => {
      const w = eingabe.value;
      if (!w && s.required) { eingabe.setCustomValidity("?"); eingabe.reportValidity(); return; }
      eingabe.setCustomValidity("");
      this._daten = { ...this._daten, [s.name]: w ? (w.length === 5 ? `${w}:00` : w) : "" };
    });
    return box;
  }

  _entitaetAuswahl(s, label) {
    const h = this.hass;
    const cfg = s.selector.entity || {};
    const domains = cfg.domain ? [].concat(cfg.domain) : null;
    const ausnahmen = new Set(cfg.exclude_entities || []);
    const mehrfach = !!cfg.multiple;
    const passend = Object.values(h.states).filter((st) => {
      const [dom] = st.entity_id.split(".");
      if (domains && !domains.includes(dom)) return false;
      if (cfg.device_class && st.attributes.device_class !== cfg.device_class) return false;
      return !ausnahmen.has(st.entity_id);
    }).sort((a, b) => (a.attributes.friendly_name || a.entity_id).localeCompare(b.attributes.friendly_name || b.entity_id));
    const anzeige = (eid) => `${h.states[eid]?.attributes?.friendly_name || eid}`;
    const box = document.createElement("div");
    box.className = "auswahl";
    const listenId = `liste-${s.name}-${Math.random().toString(36).slice(2, 8)}`;
    box.innerHTML = `<label>${esc(label)}${s.required ? " *" : ""}</label><div class="chips"></div>
      <div class="eingabe"><input list="${listenId}" placeholder="${mehrfach ? "+ " : ""}${tx(h, "auswaehlen")}">
      <button class="leeren" title="${tx(h, "entfernen")}"><ha-icon icon="mdi:close"></ha-icon></button></div>
      <datalist id="${listenId}">${passend.map((st) => `<option value="${esc(st.entity_id)}">${esc(st.attributes.friendly_name || "")}</option>`).join("")}</datalist>`;
    const chips = box.querySelector(".chips");
    const eingabe = box.querySelector("input");
    const leeren = box.querySelector(".leeren");
    const wert = () => this._daten[s.name];
    const setzen = (v) => { this._daten = { ...this._daten, [s.name]: v }; zeichnen(); };
    const zeichnen = () => {
      chips.innerHTML = "";
      if (mehrfach) {
        for (const eid of wert() || []) {
          const c = document.createElement("span");
          c.className = "chip";
          c.innerHTML = `<span>${esc(anzeige(eid))}</span><small>${esc(eid)}</small><button title="${tx(h, "entfernen")}">×</button>`;
          c.querySelector("button").addEventListener("click", () => setzen((wert() || []).filter((x) => x !== eid)));
          chips.appendChild(c);
        }
        eingabe.value = "";
        leeren.style.display = "none";
      } else {
        const v = wert();
        eingabe.value = v || "";
        eingabe.title = v ? anzeige(v) : "";
        leeren.style.display = v ? "" : "none";
        if (v) {
          const c = document.createElement("span");
          c.className = "info";
          c.textContent = anzeige(v);
          chips.appendChild(c);
        }
      }
    };
    eingabe.addEventListener("change", () => {
      const v = eingabe.value.trim();
      if (!v) { if (!mehrfach) setzen(""); return; }
      if (!h.states[v]) { eingabe.setCustomValidity("?"); eingabe.reportValidity(); return; }
      eingabe.setCustomValidity("");
      if (mehrfach) { const liste = wert() || []; if (!liste.includes(v)) setzen([...liste, v]); else zeichnen(); }
      else setzen(v);
    });
    leeren.addEventListener("click", () => setzen(mehrfach ? [] : ""));
    zeichnen();
    return box;
  }

  _status(inhalt) {
    const h = this.hass;
    const ents = this._rl.entities;
    const s = h.states[ents.status];
    const a = s?.attributes || {};
    const ja = (v) => (v === true ? tx(h, "ja") : v === false ? tx(h, "nein") : tx(h, "unbekannt"));
    const fenster = { open: tx(h, "offen"), closed: tx(h, "zu"), tilted: tx(h, "gekippt") };
    const zeilen = [
      [tx(h, "status"), s ? (this._k.status_texte[s.state] || s.state) : "–"],
      [tx(h, "letzte_meldung"), a.letzte_meldung || "–"],
      [tx(h, "naechstes_oeffnen"), automatikAus(h, this._rl)[0] ? tx(h, "aus") : zeit(h, h.states[ents.oeffnen]?.state)],
      [tx(h, "naechstes_schliessen"), automatikAus(h, this._rl)[1] ? tx(h, "aus") : zeit(h, h.states[ents.schliessen]?.state)],
      [tx(h, "fenster"), a.fenster ? (fenster[a.fenster] || a.fenster) : "–"],
      [tx(h, "helligkeit_akt"), a.helligkeit != null ? `${Math.round(a.helligkeit)} lx` : "–"],
      [tx(h, "raumtemp"), a.raumtemperatur != null ? `${a.raumtemperatur} °C` : "–"],
      [tx(h, "vorhersage"), a.vorhersage_max != null ? `${a.vorhersage_max} °C` : "–"],
      [tx(h, "schlaeft"), ja(a.schlaeft)],
      [tx(h, "bereich"), a.abschattungsbereich || "–"],
      [tx(h, "schatten_ziel"), a.abschattung_ziel != null ? `${a.abschattung_ziel} %` : "–"],
      [tx(h, "im_bereich"), ja(a.im_abschattungsbereich)],
      [tx(h, "in_abschattung"), ja(a.in_abschattung)],
      [tx(h, "vorgemerkt"), ja(a.abschatten_vorgemerkt)],
      [tx(h, "ende_vorgemerkt"), ja(a.abschattung_ende_vorgemerkt)],
      [tx(h, "nach_schliessen"), ja(a.abschatten_nach_schliessen)],
      [tx(h, "nachtschliessen"), ja(a.nachtschliessen)],
      [tx(h, "manuell"), a.manuell_gefahren ? zeit(h, a.manuell_gefahren) : "–"],
      [tx(h, "zaehler"), `${a.zaehler_runter ?? 0} / ${a.zaehler_hoch ?? 0}`],
      [tx(h, "zaehler_gestern"), `${a.zaehler_runter_gestern ?? 0} / ${a.zaehler_hoch_gestern ?? 0}`],
    ];
    const auto = h.states[ents.automatik];
    const zeile = document.createElement("div");
    zeile.className = "zeile";
    zeile.innerHTML = `<span>${tx(h, "automatik")}</span>`;
    const schalter = document.createElement("ha-switch");
    schalter.checked = auto?.state === "on";
    schalter.addEventListener("change", () =>
      h.callService("switch", schalter.checked ? "turn_on" : "turn_off", { entity_id: ents.automatik }));
    zeile.appendChild(schalter);
    inhalt.appendChild(zeile);
    const tabelle = document.createElement("table");
    for (const [k, v] of zeilen) {
      const tr = tabelle.insertRow();
      tr.insertCell().textContent = k;
      tr.insertCell().textContent = v;
    }
    inhalt.appendChild(tabelle);
  }

  _liste(inhalt) {
    const h = this.hass;
    const pfad = "/config/integrations/integration/rollladensteuerung";
    inhalt.innerHTML = `<h3>${tx(h, "rolllaeden")}</h3><ul>${this._k.rolllaeden.map((r) => `<li>${esc(r.name)} <small>(${esc(r.cover)})</small></li>`).join("")}</ul>
      <h3>${tx(h, "helligkeit")}</h3><ul>${this._k.helligkeit.map((s) => `<li>${esc(s.name)} <small>(${esc(s.entity)})</small></li>`).join("")}</ul>
      <a class="link">${tx(h, "hinzufuegen")} →</a>`;
    inhalt.querySelector(".link").addEventListener("click", () => { this.remove(); navigieren(pfad); });
  }

  async _speichern() {
    const root = this.shadowRoot;
    const knopf = root.querySelector(".speichern");
    const meldung = root.querySelector(".meldung");
    knopf.disabled = true;
    meldung.textContent = "";
    try {
      if (this._art === "rollladen") {
        await this.hass.callWS({ type: "rollladensteuerung/rollladen/speichern", sid: this._rl.sid, daten: this._daten });
      } else {
        await this.hass.callWS({ type: "rollladensteuerung/global/speichern", daten: this._daten });
      }
      setTimeout(() => konfigNeu(this.hass).catch(() => {}), 1500);
      setTimeout(() => konfigNeu(this.hass).catch(() => {}), 5000);
      this.remove();
    } catch (e) {
      meldung.textContent = `${tx(this.hass, "fehler")}: ${e?.message || e}`;
      knopf.disabled = false;
    }
  }
}


/* ---------------------------------------------------------------- Sonnenstand (Text unter dem Helligkeitsverlauf) */
// Zeigt die Werte, mit denen auch die Steuerung rechnet (Attribute von sun.sun). Home Assistant aktualisiert sie
// tagsüber alle 2–4 Minuten, nachts alle 20 Minuten; die Karte zeichnet nur neu, wenn sich etwas geändert hat.
class SonneKarte extends HTMLElement {
  setConfig(config) { this._config = config || {}; }
  getCardSize() { return 1; }
  getGridOptions() { return { columns: "full", rows: "auto" }; }
  set hass(hass) {
    this._hass = hass;
    const st = hass.states[this._config.entity || "sun.sun"];
    const a = st?.attributes || {};
    const schluessel = `${a.azimuth}|${a.elevation}|${a.rising}|${hass.language}`;
    if (schluessel === this._zuletzt) return;
    this._zuletzt = schluessel;
    if (!this.shadowRoot) {
      this.attachShadow({ mode: "open" }).innerHTML = `<style>
        ha-card { padding: 10px 16px; display: flex; align-items: center; gap: 10px; color: var(--primary-text-color); }
        ha-icon { color: var(--state-sun-above_horizon-color, var(--amber-color, #ffc107)); flex: none; }
        .text { font-size: 14px; line-height: 1.4; }
        small { color: var(--secondary-text-color); }
      </style><ha-card><ha-icon></ha-icon><div class="text"></div></ha-card>`;
    }
    const icon = this.shadowRoot.querySelector("ha-icon");
    const text = this.shadowRoot.querySelector(".text");
    if (a.azimuth == null || a.elevation == null) {
      icon.setAttribute("icon", "mdi:weather-sunny-off");
      text.textContent = `${tx(hass, "sonne_titel")}: –`;
      return;
    }
    const zahl = (v) => Number(v).toLocaleString(hass.language || undefined, { maximumFractionDigits: 1 });
    const richtungen = tx(hass, "richtungen").split(",");
    const richtung = richtungen[Math.round(((Number(a.azimuth) % 360) + 360) % 360 / 22.5) % 16];
    const oben = Number(a.elevation) > 0;
    icon.setAttribute("icon", oben ? "mdi:weather-sunny" : "mdi:weather-night");
    const trend = a.rising == null ? "" : `, ${tx(hass, a.rising ? "sonne_steigt" : "sonne_sinkt")}`;
    const stand = st.last_updated ? new Date(st.last_updated).toLocaleTimeString(hass.language || undefined,
      { hour: "2-digit", minute: "2-digit" }) : "";
    text.innerHTML = `<b>${esc(tx(hass, "sonne_titel"))}:</b> ${esc(richtung)} (${zahl(a.azimuth)}°) · `
      + `${esc(tx(hass, "sonne_hoehe"))} ${zahl(a.elevation)}°${esc(trend)}`
      + `${oben ? "" : ` <small>(${esc(tx(hass, "sonne_unter"))})</small>`}`
      + `${stand ? ` <small>· ${esc(tx(hass, "sonne_stand"))} ${esc(stand)}</small>` : ""}`;
  }
}

/* ---------------------------------------------------------------- Benachrichtigungen & Protokoll */
const PUSH_SYMBOL = { push_oeffnen: "mdi:weather-sunset-up", push_schliessen: "mdi:weather-sunset-down",
  push_warnungen: "mdi:alert-outline", push_lueften: "mdi:window-open-variant", push_abschatten: "mdi:sun-angle",
  push_funktionen: "mdi:toggle-switch-outline", push_manuell: "mdi:hand-back-right-outline",
  push_zusammenfassung: "mdi:text-box-outline" };
const ARTEN = {
  de: { oeffnen: "Öffnen", schliessen: "Schließen", lueften: "Lüften", abschatten: "Abschatten", warnung: "Warnung",
        manuell: "Von Hand", fahrt: "Fahrt", info: "Info", funktion: "Funktion" },
  en: { oeffnen: "Open", schliessen: "Close", lueften: "Ventilate", abschatten: "Shade", warnung: "Warning",
        manuell: "Manual", fahrt: "Move", info: "Info", funktion: "Function" },
};
const artText = (hass, art) => ((ARTEN[(hass?.language || "en").split("-")[0]] || ARTEN.en)[art] || art);

async function protokollLaden(hass, tage = 90, von, bis) {
  const msg = { type: "rollladensteuerung/protokoll", tage };
  if (von) msg.von = von.toISOString();
  if (bis) msg.bis = bis.toISOString();
  return (await hass.callWS(msg)).eintraege || [];
}

const zweistellig = (n) => String(n).padStart(2, "0");
const isoTag = (d) => `${d.getFullYear()}-${zweistellig(d.getMonth() + 1)}-${zweistellig(d.getDate())}`;

async function protokollSpeichern(hass, eintraege, von, bis) {
  // Semikolon + BOM: öffnet sich in Excel/Numbers direkt richtig; Datum und Uhrzeit in eigenen Spalten
  const kopf = [tx(hass, "datum"), tx(hass, "uhrzeit"), tx(hass, "rollladen"), tx(hass, "art"), tx(hass, "meldung")].join(";");
  const zeilen = eintraege.map((e) => {
    const d = new Date(e.zeit);
    const datum = isNaN(d) ? e.zeit : `${zweistellig(d.getDate())}.${zweistellig(d.getMonth() + 1)}.${d.getFullYear()}`;
    const uhr = isNaN(d) ? "" : `${zweistellig(d.getHours())}:${zweistellig(d.getMinutes())}:${zweistellig(d.getSeconds())}`;
    return [datum, uhr, e.rollladen, artText(hass, e.art), e.text]
      .map((v) => `"${String(v ?? "").replace(/"/g, '""')}"`).join(";");
  });
  const inhalt = "\ufeff" + [kopf, ...zeilen].join("\r\n");
  const bereich = von && bis ? (isoTag(von) === isoTag(bis) ? isoTag(von) : `${isoTag(von)}_bis_${isoTag(bis)}`) : isoTag(new Date());
  const name = `rollladensteuerung-protokoll-${bereich}.csv`;
  const datei = new File([inhalt], name, { type: "text/csv" });
  // Auf Handy/Tablet (App) über „Teilen“ speichern, sonst als Download
  if (navigator.canShare && navigator.canShare({ files: [datei] })) {
    try { await navigator.share({ files: [datei], title: name }); return; } catch (e) { if (e?.name === "AbortError") return; }
  }
  const url = URL.createObjectURL(datei);
  const a = document.createElement("a");
  a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}

class MeldungenKarte extends HTMLElement {
  setConfig(config) { this._config = config || {}; }
  connectedCallback() {
    this._neu = (ev) => { this._konfig = ev.detail; if (this.shadowRoot) { this._schalterBauen(); this._zeichnen(); } };
    window.addEventListener("rollladensteuerung-konfig", this._neu);
  }
  disconnectedCallback() { window.removeEventListener("rollladensteuerung-konfig", this._neu); }
  static getStubConfig() { return {}; }
  getCardSize() { return 4; }
  getGridOptions() { return { columns: 12, min_columns: 6, rows: "auto" }; }

  set hass(hass) {
    this._hass = hass;
    if (!this._aufgebaut) this._aufbauen();
    if (!this._konfig && !this._laedt) {
      this._laedt = true;
      ladeKonfig(hass).then((k) => { this._konfig = k; this._schalterBauen(); this._zeichnen(); }).catch(() => {});
    }
    this._zeichnen();
  }

  _aufbauen() {
    this._aufgebaut = true;
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `
      <style>${GEMEINSAM_CSS}
        .schalter { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
        .schalter button span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
        .schalter button ha-icon { flex: none; }
        .schalter button { display: flex; align-items: center; gap: 8px; padding: 0 10px; height: 44px; border: none; min-width: 0;
          border-radius: 12px; cursor: pointer; text-align: left; font: inherit; font-size: 13px;
          background: rgba(var(--rgb-primary-text-color, 0,0,0), 0.05); color: var(--primary-text-color); }
        .schalter button.an { background: rgba(var(--rgb-primary-color, 3,169,244), 0.18); }
        .schalter button.an ha-icon { color: var(--primary-color); }
        .hinweis { font-size: 13px; color: var(--warning-color, #e65100); }
        .alle button { min-width: 150px; }
      </style>
      <ha-card>
        <div class="kopf">
          <div class="symbol" style="--rgb-farbe: var(--rgb-primary-color, 3,169,244)"><ha-icon icon="mdi:bell-outline"></ha-icon></div>
          <div class="text"><div class="name">${tx(this._hass, "meldungen")}</div>
            <div class="zustand dienst"></div></div>
        </div>
        <div class="hinweis" hidden>${tx(this._hass, "kein_push")}</div>
        <div class="schalter"></div>
        <div class="tasten alle">
          <button class="anzeigen"><ha-icon icon="mdi:text-box-search-outline"></ha-icon>&nbsp;${tx(this._hass, "protokoll_anzeigen")}</button>
          <button class="speichern"><ha-icon icon="mdi:download"></ha-icon>&nbsp;${tx(this._hass, "protokoll_speichern")}</button>
        </div>
      </ha-card>`;
    root.querySelector(".anzeigen").addEventListener("click", () => {
      const d = document.createElement("rollladensteuerung-protokoll");
      d.hass = this._hass;
      document.body.appendChild(d);
    });
    root.querySelector(".speichern").addEventListener("click", async () => {
      try { await protokollSpeichern(this._hass, await protokollLaden(this._hass)); } catch (e) { alert(e?.message || e); }
    });
  }

  _schalterBauen() {
    const feld = this.shadowRoot.querySelector(".schalter");
    feld.innerHTML = "";
    for (const [name, eid] of Object.entries(this._konfig.push || {})) {
      if (!eid) continue;
      const b = document.createElement("button");
      b.dataset.entity = eid;
      b.innerHTML = `<ha-icon icon="${PUSH_SYMBOL[name] || "mdi:bell-outline"}"></ha-icon><span></span>`;
      b.addEventListener("click", () => this._hass.callService("switch", "toggle", { entity_id: eid }));
      feld.appendChild(b);
    }
  }

  _zeichnen() {
    if (!this._konfig || !this.shadowRoot) return;
    const r = this.shadowRoot;
    r.querySelectorAll(".schalter button").forEach((b) => {
      const st = this._hass.states[b.dataset.entity];
      b.classList.toggle("an", st?.state === "on");
      b.querySelector("span").textContent = (st?.attributes?.friendly_name || b.dataset.entity)
        .replace(/^Rollladensteuerung\s*/i, "").replace(/^Push\s*/i, "");
    });
    const dienst = this._konfig.push_dienst;
    r.querySelector(".dienst").textContent = dienst ? `${tx(this._hass, "push_ueber")} ${dienst}` : "";
    r.querySelector(".hinweis").hidden = !!dienst;
  }
}

class ProtokollDialog extends HTMLElement {
  connectedCallback() {
    const h = this.hass;
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `
      <style>
        .hinter { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 1000; display: flex;
          align-items: center; justify-content: center; padding: 16px; box-sizing: border-box; }
        .fenster { background: var(--ha-card-background, var(--card-background-color, #fff)); color: var(--primary-text-color);
          border-radius: 24px; width: 100%; max-width: 900px; max-height: 92vh; display: flex; flex-direction: column;
          box-shadow: 0 8px 32px rgba(0,0,0,0.3); overflow: hidden; }
        .kopf { display: flex; align-items: center; padding: 16px 16px 8px 24px; gap: 8px; }
        .kopf h2 { flex: 1; margin: 0; font-size: 22px; font-weight: 400; }
        .kopf button, .fuss button { border: none; background: none; color: var(--primary-text-color); cursor: pointer; padding: 8px; border-radius: 20px; font: inherit; }
        .filter { display: flex; gap: 8px; padding: 0 24px 8px; flex-wrap: wrap; }
        .filter select, .filter input { font: inherit; font-size: 14px; padding: 8px; border-radius: 8px; border: 1px solid var(--divider-color);
          background: var(--secondary-background-color, transparent); color: var(--primary-text-color); }
        .filter input { flex: 1; min-width: 140px; }
        .inhalt { overflow: auto; flex: 1; padding: 0 24px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; position: sticky; top: 0; background: var(--ha-card-background, var(--card-background-color, #fff));
          padding: 6px 8px 6px 0; border-bottom: 1px solid var(--divider-color); color: var(--secondary-text-color); font-weight: 500; }
        td { padding: 5px 8px 5px 0; border-bottom: 1px solid var(--divider-color); vertical-align: top; }
        td.zeit { white-space: nowrap; color: var(--secondary-text-color); }
        tr.warnung td { color: var(--error-color, #c62828); }
        .fuss { display: flex; justify-content: space-between; align-items: center; padding: 12px 24px 20px; gap: 8px; font-size: 13px; color: var(--secondary-text-color); }
        .fuss .haupt { background: var(--primary-color); color: var(--text-primary-color, #fff); padding: 10px 20px; font-weight: 500; }
      </style>
      <div class="hinter"><div class="fenster" role="dialog" aria-modal="true">
        <div class="kopf"><h2>${tx(h, "protokoll")}</h2><button class="zu"><ha-icon icon="mdi:close"></ha-icon></button></div>
        <div class="filter"><select class="rl"><option value="">${tx(h, "alle_rolllaeden")}</option></select>
          <select class="art"><option value="">${tx(h, "alle_arten")}</option></select>
          <input class="suche" placeholder="${tx(h, "suchen")}"></div>
        <div class="inhalt">${tx(h, "laedt")}</div>
        <div class="fuss"><span class="anzahl"></span><button class="haupt">${tx(h, "protokoll_speichern")}</button></div>
      </div></div>`;
    const weg = () => this.remove();
    root.querySelector(".zu").addEventListener("click", weg);
    root.querySelector(".hinter").addEventListener("click", (ev) => { if (ev.target === ev.currentTarget) weg(); });
    this._taste = (ev) => { if (ev.key === "Escape") weg(); };
    window.addEventListener("keydown", this._taste);
    ["rl", "art"].forEach((k) => root.querySelector(`.${k}`).addEventListener("change", () => this._zeigen()));
    root.querySelector(".suche").addEventListener("input", () => this._zeigen());
    root.querySelector(".haupt").addEventListener("click", () => protokollSpeichern(h, this._gefiltert()));
    protokollLaden(h).then((e) => {
      this._eintraege = e;
      const fuellen = (sel, werte, text) => werte.forEach((w) => {
        const o = document.createElement("option"); o.value = w; o.textContent = text(w); sel.appendChild(o);
      });
      fuellen(root.querySelector(".rl"), [...new Set(e.map((x) => x.rollladen))].sort(), (w) => w);
      fuellen(root.querySelector(".art"), [...new Set(e.map((x) => x.art))].sort(), (w) => artText(h, w));
      this._zeigen();
    }).catch((err) => { root.querySelector(".inhalt").textContent = `${tx(h, "fehler")}: ${err?.message || err}`; });
  }

  disconnectedCallback() { window.removeEventListener("keydown", this._taste); }

  _gefiltert() {
    const r = this.shadowRoot;
    const rl = r.querySelector(".rl").value, art = r.querySelector(".art").value;
    const suche = r.querySelector(".suche").value.toLowerCase();
    return (this._eintraege || []).filter((e) => (!rl || e.rollladen === rl) && (!art || e.art === art)
      && (!suche || `${e.rollladen} ${e.text}`.toLowerCase().includes(suche)));
  }

  _zeigen() {
    const h = this.hass;
    const liste = this._gefiltert();
    const sprache = h?.locale?.language || h?.language || "de";
    const tabelle = document.createElement("table");
    tabelle.innerHTML = `<thead><tr><th>${tx(h, "zeit")}</th><th>${tx(h, "rollladen")}</th><th>${tx(h, "art")}</th><th>${tx(h, "meldung")}</th></tr></thead>`;
    const body = document.createElement("tbody");
    for (const e of liste.slice(0, 2000)) {
      const tr = body.insertRow();
      if (e.art === "warnung") tr.className = "warnung";
      const d = new Date(e.zeit);
      const z = tr.insertCell(); z.className = "zeit";
      z.textContent = isNaN(d) ? e.zeit : d.toLocaleString(sprache, { weekday: "short", day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
      tr.insertCell().textContent = e.rollladen;
      tr.insertCell().textContent = artText(h, e.art);
      tr.insertCell().textContent = e.text;
    }
    tabelle.appendChild(body);
    const inhalt = this.shadowRoot.querySelector(".inhalt");
    inhalt.innerHTML = "";
    inhalt.appendChild(tabelle);
    this.shadowRoot.querySelector(".anzahl").textContent = `${liste.length} ${tx(h, "eintraege")}`;
  }
}

/* ---------------------------------------------------------------- Protokoll-Karte (eigenständig nutzbar) */
const ZEITRAEUME = ["heute", "gestern", "7t", "30t", "alles"];
const ALS_EINGABE = (d) => `${isoTag(d)}T${zweistellig(d.getHours())}:${zweistellig(d.getMinutes())}`;

function zeitraumVon(s) {
  const jetzt = new Date();
  const mitternacht = new Date(jetzt.getFullYear(), jetzt.getMonth(), jetzt.getDate());
  if (s === "gestern") return [new Date(mitternacht - 86400e3), new Date(mitternacht - 60e3)];
  if (s === "7t") return [new Date(jetzt - 7 * 86400e3), jetzt];
  if (s === "30t") return [new Date(jetzt - 30 * 86400e3), jetzt];
  if (s === "alles") return [new Date(jetzt - 90 * 86400e3), jetzt];
  return [mitternacht, jetzt];
}

class ProtokollKarte extends HTMLElement {
  static getConfigElement() { return document.createElement("rollladensteuerung-protokoll-editor"); }
  static getStubConfig() { return { zeitraum: "heute" }; }
  setConfig(config) {
    this._config = { zeitraum: "heute", filter: true, ...(config || {}) };
    this._rl = new Set(this._config.rolllaeden || []);
    this._arten = new Set(this._config.arten || []);
    if (this.shadowRoot) { this._schnell(this._config.zeitraum, false); this._filterBauen(); }
  }
  getCardSize() { return this._offen ? 10 : 5; }
  getGridOptions() { return { columns: 12, min_columns: 6, rows: "auto" }; }

  set hass(hass) {
    const erstes = !this._hass;
    this._hass = hass;
    if (!this.shadowRoot) this._aufbauen();
    if (erstes) {
      ladeKonfig(hass).then((k) => { this._namen = ["Zentrale", ...k.rolllaeden.map((r) => r.name).sort()]; this._filterBauen(); })
        .catch(() => {});
      if (this._config.anzeigen) this._anzeigen(true);
    }
  }

  _aufbauen() {
    const h = this._hass;
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `
      <style>${GEMEINSAM_CSS}
        .chips { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
        .chips .etikett { font-size: 12px; color: var(--secondary-text-color); margin-right: 2px; min-width: 70px; }
        .chip { font: inherit; font-size: 13px; padding: 5px 12px; border-radius: 16px; cursor: pointer;
          border: 1px solid var(--divider-color); background: none; color: var(--primary-text-color); }
        .chip.an { background: rgba(var(--rgb-primary-color, 3,169,244), 0.18); border-color: var(--primary-color); color: var(--primary-color); }
        .leiste { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 13px; color: var(--secondary-text-color); }
        .leiste label { display: flex; align-items: center; gap: 6px; }
        .leiste input { font: inherit; font-size: 13px; padding: 5px 8px; border-radius: 8px; border: 1px solid var(--divider-color);
          background: var(--card-background-color, transparent); color: var(--primary-text-color); color-scheme: light dark; }
        .leiste input.suche { flex: 1; min-width: 120px; }
        .tasten button.haupt { background: var(--primary-color); color: var(--text-primary-color, #fff); }
        /* breite Tabellen dürfen die Karte nicht aufweiten (Flex-Kinder haben sonst min-width: auto) */
        ha-card > * { min-width: 0; }
        .tabelle { max-height: 460px; overflow: auto; border-top: 1px solid var(--divider-color); }
        td.text { overflow-wrap: anywhere; }
        @media (max-width: 500px) { .leiste label { flex: 1 1 100%; } .leiste label input { flex: 1; min-width: 0; } }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; position: sticky; top: 0; background: var(--ha-card-background, var(--card-background-color, #fff));
          padding: 6px 8px 6px 0; border-bottom: 1px solid var(--divider-color); color: var(--secondary-text-color); font-weight: 500; }
        td { padding: 5px 8px 5px 0; border-bottom: 1px solid var(--divider-color); vertical-align: top; }
        td.zeit { white-space: nowrap; color: var(--secondary-text-color); }
        tr.warnung td { color: var(--error-color, #c62828); }
        .info { font-size: 13px; color: var(--secondary-text-color); }
        [hidden] { display: none !important; }
      </style>
      <ha-card>
        <div class="kopf">
          <div class="symbol" style="--rgb-farbe: var(--rgb-primary-color, 3,169,244)"><ha-icon icon="mdi:text-box-search-outline"></ha-icon></div>
          <div class="text"><div class="name"></div><div class="zustand"></div></div>
        </div>
        <div class="chips zeitraum">${ZEITRAEUME.map((z) => `<button class="chip" data-z="${z}">${tx(h, `p_${z}`)}</button>`).join("")}</div>
        <div class="leiste">
          <label>${tx(h, "p_von")} <input type="datetime-local" class="von"></label>
          <label>${tx(h, "p_bis")} <input type="datetime-local" class="bis"></label>
        </div>
        <div class="filter">
          <div class="chips rl"></div>
          <div class="chips art" style="margin-top:6px"></div>
          <div class="leiste" style="margin-top:6px"><input class="suche" placeholder="${tx(h, "suchen")}"></div>
        </div>
        <div class="tasten">
          <button class="anzeigen"><ha-icon icon="mdi:table-eye"></ha-icon>&nbsp;<span>${tx(h, "p_anzeigen")}</span></button>
          <button class="haupt laden"><ha-icon icon="mdi:download"></ha-icon>&nbsp;${tx(h, "p_herunterladen")}</button>
        </div>
        <div class="info"></div>
        <div class="tabelle" hidden></div>
      </ha-card>`;
    const $ = (s) => root.querySelector(s);
    root.querySelectorAll(".zeitraum .chip").forEach((b) => b.addEventListener("click", () => this._schnell(b.dataset.z, true)));
    [".von", ".bis"].forEach((s) => $(s).addEventListener("change", () => {
      this._wahl = ""; this._chipsZeitraum(); this._eintraege = null; if (this._offen) this._anzeigen(true);
    }));
    $(".suche").addEventListener("input", () => this._zeigen());
    $(".anzeigen").addEventListener("click", () => this._anzeigen(!this._offen));
    $(".laden").addEventListener("click", () => this._herunterladen());
    this._schnell(this._config.zeitraum, false);
    this._filterBauen();
  }

  _schnell(z, neuLaden) {
    const [von, bis] = zeitraumVon(z);
    this._wahl = z;
    this.shadowRoot.querySelector(".von").value = ALS_EINGABE(von);
    this.shadowRoot.querySelector(".bis").value = ALS_EINGABE(bis);
    this._chipsZeitraum();
    this._eintraege = null;
    if (neuLaden && this._offen) this._anzeigen(true);
  }
  _chipsZeitraum() {
    this.shadowRoot.querySelectorAll(".zeitraum .chip").forEach((b) => b.classList.toggle("an", b.dataset.z === this._wahl));
  }

  _zeitraum() {
    const r = this.shadowRoot;
    // „bis jetzt“-Zeiträume beim Laden aktualisieren, damit neue Einträge dazukommen
    if (this._wahl && this._wahl !== "gestern") return zeitraumVon(this._wahl);
    const von = new Date(r.querySelector(".von").value), bis = new Date(r.querySelector(".bis").value);
    if (isNaN(von) || isNaN(bis)) return null;
    bis.setSeconds(59, 999);
    return [von, bis];
  }

  _filterBauen() {
    const r = this.shadowRoot;
    if (!r || !this._hass) return;
    const h = this._hass;
    r.querySelector(".filter").hidden = this._config.filter === false;
    const bauen = (ziel, etikett, werte, menge, text) => {
      ziel.innerHTML = `<span class="etikett">${esc(etikett)}</span>`;
      const alle = document.createElement("button");
      alle.className = "chip" + (menge.size ? "" : " an");
      alle.textContent = tx(h, "p_alle");
      alle.addEventListener("click", () => { menge.clear(); this._filterBauen(); this._zeigen(); });
      ziel.appendChild(alle);
      for (const w of werte) {
        const b = document.createElement("button");
        b.className = "chip" + (menge.has(w) ? " an" : "");
        b.textContent = text(w);
        b.addEventListener("click", () => { menge.has(w) ? menge.delete(w) : menge.add(w); this._filterBauen(); this._zeigen(); });
        ziel.appendChild(b);
      }
    };
    const namen = [...new Set([...(this._namen || []), ...this._rl])];
    bauen(r.querySelector(".rl"), tx(h, "p_rolllaeden"), namen, this._rl, (w) => w);
    bauen(r.querySelector(".art"), tx(h, "p_arten"), Object.keys(ARTEN.de), this._arten, (w) => artText(h, w));
    r.querySelector(".name").textContent = this._config.titel || tx(h, "protokoll");
  }

  async _holen() {
    const z = this._zeitraum();
    const info = this.shadowRoot.querySelector(".info");
    if (!z) { info.textContent = tx(this._hass, "p_zeitraum_fehlt"); return null; }
    if (!this._eintraege || this._wahl) {
      info.textContent = tx(this._hass, "laedt");
      this._eintraege = await protokollLaden(this._hass, 90, z[0], z[1]);
      info.textContent = "";
    }
    return z;
  }

  _gefiltert() {
    const suche = this.shadowRoot.querySelector(".suche").value.toLowerCase();
    return (this._eintraege || []).filter((e) => (!this._rl.size || this._rl.has(e.rollladen))
      && (!this._arten.size || this._arten.has(e.art))
      && (!suche || `${e.rollladen} ${e.text}`.toLowerCase().includes(suche)));
  }

  async _anzeigen(offen) {
    this._offen = offen;
    const r = this.shadowRoot;
    r.querySelector(".anzeigen span").textContent = tx(this._hass, offen ? "p_ausblenden" : "p_anzeigen");
    r.querySelector(".tabelle").hidden = !offen;
    if (!offen) { r.querySelector(".info").textContent = ""; return; }
    try { await this._holen(); this._zeigen(); }
    catch (e) { r.querySelector(".info").textContent = `${tx(this._hass, "fehler")}: ${e?.message || e}`; }
  }

  async _herunterladen() {
    try {
      const z = await this._holen();
      if (!z) return;
      await protokollSpeichern(this._hass, this._gefiltert(), z[0], z[1]);
      if (this._offen) this._zeigen();
    } catch (e) { this.shadowRoot.querySelector(".info").textContent = `${tx(this._hass, "fehler")}: ${e?.message || e}`; }
  }

  _zeigen() {
    const r = this.shadowRoot, h = this._hass;
    const liste = this._gefiltert();
    r.querySelector(".zustand").textContent = this._eintraege ? `${liste.length} ${tx(h, "eintraege")}` : "";
    if (!this._offen || !this._eintraege) return;
    const ziel = r.querySelector(".tabelle");
    if (!liste.length) { ziel.innerHTML = `<div class="info" style="padding:12px 0">${esc(tx(h, "p_leer"))}</div>`; return; }
    const sprache = h?.locale?.language || h?.language || "de";
    const tabelle = document.createElement("table");
    tabelle.innerHTML = `<thead><tr><th>${tx(h, "zeit")}</th><th>${tx(h, "rollladen")}</th><th>${tx(h, "art")}</th><th>${tx(h, "meldung")}</th></tr></thead>`;
    const body = document.createElement("tbody");
    for (const e of liste.slice(0, 2000)) {
      const tr = body.insertRow();
      if (e.art === "warnung") tr.className = "warnung";
      const d = new Date(e.zeit);
      const zelle = tr.insertCell(); zelle.className = "zeit";
      zelle.textContent = isNaN(d) ? e.zeit : d.toLocaleString(sprache, { weekday: "short", day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
      tr.insertCell().textContent = e.rollladen;
      tr.insertCell().textContent = artText(h, e.art);
      const t = tr.insertCell(); t.className = "text"; t.textContent = e.text;
    }
    tabelle.appendChild(body);
    ziel.innerHTML = "";
    ziel.appendChild(tabelle);
    if (liste.length > 2000) {
      const mehr = document.createElement("div"); mehr.className = "info"; mehr.style.padding = "8px 0";
      mehr.textContent = tx(h, "p_mehr"); ziel.appendChild(mehr);
    }
  }
}

/* ---------------------------------------------------------------- Vorlagen (strategies) */
function gruppieren(hass, rolllaeden) {
  const gruppen = new Map();
  for (const r of rolllaeden) {
    const ent = hass.entities?.[r.cover];
    const geraet = ent?.device_id ? hass.devices?.[ent.device_id] : undefined;
    const bereichId = ent?.area_id || geraet?.area_id;
    const bereich = bereichId ? hass.areas?.[bereichId] : undefined;
    const stock = bereich?.floor_id ? hass.floors?.[bereich.floor_id] : undefined;
    const key = stock?.floor_id || "_";
    if (!gruppen.has(key)) {
      gruppen.set(key, { name: stock?.name || tx(hass, "rolllaeden"), icon: stock?.icon || "mdi:window-shutter",
        level: stock?.level ?? 99, liste: [] });
    }
    gruppen.get(key).liste.push(r);
  }
  return [...gruppen.values()].sort((a, b) => (a.level < 0) - (b.level < 0) || a.level - b.level);
}

function steuerungKarten(k, hass, config) {
  const karten = [
    { type: "heading", heading: config.titel || tx(hass, "automatik"), icon: "mdi:window-shutter-auto" },
    { type: "custom:rollladensteuerung-zentrale-card", grid_options: { columns: "full" } },
  ];
  if (k.helligkeit.length && config.verlauf !== false) {
    karten.push({ type: "history-graph", hours_to_show: 24, grid_options: { columns: "full" },
      entities: k.helligkeit.map((s) => ({ entity: s.entity, name: s.name })) });
    karten.push({ type: "custom:rollladensteuerung-sonne-card", entity: k.global?.daten?.sonne || "sun.sun",
      grid_options: { columns: "full", rows: "auto" } });
  }
  return karten;
}
function meldungenKarten(hass, config) {
  return [
    { type: "heading", heading: config.titel || tx(hass, "meldungen"), icon: "mdi:bell-outline" },
    { type: "custom:rollladensteuerung-meldungen-card", grid_options: { columns: "full" } },
  ];
}
function protokollKarten(hass, config) {
  const karte = { type: "custom:rollladensteuerung-protokoll-card", grid_options: { columns: "full" } };
  for (const k of ["zeitraum", "rolllaeden", "arten", "anzeigen", "filter"]) if (config[k] !== undefined) karte[k] = config[k];
  return [{ type: "heading", heading: config.titel || tx(hass, "protokoll"), icon: "mdi:text-box-search-outline" }, karte];
}
function rollladenKarten(g, titel) {
  const liste = [...g.liste].sort((a, b) => a.name.localeCompare(b.name));
  return [
    { type: "heading", heading: titel || g.name, icon: g.icon },
    ...liste.map((r) => ({ type: "custom:rollladensteuerung-card", entity: r.cover })),
  ];
}

async function ansichtBauen(config, hass) {
  let k;
  try { k = await ladeKonfig(hass, true); } catch (e) {
    return { title: config.title || "Rollläden", cards: [{ type: "markdown", content: tx(hass, "keine_konfig") }] };
  }
  // Automatik und Benachrichtigungen in EINER Spalte; standardmäßig hinter den Stockwerken
  // (Option steuerung: vorne stellt sie an den Anfang)
  const steuerung = { type: "grid", cards: [...steuerungKarten(k, hass, { verlauf: config.verlauf }), ...meldungenKarten(hass, {})] };
  const sections = gruppieren(hass, k.rolllaeden).map((g) => ({ type: "grid", cards: rollladenKarten(g) }));
  if (config.steuerung === "vorne") sections.unshift(steuerung); else sections.push(steuerung);
  const spalten = config.max_columns || 4;
  // Protokoll als eigene Gruppe unter allen anderen (volle Breite); protokoll: false blendet sie aus
  if (config.protokoll !== false) sections.push({ type: "grid", column_span: spalten, cards: protokollKarten(hass, {}) });
  return { title: config.title || tx(hass, "rolllaeden"), path: config.path, icon: config.icon,
    type: "sections", max_columns: spalten, sections };
}

/* ---------------------------------------------------------------- Abschnitts-Vorlagen (section strategies) */
const hinweis = (text) => ({ type: "grid", cards: [{ type: "markdown", content: text }] });

class AbschnittRolllaeden extends HTMLElement {
  static getConfigElement() { return document.createElement("rollladensteuerung-abschnitt-editor"); }
  static async getStubConfig(hass) {
    try {
      const k = await frischeKonfig(hass);
      const g = gruppieren(hass, k.rolllaeden)[0];
      const stock = g?.liste.length ? stockwerkVon(hass, g.liste[0]) : undefined;
      return { type: "custom:rollladensteuerung", stockwerk: stock || "alle" };
    } catch (e) { return { type: "custom:rollladensteuerung", stockwerk: "alle" }; }
  }
  static async generate(config, hass) {
    let k;
    try { k = await frischeKonfig(hass); } catch (e) { return hinweis(tx(hass, "keine_konfig")); }
    const stock = config.stockwerk || "alle";
    if (stock === "alle") {
      return { type: "grid", cards: rollladenKarten({ name: tx(hass, "alle_stockwerke"), icon: "mdi:window-shutter",
        liste: k.rolllaeden }, config.titel) };
    }
    if (stock !== "ohne" && !hass.floors?.[stock]) return hinweis(tx(hass, "stock_fehlt"));
    const liste = k.rolllaeden.filter((r) => (stockwerkVon(hass, r) || "ohne") === stock);
    const f = hass.floors?.[stock];
    const g = { name: f?.name || tx(hass, "ohne_stockwerk"), icon: f?.icon || "mdi:window-shutter", liste };
    const karten = rollladenKarten(g, config.titel);
    if (!liste.length) karten.push({ type: "markdown", content: tx(hass, "keine_rolllaeden") });
    return { type: "grid", cards: karten };
  }
}
class AbschnittSteuerung extends HTMLElement {
  static getConfigElement() { return document.createElement("rollladensteuerung-steuerung-editor"); }
  static getStubConfig() { return { type: "custom:rollladensteuerung-steuerung" }; }
  static async generate(config, hass) {
    let k;
    try { k = await frischeKonfig(hass); } catch (e) { return hinweis(tx(hass, "keine_konfig")); }
    return { type: "grid", cards: steuerungKarten(k, hass, config) };
  }
}
class AbschnittMeldungen extends HTMLElement {
  static registryDependencies = [];
  static getConfigElement() { return document.createElement("rollladensteuerung-meldungen-editor"); }
  static getStubConfig() { return { type: "custom:rollladensteuerung-meldungen" }; }
  static async generate(config, hass) { return { type: "grid", cards: meldungenKarten(hass, config) }; }
}

class AbschnittProtokoll extends HTMLElement {
  static getConfigElement() { return document.createElement("rollladensteuerung-protokoll-editor"); }
  static getStubConfig() { return { type: "custom:rollladensteuerung-protokoll" }; }
  // volle Breite (wird auf die Spaltenzahl der Ansicht begrenzt) → steht als eigene Gruppe unter den anderen
  static async generate(config, hass) { return { type: "grid", column_span: 4, cards: protokollKarten(hass, config) }; }
}

function stockwerkVon(hass, r) {
  const ent = hass.entities?.[r.cover];
  const geraet = ent?.device_id ? hass.devices?.[ent.device_id] : undefined;
  const bereichId = ent?.area_id || geraet?.area_id;
  return bereichId ? hass.areas?.[bereichId]?.floor_id || undefined : undefined;
}

// Einstellungen der Abschnitte (visueller Editor)
class AbschnittEditor extends HTMLElement {
  setConfig(config) { this._config = config; this._zeichnen(); }
  set hass(hass) { this._hass = hass; this._zeichnen(); }
  schema() { return [{ name: "titel", selector: { text: {} } }]; }
  async _zeichnen() {
    if (!this._hass || !this._config) return;
    if (!this._form) {
      this._form = true;
      await haFormBereit();
      const form = document.createElement("ha-form");
      form.computeLabel = (f) => tx(this._hass, `f_${f.name}`);
      form.addEventListener("value-changed", (ev) => {
        const neu = { ...this._config, ...ev.detail.value };
        for (const [s, w] of Object.entries(neu)) if (w === "" || w === undefined || w === null) delete neu[s];
        this._config = neu;
        this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: neu }, bubbles: true, composed: true }));
      });
      this.appendChild(form);
      this._form = form;
    }
    if (this._form === true) return;
    this._form.hass = this._hass;
    this._form.schema = this.schema();
    this._form.data = this._daten();
  }
  _daten() { return this._config; }
}
class RolllaedenEditor extends AbschnittEditor {
  schema() {
    const h = this._hass;
    const stockwerke = Object.values(h.floors || {}).sort((a, b) => (a.level ?? 99) - (b.level ?? 99))
      .map((f) => ({ value: f.floor_id, label: f.name }));
    return [
      { name: "stockwerk", selector: { select: { mode: "dropdown", options: [
        { value: "alle", label: tx(h, "alle_stockwerke") }, ...stockwerke, { value: "ohne", label: tx(h, "ohne_stockwerk") }] } } },
      ...super.schema(),
    ];
  }
  _daten() { return { stockwerk: "alle", ...this._config }; }
}
class SteuerungEditor extends AbschnittEditor {
  schema() { return [...super.schema(), { name: "verlauf", selector: { boolean: {} } }]; }
  _daten() { return { verlauf: true, ...this._config }; }
}

class ProtokollEditor extends AbschnittEditor {
  async _zeichnen() {
    if (this._hass && !this._namen) {
      this._namen = [];
      try { this._namen = ["Zentrale", ...(await ladeKonfig(this._hass)).rolllaeden.map((r) => r.name).sort()]; } catch (e) { /* leer */ }
    }
    return super._zeichnen();
  }
  schema() {
    const h = this._hass;
    return [
      ...super.schema(),
      { name: "zeitraum", selector: { select: { mode: "dropdown", options: ZEITRAEUME.map((z) => ({ value: z, label: tx(h, `p_${z}`) })) } } },
      { name: "rolllaeden", selector: { select: { multiple: true, options: (this._namen || []).map((n) => ({ value: n, label: n })) } } },
      { name: "arten", selector: { select: { multiple: true, options: Object.keys(ARTEN.de).map((a) => ({ value: a, label: artText(h, a) })) } } },
      { name: "filter", selector: { boolean: {} } },
      { name: "anzeigen", selector: { boolean: {} } },
    ];
  }
  _daten() { return { zeitraum: "heute", filter: true, anzeigen: false, ...this._config }; }
}

class AnsichtVorlage extends HTMLElement {
  static async generate(config, hass) { return ansichtBauen(config, hass); }
}
class DashboardVorlage extends HTMLElement {
  static getCreateSuggestions(hass) { return { title: tx(hass, "rolllaeden"), icon: "mdi:window-shutter-auto" }; }
  static async generate(config, hass) {
    return { title: config.title, views: [{ strategy: { ...config, type: "custom:rollladensteuerung" },
      title: config.title || tx(hass, "rolllaeden"), path: "rollladen", icon: "mdi:window-shutter-auto" }] };
  }
}

const definieren = (name, klasse) => { if (!customElements.get(name)) customElements.define(name, klasse); };
definieren("rollladensteuerung-card", RollladenKarte);
definieren("rollladensteuerung-zentrale-card", ZentraleKarte);
definieren("rollladensteuerung-dialog", EinstellDialog);
definieren("rollladensteuerung-meldungen-card", MeldungenKarte);
definieren("rollladensteuerung-sonne-card", SonneKarte);
definieren("rollladensteuerung-protokoll", ProtokollDialog);
definieren("rollladensteuerung-protokoll-card", ProtokollKarte);
definieren("ll-strategy-section-rollladensteuerung-protokoll", AbschnittProtokoll);
definieren("rollladensteuerung-protokoll-editor", ProtokollEditor);
definieren("ll-strategy-view-rollladensteuerung", AnsichtVorlage);
definieren("ll-strategy-dashboard-rollladensteuerung", DashboardVorlage);
definieren("ll-strategy-section-rollladensteuerung", AbschnittRolllaeden);
definieren("ll-strategy-section-rollladensteuerung-steuerung", AbschnittSteuerung);
definieren("ll-strategy-section-rollladensteuerung-meldungen", AbschnittMeldungen);
definieren("rollladensteuerung-abschnitt-editor", RolllaedenEditor);
definieren("rollladensteuerung-steuerung-editor", SteuerungEditor);
definieren("rollladensteuerung-meldungen-editor", AbschnittEditor);

// im Dashboard-Editor auswählbar (Automatischer Abschnitt → Community / Neues Dashboard → Community)
{
  const sprache = (document.documentElement.lang || navigator.language || "en").split("-")[0];
  const t = (key) => (TEXTE[sprache] || TEXTE.en)[key];
  window.customStrategies = window.customStrategies || [];
  const doku = "https://github.com/Cluni2k/ha-rollladensteuerung";
  for (const [type, strategyType, name, description] of [
    ["rollladensteuerung", "section", t("v_rolllaeden"), t("v_rolllaeden_text")],
    ["rollladensteuerung-steuerung", "section", t("v_steuerung"), t("v_steuerung_text")],
    ["rollladensteuerung-meldungen", "section", t("v_meldungen"), t("v_meldungen_text")],
    ["rollladensteuerung-protokoll", "section", t("v_protokoll"), t("v_protokoll_text")],
    ["rollladensteuerung", "dashboard", t("zentrale"), t("v_dashboard_text")],
  ]) {
    if (!window.customStrategies.some((s) => s.type === type && s.strategyType === strategyType)) {
      window.customStrategies.push({ type, strategyType, name, description, documentationURL: doku });
    }
  }
}

window.customCards = window.customCards || [];
window.customCards.push(
  { type: "rollladensteuerung-card", name: "Rollladen (Rollladensteuerung)", description: "Rollladen mit Automatik-Status und Einstellungen", preview: false },
  { type: "rollladensteuerung-meldungen-card", name: "Rollladensteuerung – Benachrichtigungen & Protokoll", description: "Push-Schalter und Protokoll", preview: false },
  { type: "rollladensteuerung-protokoll-card", name: "Rollladensteuerung – Protokoll", description: "Protokoll mit Zeitraum, Filtern und CSV-Download", preview: false },
  { type: "rollladensteuerung-zentrale-card", name: "Rollladensteuerung – Zentrale", description: "Globale Schalter und Einstellungen", preview: false },
);
console.info(`%c ROLLLADENSTEUERUNG %c ${VERSION} `, "background:#926bc7;color:#fff", "background:#ddd;color:#000");
