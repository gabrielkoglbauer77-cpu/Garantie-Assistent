"""Beispieldaten zum Ausprobieren — ein- und ausschaltbar.

Jeder Demo-Eintrag trägt ``demo=True``. Dadurch lässt sich die Demo
abschalten, ohne die eigenen Fälle und Geräte anzurühren: Entfernt werden
nur die markierten Einträge.

Alle Datumsangaben werden relativ zum heutigen Tag berechnet. Ein fest
eingetragenes Kaufdatum wäre nach einem halben Jahr aus der Gewährleistung
gelaufen, und die Demo würde das Gegenteil von dem zeigen, was sie soll.

``demo_faelle`` und ``demo_geraete`` speichern nichts, sie geben die Daten
nur zurück. Gespeichert wird in ``demo_einschalten``.
"""

from __future__ import annotations

import daten
from daten import Ereignis, Fall, Geraet, heute, plus_tage
from recht.gewaehrleistung import plus_monate


def vor_monaten(anzahl: int) -> str:
    """Datum vor n Monaten."""
    return plus_monate(heute(), -anzahl)


def vor_tagen(anzahl: int) -> str:
    """Datum vor n Tagen."""
    return plus_tage(heute(), -anzahl)


def _ereignis(tage: int, art: str, text: str) -> Ereignis:
    return Ereignis(datum=vor_tagen(tage), art=art, text=text)


def _kopfhoerer() -> Fall:
    return Fall(
        produkt="Bluetooth-Kopfhörer", status="neu",
        beschreibung="Der linke Kanal fällt nach etwa zehn Minuten aus und "
                     "kommt erst nach einem Neustart wieder.",
        haendler="Elektro Müller GmbH", haendler_email="service@beispiel.at",
        kaufdatum=vor_monaten(8), mangel_seit=vor_tagen(6), preis=249.9,
        bestellnummer="BST-99213", garantie_monate=24,
    )


def _waschmaschine() -> Fall:
    return Fall(
        produkt="Waschmaschine", status="abgelehnt",
        beschreibung="Die Trommel blockiert im Schleudergang, Fehlercode "
                     "E18.",
        haendler="HausTechnik24", haendler_email="reklamation@beispiel.at",
        kaufdatum=vor_monaten(14), mangel_seit=vor_tagen(40), preis=629.0,
        bestellnummer="HT-2026-4471", frist=vor_tagen(12),
        ereignisse=[
            _ereignis(38, "gesendet", "Mängelanzeige an HausTechnik24"),
            _ereignis(38, "frist", "Frist gesetzt"),
            _ereignis(26, "erhalten",
                      "Antwort: „Hierbei handelt es sich um normalen "
                      "Verschleiß, zudem ist die Garantie abgelaufen.“"),
            _ereignis(25, "notiz", "Hotline: Rückruf zugesagt, nie erfolgt."),
        ],
    )


def _notebook() -> Fall:
    return Fall(
        produkt="Notebook", status="gemeldet",
        beschreibung="Das Display zeigt einen hellen Streifen am linken "
                     "Rand, der sich beim Aufklappen verbreitert.",
        haendler="Technikwelt", haendler_email="support@beispiel.at",
        kaufdatum=vor_monaten(5), mangel_seit=vor_tagen(21), preis=1149.0,
        bestellnummer="TW-88120", garantie_monate=36, frist=vor_tagen(4),
        ereignisse=[
            _ereignis(18, "gesendet", "Mängelanzeige an Technikwelt"),
            _ereignis(18, "frist", "Frist gesetzt"),
            _ereignis(9, "erhalten",
                      "„Ihr Fall wird geprüft, wir melden uns.“"),
        ],
    )


def _smartphone() -> Fall:
    return Fall(
        produkt="Smartphone", status="eskaliert",
        beschreibung="Der Akku hält nach kurzer Zeit nur noch zwei Stunden; "
                     "Akkuzustand laut System 61 %.",
        haendler="Mobilshop", haendler_email="kundenservice@beispiel.at",
        kaufdatum=vor_monaten(20), mangel_seit=vor_tagen(60), preis=899.0,
        bestellnummer="MS-55019", garantie_monate=24, frist=vor_tagen(2),
        ereignisse=[
            _ereignis(55, "gesendet", "Mängelanzeige an Mobilshop"),
            _ereignis(41, "erhalten",
                      "Reparatur abgelehnt, Verweis an den Hersteller"),
            _ereignis(16, "gesendet", "Letzte Nachfrist gesetzt"),
        ],
    )


def _kaffeemaschine() -> Fall:
    return Fall(
        produkt="Kaffeemaschine", status="geloest",
        beschreibung="Pumpe defekt, kein Druckaufbau.",
        haendler="Küchenhaus Wien", kaufdatum=vor_monaten(10),
        mangel_seit=vor_monaten(3), preis=329.0, bestellnummer="KHW-1174",
        ereignisse=[
            Ereignis(vor_monaten(3), "gesendet", "Mängelanzeige mit Frist"),
            Ereignis(vor_monaten(2), "erhalten", "Austauschgerät zugesagt"),
            Ereignis(vor_monaten(2), "status", "Status: Gelöst"),
        ],
    )


def demo_faelle() -> list[Fall]:
    """Fünf Fälle, jeder Zustand einmal."""
    faelle = [_kopfhoerer(), _waschmaschine(), _notebook(), _smartphone(),
              _kaffeemaschine()]
    for fall in faelle:
        fall.demo = True
    return faelle


def demo_geraete() -> list[Geraet]:
    """Fünf Geräte: frisch, lange Garantie, abgelaufen, ohne Kaufdatum."""
    geraete = [
        Geraet(name="Fernseher 55 Zoll", hersteller="Samsung",
               haendler="Elektro Müller GmbH", kaufdatum=vor_monaten(21),
               preis=749.0, garantie_monate=24, seriennummer="SN-4471-9920",
               notiz="Rechnung liegt im Ordner „Belege 2025“."),
        Geraet(name="Geschirrspüler", hersteller="Bosch",
               haendler="HausTechnik24", kaufdatum=vor_monaten(4),
               preis=579.0, garantie_monate=60, seriennummer="BSH-88-2291",
               notiz="Fünf Jahre Herstellergarantie nach Registrierung."),
        Geraet(name="E-Bike", hersteller="KTM", haendler="Radhaus Linz",
               kaufdatum=vor_monaten(11), preis=2390.0, garantie_monate=24,
               seriennummer="KTM-2026-00412",
               notiz="Akku separat: eigene Garantie über 500 Ladezyklen."),
        Geraet(name="Staubsauger", hersteller="Dyson",
               haendler="Technikwelt", kaufdatum=vor_monaten(26),
               preis=449.0, garantie_monate=24, seriennummer="DY-7781"),
        Geraet(name="Kopfhörer", hersteller="Sony",
               haendler="Elektro Müller GmbH", kaufdatum=None, preis=249.9,
               garantie_monate=24,
               notiz="Kaufdatum nachtragen — Rechnung suchen."),
    ]
    for geraet in geraete:
        geraet.demo = True
    return geraete


def demo_aktiv() -> bool:
    """Ist gerade mindestens ein Demo-Eintrag vorhanden?"""
    return (any(f.demo for f in daten.faelle_laden())
            or any(g.demo for g in daten.geraete_laden()))


def demo_ausschalten() -> None:
    """Entfernt alle Demo-Einträge; eigene Fälle und Geräte bleiben."""
    for fall in daten.faelle_laden():
        if fall.demo:
            daten.fall_loeschen(fall.id)
    eigene = [g for g in daten.geraete_laden() if not g.demo]
    daten.geraete_speichern(eigene)


def demo_einschalten() -> None:
    """Fügt die Demo-Einträge hinzu, vor die eigenen Einträge."""
    demo_ausschalten()
    daten.alles_ersetzen(demo_faelle() + daten.faelle_laden(),
                         demo_geraete() + daten.geraete_laden())


def beim_ersten_start_anlegen() -> bool:
    """Schaltet die Demo ein, wenn es noch gar keine Daten gibt.

    So ist die App sofort gefüllt. Gibt es die Dateien schon — auch leer,
    weil jemand die Demo abgeschaltet hat —, bleibt alles, wie es ist.
    Gibt True zurück, wenn die Demo eingeschaltet wurde.
    """
    if daten.FAELLE_DATEI.exists() or daten.GERAETE_DATEI.exists():
        return False
    demo_einschalten()
    return True
