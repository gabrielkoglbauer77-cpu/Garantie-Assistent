"""Datenmodell und Speicher des Garantie-Assistenten.

Ein Fall und ein Gerät sind flache Datensätze ohne Verweise auf andere
Tabellen. Gespeichert wird als JSON-Datei im Ordner ``daten`` neben dem
Programm. Der Pfad wird relativ zu dieser Datei gebildet, damit die App
auf jedem Rechner ohne Anpassung läuft.

Warum JSON und nicht SQLite: Ein Fall ist ein verschachteltes Objekt mit
Verlauf und Belegen. Als JSON passt er ohne Umbau in eine Datei, lässt sich
mit jedem Editor lesen und als Sicherung exportieren.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field, fields
from datetime import date, timedelta
from pathlib import Path

DATEN_ORDNER = Path(__file__).parent / "daten"
FAELLE_DATEI = DATEN_ORDNER / "faelle.json"
GERAETE_DATEI = DATEN_ORDNER / "geraete.json"
BELEGE_ORDNER = DATEN_ORDNER / "belege"

RECHTSORDNUNGEN = {"AT": "Österreich", "DE": "Deutschland"}

STATUS_TEXT = {
    "neu": "Neu",
    "gemeldet": "Gemeldet",
    "abgelehnt": "Abgelehnt",
    "eskaliert": "Eskaliert",
    "geloest": "Gelöst",
    "aufgegeben": "Aufgegeben",
}

EREIGNIS_ARTEN = {
    "notiz": "Notiz",
    "gesendet": "Gesendet",
    "erhalten": "Erhalten",
    "frist": "Frist",
    "status": "Status",
}


# ── Hilfsfunktionen für Datum und Geld ─────────────────────────────────────

def neue_id() -> str:
    """Eindeutige Kennung für Fälle, Geräte, Einträge und Belege."""
    return uuid.uuid4().hex


def heute() -> str:
    """Heutiges Datum als ISO-Text, z. B. ``2026-11-23``."""
    return date.today().isoformat()


def plus_tage(iso: str, tage: int) -> str:
    """Datum plus n Tage, wieder als ISO-Text."""
    return (date.fromisoformat(iso[:10]) + timedelta(days=tage)).isoformat()


def datum_de(iso: str | None) -> str:
    """``2026-03-07`` wird zu ``07.03.2026``; fehlt das Datum, ein Strich."""
    if not iso:
        return "—"
    jahr, monat, tag = iso[:10].split("-")
    return f"{tag}.{monat}.{jahr}"


def euro(betrag: float | None) -> str:
    """Betrag im österreichischen Format: ``€ 1.149,00``."""
    if betrag is None:
        return "—"
    text = f"{betrag:,.2f}".replace(",", "X").replace(".", ",")
    return "€ " + text.replace("X", ".")


# ── Das Datenmodell ────────────────────────────────────────────────────────

@dataclass
class Ereignis:
    """Ein Eintrag im Verlauf — die Beweiskette des Falls."""

    datum: str
    art: str
    text: str
    id: str = field(default_factory=neue_id)


@dataclass
class Beleg:
    """Ein Foto oder eine Rechnung; die Datei liegt in ``daten/belege``."""

    name: str
    typ: str
    groesse: int
    datei: str
    belegt: str = field(default_factory=heute)
    id: str = field(default_factory=neue_id)


@dataclass
class Fall:  # pylint: disable=too-many-instance-attributes
    """Ein Garantiefall: was, bei wem, wann, und was seitdem passiert ist."""

    produkt: str = ""
    beschreibung: str = ""
    mangel_seit: str | None = None
    haendler: str = ""
    haendler_email: str = ""
    kaufdatum: str | None = None
    preis: float | None = None
    bestellnummer: str = ""
    recht: str = "AT"
    garantie_monate: int | None = None
    status: str = "neu"
    frist: str | None = None
    ereignisse: list[Ereignis] = field(default_factory=list)
    belege: list[Beleg] = field(default_factory=list)
    demo: bool = False
    id: str = field(default_factory=neue_id)
    angelegt: str = field(default_factory=heute)

    @property
    def erledigt(self) -> bool:
        """Gelöste und aufgegebene Fälle brauchen keine Handlung mehr."""
        return self.status in ("geloest", "aufgegeben")


@dataclass
class Geraet:  # pylint: disable=too-many-instance-attributes
    """Ein Kauf, eingetragen solange noch alles funktioniert."""

    name: str = ""
    hersteller: str = ""
    haendler: str = ""
    kaufdatum: str | None = None
    preis: float | None = None
    garantie_monate: int | None = None
    seriennummer: str = ""
    notiz: str = ""
    fall_id: str | None = None
    demo: bool = False
    id: str = field(default_factory=neue_id)
    angelegt: str = field(default_factory=heute)


# ── Umwandeln zwischen Objekt und JSON ─────────────────────────────────────

def _nur_bekannte(klasse, roh: dict) -> dict:
    """Unbekannte Felder verwerfen, damit alte Dateien lesbar bleiben."""
    namen = {f.name for f in fields(klasse)}
    return {k: v for k, v in roh.items() if k in namen}


def fall_aus_dict(roh: dict) -> Fall:
    """Baut einen Fall samt Verlauf und Belegen aus einem Wörterbuch."""
    werte = _nur_bekannte(Fall, roh)
    werte["ereignisse"] = [
        Ereignis(**_nur_bekannte(Ereignis, e))
        for e in roh.get("ereignisse", [])
    ]
    werte["belege"] = [
        Beleg(**_nur_bekannte(Beleg, b)) for b in roh.get("belege", [])
    ]
    return Fall(**werte)


def geraet_aus_dict(roh: dict) -> Geraet:
    """Baut ein Gerät aus einem Wörterbuch."""
    return Geraet(**_nur_bekannte(Geraet, roh))


# ── Lesen und Schreiben ────────────────────────────────────────────────────

def liste_laden(datei: Path) -> list[dict]:
    """Liest eine JSON-Liste; eine fehlende oder kaputte Datei ist leer."""
    try:
        inhalt = json.loads(datei.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return inhalt if isinstance(inhalt, list) else []


def liste_speichern(datei: Path, liste: list[dict]) -> None:
    """Schreibt eine JSON-Liste und legt den Ordner bei Bedarf an."""
    datei.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(liste, ensure_ascii=False, indent=2)
    datei.write_text(text, encoding="utf-8")


def faelle_laden() -> list[Fall]:
    """Alle Fälle aus ``daten/faelle.json``."""
    return [fall_aus_dict(r) for r in liste_laden(FAELLE_DATEI)]


def geraete_laden() -> list[Geraet]:
    """Alle Geräte aus ``daten/geraete.json``."""
    return [geraet_aus_dict(r) for r in liste_laden(GERAETE_DATEI)]


def faelle_speichern(faelle: list[Fall]) -> None:
    """Schreibt alle Fälle zurück."""
    liste_speichern(FAELLE_DATEI, [asdict(f) for f in faelle])


def geraete_speichern(geraete: list[Geraet]) -> None:
    """Schreibt alle Geräte zurück."""
    liste_speichern(GERAETE_DATEI, [asdict(g) for g in geraete])


def fall_finden(fall_id: str) -> Fall | None:
    """Sucht einen Fall über seine Kennung."""
    return next((f for f in faelle_laden() if f.id == fall_id), None)


def fall_sichern(fall: Fall) -> None:
    """Ersetzt einen bekannten Fall oder stellt einen neuen nach vorne."""
    faelle = faelle_laden()
    if any(f.id == fall.id for f in faelle):
        faelle = [fall if f.id == fall.id else f for f in faelle]
    else:
        faelle.insert(0, fall)
    faelle_speichern(faelle)


def fall_loeschen(fall_id: str) -> None:
    """Löscht einen Fall samt seinen Beleg-Dateien."""
    fall = fall_finden(fall_id)
    if fall:
        for beleg in fall.belege:
            beleg_pfad(beleg).unlink(missing_ok=True)
    faelle_speichern([f for f in faelle_laden() if f.id != fall_id])


def geraet_sichern(geraet: Geraet) -> None:
    """Ersetzt ein bekanntes Gerät oder stellt ein neues nach vorne."""
    geraete = geraete_laden()
    if any(g.id == geraet.id for g in geraete):
        geraete = [geraet if g.id == geraet.id else g for g in geraete]
    else:
        geraete.insert(0, geraet)
    geraete_speichern(geraete)


def geraet_loeschen(geraet_id: str) -> None:
    """Löscht ein Gerät."""
    geraete_speichern([g for g in geraete_laden() if g.id != geraet_id])


def alles_ersetzen(faelle: list[Fall], geraete: list[Geraet]) -> None:
    """Ersetzt den gesamten Bestand — für Demo, Import und Zurücksetzen."""
    faelle_speichern(faelle)
    geraete_speichern(geraete)


# ── Belege ─────────────────────────────────────────────────────────────────

def beleg_pfad(beleg: Beleg) -> Path:
    """Wo die Datei eines Belegs auf der Festplatte liegt."""
    return BELEGE_ORDNER / beleg.datei


def beleg_ablegen(name: str, typ: str, inhalt: bytes) -> Beleg:
    """Speichert eine Datei im Belegordner und gibt den Beleg zurück."""
    endung = Path(name).suffix.lower() or ".bin"
    beleg = Beleg(name=name, typ=typ, groesse=len(inhalt), datei="")
    beleg.datei = beleg.id + endung
    BELEGE_ORDNER.mkdir(parents=True, exist_ok=True)
    beleg_pfad(beleg).write_bytes(inhalt)
    return beleg


# ── Sicherung ──────────────────────────────────────────────────────────────

def als_json(faelle: list[Fall], geraete: list[Geraet]) -> str:
    """Alles als eine Datei zum Herunterladen."""
    daten = {
        "exportiert": heute(),
        "faelle": [asdict(f) for f in faelle],
        "geraete": [asdict(g) for g in geraete],
    }
    return json.dumps(daten, ensure_ascii=False, indent=2)


def aus_json(text: str) -> tuple[list[Fall], list[Geraet], str | None]:
    """Liest eine Sicherung. Gibt Fälle, Geräte und eine Fehlermeldung."""
    try:
        daten = json.loads(text)
    except json.JSONDecodeError:
        return [], [], "Die Datei ist kein gültiges JSON."
    if isinstance(daten, list):
        return [fall_aus_dict(r) for r in daten], [], None
    if not isinstance(daten, dict):
        return [], [], "Die Datei hat ein unbekanntes Format."
    faelle = [fall_aus_dict(r) for r in daten.get("faelle") or []]
    geraete = [geraet_aus_dict(r) for r in daten.get("geraete") or []]
    if not faelle and not geraete:
        return [], [], "In der Datei sind keine Fälle oder Geräte enthalten."
    return faelle, geraete, None
