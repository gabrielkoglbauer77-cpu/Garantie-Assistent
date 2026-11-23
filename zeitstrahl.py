"""Die Rechnung hinter dem Zeitstrahl — getrennt von der Darstellung.

So lässt sich prüfen, ob der Balken das Richtige zeigt, ohne die App zu
starten. In dieser Datei steht keine einzige Farbe.
"""

from __future__ import annotations

from dataclasses import dataclass

from recht.gewaehrleistung import monate_zwischen


@dataclass
class Abschnitt:
    """Ein farbiger Abschnitt des Balkens, gemessen in Monaten."""

    id: str
    start: int
    breite: int
    titel: str


@dataclass
class Strahl:
    """Alles, was die Anzeige zum Zeichnen braucht."""

    monate: int
    gesamt: int
    abschnitte: list[Abschnitt]
    heute_prozent: float
    garantie: int


def strahl_bauen(kaufdatum: str, garantie_monate: int | None,
                 heute_iso: str) -> Strahl:
    """Teilt die Zeit seit dem Kauf in Abschnitte.

    Die Gesamtlänge ist das Maximum aus 24 Monaten, der Garantiedauer und
    ``monate + 1`` — sonst stünde „heute“ bei einem alten Gerät außerhalb.
    """
    monate = monate_zwischen(kaufdatum, heute_iso)
    garantie = max(0, garantie_monate or 0)
    gesamt = max(24, garantie, monate + 1)

    grenzen = [("beweislast", 12, "Händler muss beweisen"),
               ("gewaehrleistung", 24, "Du musst beweisen")]
    if garantie > 24:
        grenzen.append(("garantie", garantie, "nur Garantie"))
    grenzen.append(("vorbei", gesamt, "keine Ansprüche auf dem Regelweg"))

    abschnitte = []
    gelaufen = 0
    for kennung, grenze, titel in grenzen:
        bis = min(grenze, gesamt)
        if bis - gelaufen > 0:
            abschnitte.append(Abschnitt(kennung, gelaufen, bis - gelaufen,
                                        titel))
        gelaufen = bis

    # Bei 100 % läge der Strich auf dem Rand und wäre halb abgeschnitten.
    prozent = min(99.6, max(0.0, monate / gesamt * 100))
    return Strahl(monate, gesamt, abschnitte, prozent, min(garantie, gesamt))
