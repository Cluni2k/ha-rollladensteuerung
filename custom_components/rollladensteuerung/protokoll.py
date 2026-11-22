"""Protokoll der Rollladensteuerung: alle Aktionen der letzten 90 Tage (JSON-Zeilen in .storage)."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util

from .const import DOMAIN

AUFBEWAHRUNG_TAGE = 90


class Protokoll:
    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self.hass = hass
        self.pfad = Path(hass.config.path(".storage", f"{DOMAIN}.{entry_id}.protokoll.jsonl"))
        self._puffer: list[dict] = []
        self._sperre = asyncio.Lock()
        self._aufgabe: asyncio.Task | None = None

    @callback
    def eintragen(self, rollladen: str, art: str, text: str) -> None:
        self._puffer.append({"zeit": dt_util.now().isoformat(timespec="seconds"),
                             "rollladen": rollladen, "art": art, "text": text})
        if self._aufgabe is None or self._aufgabe.done():
            self._aufgabe = self.hass.async_create_task(self._schreiben())

    async def _schreiben(self) -> None:
        async with self._sperre:
            await asyncio.sleep(1)  # mehrere Einträge auf einmal schreiben
            zeilen, self._puffer = self._puffer, []
            if not zeilen:
                return
            text = "".join(json.dumps(z, ensure_ascii=False) + "\n" for z in zeilen)

            def _anhaengen() -> None:
                self.pfad.parent.mkdir(parents=True, exist_ok=True)
                with self.pfad.open("a", encoding="utf-8") as datei:
                    datei.write(text)
            await self.hass.async_add_executor_job(_anhaengen)

    def _laden(self) -> list[dict]:
        if not self.pfad.exists():
            return []
        eintraege = []
        for zeile in self.pfad.read_text("utf-8").splitlines():
            try:
                eintraege.append(json.loads(zeile))
            except ValueError:
                continue
        return eintraege

    async def lesen(self, tage: int = AUFBEWAHRUNG_TAGE, von: datetime | None = None,
                    bis: datetime | None = None) -> list[dict]:
        """Einträge eines Zeitraums (von/bis mit Zeitzone); ohne von: die letzten `tage` Tage."""
        await self._schreiben()
        if von is None:
            von = dt_util.now() - timedelta(days=tage)
        eintraege = await self.hass.async_add_executor_job(self._laden)
        aus = []
        for e in eintraege:
            zeit = self.als_zeit(e.get("zeit", ""))
            if zeit is None or zeit.tzinfo is None or zeit < von or (bis is not None and zeit > bis):
                continue
            aus.append(e)
        return aus

    async def bereinigen(self) -> None:
        """Einträge älter als AUFBEWAHRUNG_TAGE entfernen (täglich nachts)."""
        async with self._sperre:
            grenze = (dt_util.now() - timedelta(days=AUFBEWAHRUNG_TAGE)).isoformat(timespec="seconds")

            def _kuerzen() -> None:
                eintraege = [e for e in self._laden() if e.get("zeit", "") >= grenze]
                self.pfad.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in eintraege), "utf-8")
            if self.pfad.exists():
                await self.hass.async_add_executor_job(_kuerzen)

    @staticmethod
    def als_zeit(text: str) -> datetime | None:
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            return None
