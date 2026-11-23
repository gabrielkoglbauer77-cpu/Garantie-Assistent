"""Fristen — der Teil, an dem Ansprüche tatsächlich verloren gehen.

In einem Gewährleistungsfall laufen bis zu vier Uhren gleichzeitig:

    Händlerfrist      die Frist, die DU gesetzt hast. Läuft sie ab,
                      entstehen Preisminderung und Wandlung.
    Beweislast        zwölf Monate ab Übergabe. Danach musst du beweisen,
                      dass der Mangel von Anfang an bestand.
    Gewährleistung    zwei Jahre ab Übergabe. Danach ist der Regelweg zu.
    Garantie          was in der Zusage des Herstellers steht.

Gerechnet wird in ganzen Kalendertagen. ``date`` kennt keine Uhrzeit,
deshalb verschiebt die Sommerzeitumstellung hier nichts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from daten import Fall, datum_de
from recht.gewaehrleistung import Lage, lage_ermitteln, plus_monate


@dataclass
class Fristlage:
    """Eine laufende oder abgelaufene Frist."""

    art: str
    titel: str
    ziel: str
    tage_rest: int
    zustand: str
    bedeutung: str


@dataclass
class Schritt:
    """Der eine nächste Schritt mit Begründung."""

    titel: str
    warum: str
    dringend: bool


def tage_zwischen(von_iso: str, bis_iso: str) -> int:
    """Ganze Tage von a nach b; negativ, wenn b vor a liegt."""
    von = date.fromisoformat(von_iso[:10])
    bis = date.fromisoformat(bis_iso[:10])
    return (bis - von).days


def zustand_aus(tage_rest: int) -> str:
    """Ordnet die Restlaufzeit einem von vier Zuständen zu."""
    if tage_rest < 0:
        return "ueberschritten"
    if tage_rest == 0:
        return "heute"
    if tage_rest <= 7:
        return "knapp"
    return "offen"


def _garantie_ende(fall: Fall) -> str | None:
    if fall.kaufdatum and fall.garantie_monate is not None:
        return plus_monate(fall.kaufdatum, fall.garantie_monate)
    return None


def _fristziele(fall: Fall, lage: Lage) -> list[tuple]:
    """Die vier möglichen Fristen als (Art, Titel, Ziel, Bedeutung)."""
    return [
        ("haendler", "Frist an den Händler", fall.frist,
         "Ist sie abgelaufen, kannst du Preisminderung verlangen oder den "
         "Vertrag auflösen."),
        ("beweislast", "Beweislast kippt", lage.beweislast_ende,
         "Bis dahin muss der Händler beweisen, dass die Ware in Ordnung "
         "war. Danach musst du es umgekehrt beweisen."),
        ("gewaehrleistung", "Gewährleistung endet", lage.frist_ende,
         "Danach ist der gesetzliche Regelweg zu. Die Anzeige muss vorher "
         "heraus sein."),
        ("garantie", "Herstellergarantie endet", _garantie_ende(fall),
         "Zusätzlicher Weg neben der Gewährleistung — sein Ende ändert an "
         "den gesetzlichen Rechten nichts."),
    ]


def fristen_fuer(fall: Fall, heute_iso: str) -> list[Fristlage]:
    """Alle berechenbaren Fristen, die dringendste zuerst."""
    lage = lage_ermitteln(fall, heute_iso)
    liste = []
    for art, titel, ziel, bedeutung in _fristziele(fall, lage):
        if not ziel:
            continue
        rest = tage_zwischen(heute_iso, ziel)
        liste.append(Fristlage(art, titel, ziel, rest, zustand_aus(rest),
                               bedeutung))
    return sorted(liste, key=lambda f: f.tage_rest)


def _schritt_abgeschlossen(fall: Fall) -> Schritt | None:
    if fall.status == "geloest":
        return Schritt("Erledigt", "Der Fall ist abgeschlossen.", False)
    if fall.status == "aufgegeben":
        return Schritt(
            "Nicht weiterverfolgt",
            "Du hast den Fall bewusst liegen gelassen. Solange die "
            "Gewährleistungsfrist läuft, kannst du ihn jederzeit wieder "
            "aufnehmen.",
            False,
        )
    return None


def _schritt_neu(lage: Lage, heute_iso: str) -> Schritt:
    if lage.beweislast_beim_haendler:
        warum = (
            "Die Beweislast liegt noch bis "
            f"{datum_de(lage.beweislast_ende)} beim Händler. Jetzt "
            "gesendet, muss er beweisen, dass die Ware in Ordnung war."
        )
    else:
        warum = ("Die Anzeige setzt die Frist in Gang, an die "
                 "Preisminderung und Wandlung anknüpfen.")
    bald = False
    if lage.beweislast_ende:
        bald = tage_zwischen(heute_iso, lage.beweislast_ende) <= 30
    return Schritt("Mängelanzeige senden", warum,
                   not lage.in_frist or bald)


def _schritt_mit_frist(fall: Fall, heute_iso: str) -> Schritt:
    fristen = fristen_fuer(fall, heute_iso)
    eigene = next((f for f in fristen if f.art == "haendler"), None)
    if eigene is None:
        return Schritt(
            "Frist setzen",
            "Du hast den Mangel gemeldet, aber keine Frist mit Datum "
            "gesetzt. Ohne Datum entstehen keine weiteren Rechte.",
            True,
        )
    if eigene.tage_rest < 0:
        return Schritt(
            "Vertragsauflösung erklären",
            f"Deine Frist ist am {datum_de(eigene.ziel)} abgelaufen. Damit "
            "sind Preisminderung und Wandlung offen.",
            True,
        )
    return Schritt(
        "Antwort abwarten",
        f"Die Frist läuft bis {datum_de(eigene.ziel)} ({eigene.tage_rest} "
        "Tage). Kommt bis dahin nichts, folgt die letzte Nachfrist.",
        False,
    )


def naechster_schritt(fall: Fall, heute_iso: str) -> Schritt:
    """Genau ein nächster Schritt — eine Liste mit zwölf führt zu nichts."""
    abgeschlossen = _schritt_abgeschlossen(fall)
    if abgeschlossen:
        return abgeschlossen
    if not fall.kaufdatum:
        return Schritt(
            "Kaufdatum nachtragen",
            "Ohne Kaufdatum lässt sich keine Frist berechnen — und das "
            "Kaufdatum entscheidet darüber, wer was beweisen muss.",
            True,
        )
    if fall.status == "neu":
        return _schritt_neu(lage_ermitteln(fall, heute_iso), heute_iso)
    if fall.status == "abgelehnt":
        return Schritt(
            "Ablehnung kontern",
            "Eine unbeantwortete Ablehnung wird zum Ergebnis. Die Antwort "
            "braucht die Norm und ein Fristdatum.",
            True,
        )
    return _schritt_mit_frist(fall, heute_iso)


def rest_text(tage_rest: int) -> str:
    """„in 12 Tagen“, „seit 3 Tagen abgelaufen“ oder „heute“."""
    if tage_rest == 0:
        return "heute"
    if tage_rest < 0:
        anzahl = -tage_rest
        return f"seit {anzahl} {'Tag' if anzahl == 1 else 'Tagen'} abgelaufen"
    return f"in {tage_rest} {'Tag' if tage_rest == 1 else 'Tagen'}"
