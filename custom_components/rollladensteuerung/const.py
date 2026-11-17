"""Konstanten der Rollladensteuerung."""
DOMAIN = "rollladensteuerung"

SUB_ROLLLADEN = "rollladen"
SUB_HELLIGKEIT = "helligkeit"

# globale Einstellungen
CONF_ANWESENHEIT = "anwesenheit"
CONF_TEMPERATUR = "temperatur"
CONF_WERKTAG = "werktag"
CONF_SONNE = "sonne"
CONF_ASTRO_MORGENS = "astro_morgens"
CONF_ASTRO_ABENDS = "astro_abends"
CONF_HORIZONT_MORGENS = "horizont_morgens"
CONF_HORIZONT_ABENDS = "horizont_abends"
CONF_FROST_TEMP = "frost_temp"
CONF_HELLIGKEIT_MIN = "helligkeit_min"
CONF_WETTER = "wetter"
CONF_ABSTAND = "abstand_sekunden"
CONF_PUSH = "push_dienst"
CONF_RAUCH = "rauchmelder"
CONF_HITZE_TEMP = "hitzeschutz_temp"
CONF_HITZE_POS = "hitzeschutz_pos"
CONF_DUNKEL = "dunkel_lux"
CONF_URLAUB_ZUFALL = "urlaub_zufall"
CONF_ZUSAMMENFASSUNG = "zusammenfassung_zeit"

# Rollladen-Felder, die nicht in core.Einstellungen stehen
CONF_COVER = "cover"
CONF_FENSTER = "fenster"
CONF_HELLIGKEITSSENSOR = "helligkeitssensor"
CONF_ENTITY = "entity"
CONF_SCHLAF = "schlaf"
CONF_RAUMTEMPERATUR = "raumtemperatur"

ASTRO_MODI = {  # Sonnenhöhe in Grad
    "real": -0.833,
    "civil": -6.0,
    "nautic": -12.0,
    "astronomic": -18.0,
    "horizon": None,
}

SCHALTER = ("morgens", "abends", "abschattung", "komfort", "partymodus", "gast", "urlaub")
# Push-Benachrichtigungen (Schalter im Dashboard)
PUSH = ("push_oeffnen", "push_schliessen", "push_warnungen", "push_lueften", "push_abschatten", "push_funktionen",
        "push_manuell", "push_zusammenfassung")
SCHALTER_STANDARD = {"morgens": True, "abends": True, "abschattung": True, "komfort": True,
                     "partymodus": False, "gast": False, "push_oeffnen": False, "push_schliessen": False,
                     "push_warnungen": True, "push_lueften": False, "push_abschatten": False,
                     "push_funktionen": False, "push_manuell": False,
                     "urlaub": False, "push_zusammenfassung": False}
AUSFALL_MINUTEN = 15   # so lange darf ein Sensor/Rollladen nicht erreichbar sein, bevor gewarnt wird

EVENT_FAHRT = "rollladensteuerung_fahrt"
SIGNAL_UPDATE = "rollladensteuerung_update_{}"

NACHT_RESET = (3, 5, 0)
ABSCHATTUNG_INTERVALL_MIN = 2
