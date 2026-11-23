"""Prüfungen der Rechen- und Rechtslogik.

Starten mit:

    python pruefung.py

Geprüft werden vor allem Grenzen, nicht die Mitte: genau 12 Monate, genau
24, Monatsenden, Schaltjahr. Die Prüfungen brauchen keine Oberfläche und
laufen in unter einer Sekunde.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from daten import (Fall, aus_json, als_json, datum_de, euro, liste_laden,
                   liste_speichern, plus_tage)
import daten
from demo import (beim_ersten_start_anlegen, demo_aktiv, demo_ausschalten,
                  demo_einschalten, demo_faelle, demo_geraete)
from recht.ablehnungen import (ABLEHNUNGEN, ablehnung_nach,
                               ablehnungen_erkennen)
from recht.fristen import (fristen_fuer, naechster_schritt, rest_text,
                           tage_zwischen)
from recht.gewaehrleistung import frist_text, lage_ermitteln, monate_zwischen
from recht.schreiben import (als_gesendet_vermerken, naechstes_schreiben,
                             schreiben_bauen)
from zeitstrahl import strahl_bauen

ANZAHL = {"ok": 0}


def pruefe(name: str, bedingung: bool) -> None:
    """Eine Prüfung: bricht mit Meldung ab, wenn die Bedingung falsch ist."""
    assert bedingung, f"FEHLGESCHLAGEN: {name}"
    ANZAHL["ok"] += 1
    print(f"  ok  {name}")


def fall(**teil) -> Fall:
    """Ein Beispielfall, gekauft am 15.01.2025 um 199 Euro."""
    werte = {"produkt": "Kopfhörer", "haendler": "Shop",
             "kaufdatum": "2025-01-15", "preis": 199.0}
    werte.update(teil)
    return Fall(**werte)


def datum_pruefen() -> None:
    """Monate und Tage zählen."""
    print("\nDatumsrechnung")
    pruefe("gleicher Tag = 0 Monate",
           monate_zwischen("2025-01-15", "2025-01-15") == 0)
    pruefe("Tag vor dem Monatstag zählt nicht",
           monate_zwischen("2025-01-15", "2025-02-14") == 0)
    pruefe("Monatstag erreicht = 1",
           monate_zwischen("2025-01-15", "2025-02-15") == 1)
    pruefe("zwei Jahre = 24",
           monate_zwischen("2025-01-15", "2027-01-15") == 24)
    pruefe("Jahreswechsel", monate_zwischen("2024-11-30", "2025-03-01") == 3)
    pruefe("Schaltjahr 29.02.",
           monate_zwischen("2024-02-29", "2024-03-29") == 1)
    pruefe("ein Tag", tage_zwischen("2026-03-01", "2026-03-02") == 1)
    pruefe("rückwärts negativ", tage_zwischen("2026-03-10", "2026-03-01")
           == -9)
    pruefe("über Sommerzeitumstellung",
           tage_zwischen("2026-03-28", "2026-03-30") == 2)
    pruefe("plus_tage über Jahresgrenze",
           plus_tage("2025-12-31", 1) == "2026-01-01")
    pruefe("plus_tage Schaltjahr", plus_tage("2024-02-28", 1)
           == "2024-02-29")
    pruefe("datum_de", datum_de("2026-03-07") == "07.03.2026")
    pruefe("datum_de ohne Datum", datum_de(None) == "—")
    pruefe("euro", euro(1149) == "€ 1.149,00" and euro(None) == "—")


def lage_pruefen() -> None:
    """Fristen und Beweislast an ihren Grenzen."""
    print("\nRechtslage — Fristen")
    lage = lage_ermitteln(fall(), "2025-12-15")
    pruefe("11 Monate: Beweislast beim Händler",
           lage.monate == 11 and lage.beweislast_beim_haendler)
    lage = lage_ermitteln(fall(), "2026-01-15")
    pruefe("genau 12 Monate: Beweislast gekippt",
           lage.monate == 12 and not lage.beweislast_beim_haendler
           and lage.in_frist)
    pruefe("23 Monate: noch in Frist",
           lage_ermitteln(fall(), "2026-12-15").in_frist)
    pruefe("genau 24 Monate: Frist vorbei",
           not lage_ermitteln(fall(), "2027-01-15").in_frist)
    lage = lage_ermitteln(fall(), "2026-01-01")
    pruefe("Fristenden korrekt", lage.beweislast_ende == "2026-01-15"
           and lage.frist_ende == "2027-01-15")
    lage = lage_ermitteln(fall(kaufdatum="2025-01-31"), "2025-06-01")
    pruefe("31.01. bleibt am Monatsende", lage.frist_ende == "2027-01-31")
    lage = lage_ermitteln(fall(kaufdatum=None), "2026-01-01")
    pruefe("ohne Kaufdatum zugunsten des Nutzers offen",
           lage.monate is None and lage.in_frist
           and lage.beweislast_beim_haendler and lage.frist_ende is None)


def rechte_pruefen() -> None:
    """Normen, Rechte und Fallen."""
    print("\nRechtslage — Rechte und Normen")
    at = lage_ermitteln(fall(recht="AT"), "2025-06-01")
    de = lage_ermitteln(fall(recht="DE"), "2025-06-01")
    pruefe("AT zitiert ABGB, DE zitiert BGB",
           "ABGB" in at.rechte[0].norm and "ABGB" not in de.rechte[0].norm
           and "932 ABGB" in at.kernsatz and "437 BGB" in de.kernsatz)
    pruefe("sechs Rechte mit Norm und Erklärung",
           len(at.rechte) == 6 and all(
               len(r.norm) > 3 and len(r.erklaerung) > 40
               for r in at.rechte))
    spaet = lage_ermitteln(fall(), "2026-06-01").rechte[3]
    pruefe("Beweislastrecht kippt, Hinweis nennt Gutachten",
           not spaet.verfuegbar and "Gutachten" in (spaet.hinweis or ""))
    mit = fall(garantie_monate=36)
    pruefe("Garantie nur verfügbar, solange sie läuft",
           lage_ermitteln(mit, "2027-06-01").rechte[5].verfuegbar
           and not lage_ermitteln(mit, "2028-06-01").rechte[5].verfuegbar)
    pruefe("Schadenersatz immer verfügbar",
           lage_ermitteln(fall(), "2030-01-01").rechte[4].verfuegbar)
    pruefe("Fallen nennen UGB bzw. HGB",
           any("UGB" in t for t in at.fallen)
           and any("HGB" in t for t in de.fallen))
    pruefe("nach der Vermutung kommt der Beweissicherungshinweis",
           any("Monate vergangen" in t for t in
               lage_ermitteln(fall(), "2026-06-01").fallen))
    pruefe("frist_text Mehrzahl",
           frist_text(lage_ermitteln(fall(), "2025-12-15"))
           == "noch 13 Monate")
    pruefe("frist_text Einzahl",
           frist_text(lage_ermitteln(fall(), "2026-12-20")) == "noch 1 Monat")
    pruefe("frist_text abgelaufen",
           frist_text(lage_ermitteln(fall(), "2027-06-01"))
           == "Gewährleistung abgelaufen")


def fristen_pruefen() -> None:
    """Die Fristenliste und ihre Zustände."""
    print("\nFristen")
    pruefe("rest_text in allen Formen",
           [rest_text(n) for n in (0, 1, 12, -1, -3)] == [
               "heute", "in 1 Tag", "in 12 Tagen", "seit 1 Tag abgelaufen",
               "seit 3 Tagen abgelaufen"])
    pruefe("drei Fristen ohne Garantie, vier mit",
           len(fristen_fuer(fall(frist="2026-02-01"), "2026-01-20")) == 3
           and len(fristen_fuer(fall(frist="2026-02-01", garantie_monate=24),
                                "2026-01-20")) == 4)
    pruefe("ohne Kaufdatum und eigene Frist: keine Frist",
           fristen_fuer(fall(kaufdatum=None), "2026-01-20") == [])
    liste = fristen_fuer(fall(frist="2026-01-10"), "2026-01-20")
    pruefe("Dringendstes steht vorne",
           liste[0].art == "haendler" and liste[0].tage_rest == -10
           and liste[0].zustand == "ueberschritten")

    def zustand(ziel: str) -> str:
        fristen = fristen_fuer(fall(frist=ziel), "2026-01-20")
        return next(f.zustand for f in fristen if f.art == "haendler")
    pruefe("Zustände an ihren Grenzen",
           [zustand(z) for z in ("2026-01-20", "2026-01-27", "2026-01-28",
                                 "2026-01-19")]
           == ["heute", "knapp", "offen", "ueberschritten"])
    garantie = fristen_fuer(fall(kaufdatum="2025-01-31", garantie_monate=1),
                            "2025-02-01")
    pruefe("Garantieende in Kalendermonaten",
           any(f.ziel == "2025-02-28" for f in garantie))


def schritt_pruefen() -> None:
    """Genau ein nächster Schritt je Lage."""
    print("\nNächster Schritt")
    tag = "2026-01-20"
    pruefe("ohne Kaufdatum zuerst das Kaufdatum",
           naechster_schritt(fall(kaufdatum=None), tag).titel
           == "Kaufdatum nachtragen")
    schritt = naechster_schritt(fall(kaufdatum="2025-11-01"), "2025-12-01")
    pruefe("neu: Mängelanzeige, nicht dringend",
           schritt.titel == "Mängelanzeige senden" and not schritt.dringend)
    pruefe("Beweislast kippt bald: dringend",
           naechster_schritt(fall(), "2026-01-01").dringend)
    pruefe("abgelehnt: kontern",
           naechster_schritt(fall(status="abgelehnt"), tag).titel
           == "Ablehnung kontern")
    schritt = naechster_schritt(fall(status="gemeldet", frist="2026-02-01"),
                                tag)
    pruefe("Frist läuft: abwarten",
           schritt.titel == "Antwort abwarten" and "12 Tage" in schritt.warum)
    schritt = naechster_schritt(fall(status="gemeldet", frist="2026-01-10"),
                                tag)
    pruefe("Frist abgelaufen: Wandlung",
           schritt.titel == "Vertragsauflösung erklären"
           and "10.01.2026" in schritt.warum)
    pruefe("gemeldet ohne Frist: Frist setzen",
           naechster_schritt(fall(status="gemeldet"), tag).titel
           == "Frist setzen")
    pruefe("kein Schritt ohne Begründung",
           all(len(naechster_schritt(fall(status=s), tag).warum) > 20
               for s in ("neu", "gemeldet", "abgelehnt", "eskaliert",
                         "geloest", "aufgegeben")))


def ablehnungen_pruefen() -> None:
    """Die Stichwortsuche in der Händlerantwort."""
    print("\nAblehnungen")
    pruefe("erkennt den Garantie-Baustein",
           ablehnungen_erkennen("Leider ist die Garantie abgelaufen.")[0][0]
           .id == "garantie_abgelaufen")
    pruefe("Groß- und Kleinschreibung egal",
           ablehnungen_erkennen("KEIN GEWÄHRLEISTUNGSFALL")[0][0].id
           == "kein_fall")
    treffer = ablehnungen_erkennen(
        "Das ist normaler Verschleiß und kein Gewährleistungsfall, zudem "
        "Abnutzung. Bitte senden Sie Fotos.")
    pruefe("mehrere Bausteine, Hauptgrund oben",
           treffer[0][0].id == "kein_fall" and treffer[0][1] >= 2
           and any(a.id == "fotos" for a, _ in treffer))
    pruefe("harmloser Text ohne Treffer", ablehnungen_erkennen(
        "Wir haben Ihre Nachricht erhalten und senden Ersatz.") == [])
    pruefe("ablehnung_nach findet und fehlt sauber",
           ablehnung_nach("fotos").id == "fotos"
           and ablehnung_nach("gibt-es-nicht") is None)
    pruefe("zwölf eindeutige, vollständige Ablehnungen",
           len({a.id for a in ABLEHNUNGEN}) == len(ABLEHNUNGEN) == 12
           and all(a.norm["AT"] and a.norm["DE"] and len(a.absatz) > 80
                   for a in ABLEHNUNGEN))
    pruefe("jedes Muster findet seine eigene Ablehnung", all(
        any(a2.id == a.id for a2, _ in ablehnungen_erkennen(m))
        for a in ABLEHNUNGEN for m in a.muster))


def schreiben_pruefen() -> None:
    """Die vier Briefe."""
    print("\nSchreiben")
    voll = fall(bestellnummer="A-123", beschreibung="Linker Kanal fällt aus.",
                mangel_seit="2025-06-01", haendler_email="shop@example.com")
    text = schreiben_bauen(voll, "anzeige", heute_iso="2025-07-01").text
    pruefe("Mängelanzeige mit Sachverhalt, Norm und Frist",
           all(t in text for t in ("Linker Kanal", "A-123", "15.01.2025",
                                   "01.06.2025", "932 ABGB", "924 ABGB",
                                   "15.07.2025")))
    text = schreiben_bauen(voll, "anzeige", heute_iso="2026-07-01").text
    pruefe("nach 12 Monaten keine Beweislastvermutung mehr",
           "924 ABGB" not in text and "932 ABGB" in text)
    text = schreiben_bauen(voll, "anzeige", heute_iso="2027-07-01").text
    pruefe("nach 24 Monaten über § 933", "933 ABGB" in text)
    text = schreiben_bauen(fall(recht="DE"), "anzeige",
                           heute_iso="2025-07-01").text
    pruefe("DE zitiert deutsche Normen",
           "437 BGB" in text and "ABGB" not in text)
    text = schreiben_bauen(fall(frist="2025-07-15"), "nachfrist",
                           heute_iso="2025-07-20").text
    pruefe("Nachfrist nennt alte Frist, neue Frist und Preis",
           "15.07.2025" in text and "27.07.2025" in text and "199,00" in text)
    brief = schreiben_bauen(voll, "wandlung", heute_iso="2025-08-01")
    pruefe("Wandlung mit Norm, IBAN-Platzhalter und Bank-Lücke",
           "932 Abs 4 ABGB" in brief.text and "[IBAN]" in brief.text
           and "Bankverbindung für die Rückzahlung" in brief.luecken)
    brief = schreiben_bauen(voll, "ablehnung", ablehnung_id="hinhalten",
                            heute_iso="2025-08-01")
    pruefe("Antwort ersetzt [FRIST] durch das Datum",
           "[FRIST]" not in brief.text and "15.08.2025" in brief.text)
    brief = schreiben_bauen(Fall(), "anzeige", heute_iso="2025-08-01")
    pruefe("fehlende Angaben werden Lücken, nicht erfunden",
           "[MANGEL BESCHREIBEN]" in brief.text and len(brief.luecken) == 5)
    pruefe("kein Brief enthält None", all(
        "None" not in schreiben_bauen(f, art, heute_iso="2025-08-01").text
        for art in ("anzeige", "nachfrist", "wandlung", "ablehnung")
        for f in (voll, Fall(), fall(preis=None))))
    pruefe("naechstes_schreiben folgt dem Status",
           [naechstes_schreiben(fall(status=s)) for s in
            ("neu", "gemeldet", "abgelehnt", "eskaliert")]
           == ["anzeige", "nachfrist", "ablehnung", "wandlung"])
    gesendet = fall()
    brief = schreiben_bauen(gesendet, "anzeige", heute_iso="2025-08-01")
    als_gesendet_vermerken(gesendet, brief, "2025-08-15", "2025-08-01")
    pruefe("als gesendet: Frist, Status, zwei Einträge",
           gesendet.frist == "2025-08-15" and gesendet.status == "gemeldet"
           and len(gesendet.ereignisse) == 2)


def zeitstrahl_pruefen() -> None:
    """Die Rechnung hinter dem Balken."""
    print("\nZeitstrahl")
    strahl = strahl_bauen("2026-01-01", 24, "2026-04-01")
    pruefe("frisches Gerät: zwei Abschnitte, 24 Monate",
           strahl.gesamt == 24 and [a.id for a in strahl.abschnitte]
           == ["beweislast", "gewaehrleistung"] and strahl.monate == 3)
    strahl = strahl_bauen("2026-01-01", 60, "2026-04-01")
    pruefe("lange Garantie bekommt einen eigenen Abschnitt",
           strahl.gesamt == 60 and strahl.abschnitte[2].id == "garantie")
    strahl = strahl_bauen("2020-01-01", 24, "2026-01-01")
    pruefe("altes Gerät: Balken wächst mit, heute bleibt drin",
           strahl.gesamt == 73 and 0 < strahl.heute_prozent <= 99.6)
    for kauf, garantie, tag in (("2026-01-01", 24, "2026-06-01"),
                                ("2019-05-20", None, "2026-10-12"),
                                ("2026-01-01", 0, "2026-01-01")):
        strahl = strahl_bauen(kauf, garantie, tag)
        position = 0
        for abschnitt in strahl.abschnitte:
            assert abschnitt.start == position and abschnitt.breite > 0
            position += abschnitt.breite
        pruefe(f"Abschnitte lückenlos ({kauf})", position == strahl.gesamt)


def speicher_pruefen() -> None:
    """Lesen, Schreiben und Sicherung."""
    print("\nSpeicher und Sicherung")
    with tempfile.TemporaryDirectory() as ordner:
        datei = Path(ordner) / "test.json"
        pruefe("fehlende Datei ist eine leere Liste",
               liste_laden(datei) == [])
        liste_speichern(datei, [{"id": "a"}])
        pruefe("gespeicherte Liste kommt zurück",
               liste_laden(datei) == [{"id": "a"}])
        datei.write_text("{kaputt", encoding="utf-8")
        pruefe("kaputte Datei bringt die App nicht zum Absturz",
               liste_laden(datei) == [])
    faelle, geraete = demo_faelle(), demo_geraete()
    zurueck_f, zurueck_g, fehler = aus_json(als_json(faelle, geraete))
    pruefe("Sicherung lässt sich unverändert zurücklesen",
           fehler is None and zurueck_f == faelle and zurueck_g == geraete)
    pruefe("kaputtes JSON wird gemeldet",
           "JSON" in (aus_json("{nicht json")[2] or ""))
    pruefe("leere Sicherung wird gemeldet",
           aus_json('{"faelle": [], "geraete": []}')[2] is not None)


def demo_pruefen() -> None:
    """Die Beispieldaten bleiben gültig, egal wann man sie lädt."""
    print("\nDemo")
    faelle, geraete = demo_faelle(), demo_geraete()
    pruefe("fünf Fälle und fünf Geräte", len(faelle) == len(geraete) == 5)
    pruefe("jeder Zustand kommt vor",
           {"neu", "gemeldet", "abgelehnt", "eskaliert", "geloest"}
           <= {f.status for f in faelle})
    neu = next(f for f in faelle if f.status == "neu")
    pruefe("der frische Fall liegt in der Vermutungsfrist",
           lage_ermitteln(neu, plus_tage(neu.kaufdatum, 240))
           .beweislast_beim_haendler)
    pruefe("ein Gerät ohne Kaufdatum, eines mit langer Garantie",
           any(g.kaufdatum is None for g in geraete)
           and any((g.garantie_monate or 0) > 24 for g in geraete))
    erster_start_pruefen()


def erster_start_pruefen() -> None:
    """Beispieldaten nur, wenn es noch gar keine Daten gibt."""
    original = daten.FAELLE_DATEI, daten.GERAETE_DATEI
    with tempfile.TemporaryDirectory() as ordner:
        daten.FAELLE_DATEI = Path(ordner) / "faelle.json"
        daten.GERAETE_DATEI = Path(ordner) / "geraete.json"
        try:
            pruefe("erster Start legt Beispieldaten an",
                   beim_ersten_start_anlegen()
                   and len(daten.faelle_laden()) == 5)
            daten.fall_sichern(Fall(produkt="Eigener Fall"))
            demo_ausschalten()
            pruefe("Demo aus: nur der eigene Fall bleibt",
                   not demo_aktiv() and [f.produkt for f in
                                         daten.faelle_laden()]
                   == ["Eigener Fall"] and daten.geraete_laden() == [])
            pruefe("Demo bleibt beim nächsten Start aus",
                   not beim_ersten_start_anlegen())
            demo_einschalten()
            pruefe("Demo wieder an: Beispiele plus eigener Fall",
                   demo_aktiv() and len(daten.faelle_laden()) == 6)
        finally:
            daten.FAELLE_DATEI, daten.GERAETE_DATEI = original


def main() -> None:
    """Alle Prüfungen nacheinander."""
    for gruppe in (datum_pruefen, lage_pruefen, rechte_pruefen,
                   fristen_pruefen, schritt_pruefen, ablehnungen_pruefen,
                   schreiben_pruefen, zeitstrahl_pruefen, speicher_pruefen,
                   demo_pruefen):
        gruppe()
    print(f"\n{ANZAHL['ok']} Prüfungen bestanden.\n")


if __name__ == "__main__":
    main()
