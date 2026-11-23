"""Die vier Schreiben eines Gewährleistungsfalls, aus den Falldaten gebaut.

Bewusst ohne Sprachmodell: Diese Briefe sind Formulare — Anrede, Bezug,
Sachverhalt, Anspruch mit Norm, Frist mit Datum, Grußformel. Was in den
Falldaten fehlt, bleibt als [PLATZHALTER] sichtbar statt erfunden: Eine
Lücke im Brief ist reparierbar, eine erfundene Tatsache nicht.
"""

from __future__ import annotations

from dataclasses import dataclass

from daten import Ereignis, Fall, datum_de, euro, heute, plus_tage
from recht.ablehnungen import ablehnung_nach
from recht.gewaehrleistung import lage_ermitteln

ARTEN = {
    "anzeige": "Mängelanzeige",
    "ablehnung": "Antwort auf Ablehnung",
    "nachfrist": "Letzte Nachfrist",
    "wandlung": "Vertragsauflösung",
}


@dataclass
class Schreiben:
    """Ein fertiger Brief samt Betreff und fehlenden Angaben."""

    art: str
    titel: str
    wann: str
    betreff: str
    text: str
    luecken: list[str]


def _kopf(fall: Fall) -> list[str]:
    bezug = "ich beziehe mich auf meinen Kauf"
    if fall.bestellnummer:
        bezug += f" mit der Bestellnummer {fall.bestellnummer}"
    if fall.kaufdatum:
        bezug += f" vom {datum_de(fall.kaufdatum)}"
    if fall.produkt:
        bezug += f" ({fall.produkt})"
    return ["Sehr geehrte Damen und Herren,", "", bezug + ".", ""]


def _fuss() -> list[str]:
    return ["", "Mit freundlichen Grüßen", "[NAME]"]


def _luecken(fall: Fall) -> list[str]:
    luecken = []
    if not fall.haendler:
        luecken.append("Name des Händlers")
    if not fall.kaufdatum:
        luecken.append("Kaufdatum")
    if not fall.bestellnummer:
        luecken.append("Bestell- oder Rechnungsnummer")
    if not fall.beschreibung:
        luecken.append("Beschreibung des Mangels")
    luecken.append("eigener Name und Anschrift")
    return luecken


def _betreff(titel: str, fall: Fall) -> str:
    if fall.bestellnummer:
        return f"{titel} — Bestellung {fall.bestellnummer}"
    return titel


def _zusammensetzen(zeilen: list[str | None]) -> str:
    """Fügt Zeilen zusammen; ``None`` fällt weg, doppelte Leerzeilen auch."""
    ergebnis: list[str] = []
    for zeile in zeilen:
        if zeile is None:
            continue
        if zeile == "" and ergebnis and ergebnis[-1] == "":
            continue
        ergebnis.append(zeile)
    return "\n".join(ergebnis).strip()


def _anzeige(fall: Fall, frist: str, heute_iso: str) -> list[str | None]:
    lage = lage_ermitteln(fall, heute_iso)
    norm = "§ 924 ABGB" if fall.recht == "AT" else "§ 477 BGB"
    beweislast = None
    if lage.beweislast_beim_haendler:
        beweislast = (
            "Da sich der Mangel innerhalb der ersten zwölf Monate nach "
            "Übergabe gezeigt hat, wird vermutet, dass er bereits bei der "
            f"Übergabe vorlag ({norm}). Der Beweis des Gegenteils obliegt "
            "Ihnen."
        )
    seit = None
    if fall.mangel_seit:
        seit = f"Aufgetreten ist der Mangel am {datum_de(fall.mangel_seit)}."
    return [
        *_kopf(fall),
        "An der gelieferten Ware zeigt sich folgender Mangel:", "",
        fall.beschreibung or "[MANGEL BESCHREIBEN]", seit, "",
        lage.kernsatz, beweislast, "",
        f"Ich fordere Sie auf, den Mangel bis zum {datum_de(frist)} "
        "kostenlos zu beheben oder die Ware auszutauschen. Die Wahl zwischen "
        "Verbesserung und Austausch steht mir zu; sämtliche damit "
        "verbundenen Kosten tragen Sie.", "",
        "Nach fruchtlosem Ablauf dieser Frist werde ich ohne weitere "
        "Ankündigung Preisminderung geltend machen bzw. die "
        "Vertragsauflösung erklären.",
        *_fuss(),
    ]


def _nachfrist(fall: Fall, frist: str) -> list[str | None]:
    alte = f" mit Frist bis zum {datum_de(fall.frist)}" if fall.frist else ""
    preis = f" von {euro(fall.preis)}" if fall.preis else ""
    return [
        *_kopf(fall),
        f"meine Mängelanzeige{alte} ist ohne ausreichende Reaktion "
        "geblieben.", "",
        f"Ich setze Ihnen hiermit eine letzte Nachfrist bis zum "
        f"{datum_de(frist)}.", "",
        "Nach fruchtlosem Ablauf werde ich ohne weitere Ankündigung",
        "— den Kaufpreis angemessen mindern oder",
        f"— die Vertragsauflösung erklären und den vollen Kaufpreis{preis} "
        "zurückfordern,", "",
        "sowie die mir entstandenen Kosten der Rechtsverfolgung geltend "
        "machen.",
        *_fuss(),
    ]


def _wandlung(fall: Fall, frist: str) -> list[str | None]:
    norm = "§ 932 Abs 4 ABGB" if fall.recht == "AT" else (
        "§§ 437 Nr. 2, 323 BGB")
    preis = f" in Höhe von {euro(fall.preis)}" if fall.preis else ""
    return [
        *_kopf(fall),
        "die von mir gesetzte Frist ist fruchtlos verstrichen. Der Mangel "
        "wurde weder behoben noch wurde die Ware ausgetauscht.", "",
        f"Ich erkläre hiermit die Auflösung des Kaufvertrages ({norm}).", "",
        f"Ich fordere Sie auf, mir den Kaufpreis{preis} bis zum "
        f"{datum_de(frist)} auf folgendes Konto zu überweisen:",
        "[IBAN]", "",
        "Die Ware halte ich zur Abholung bereit bzw. sende sie auf Ihre "
        "Kosten zurück. Eine Erstattung in Form eines Gutscheins stellt "
        "keine Erfüllung dar.", "",
        "Zusätzlich mache ich die mir entstandenen Kosten geltend (Porto, "
        "Einschreiben, Fahrtkosten).",
        *_fuss(),
    ]


def _antwort(fall: Fall, frist: str, ablehnung_id: str | None,
             heute_iso: str) -> list[str | None]:
    ablehnung = ablehnung_nach(ablehnung_id)
    if ablehnung:
        absatz = ablehnung.absatz.replace("[FRIST]", datum_de(frist))
        grundlage = f"Rechtsgrundlage: {ablehnung.norm[fall.recht]}."
    else:
        absatz = lage_ermitteln(fall, heute_iso).kernsatz
        grundlage = None
    return [
        *_kopf(fall),
        "Ihre Antwort kann ich nicht akzeptieren.", "",
        absatz, "", grundlage, "",
        f"Ich fordere Sie auf, bis zum {datum_de(frist)} Abhilfe zu "
        "schaffen.",
        *_fuss(),
    ]


WANN = {
    "anzeige": "Zuerst — sie setzt die Frist in Gang, an die alles Weitere "
               "anknüpft.",
    "nachfrist": "Wenn die erste Frist verstrichen ist — sie schafft die "
                 "Voraussetzung für Preisminderung und Wandlung.",
    "wandlung": "Nach fruchtloser Nachfrist oder gescheiterter Reparatur — "
                "wirkt mit Zugang, auch ohne Zustimmung.",
    "ablehnung": "Sobald der Händler ablehnt — unbeantwortet wird aus der "
                 "Ablehnung ein Ergebnis.",
}


def _titel(art: str, ablehnung_id: str | None) -> str:
    if art == "ablehnung":
        ablehnung = ablehnung_nach(ablehnung_id)
        if ablehnung:
            return f"Antwort auf: {ablehnung.label}"
        return "Antwort auf die Ablehnung"
    return {"anzeige": "Mängelanzeige", "nachfrist": "Letzte Nachfrist",
            "wandlung": "Vertragsauflösung erklären"}[art]


def schreiben_bauen(fall: Fall, art: str, frist_tage: int | None = None,
                    ablehnung_id: str | None = None,
                    heute_iso: str | None = None) -> Schreiben:
    """Baut eines der vier Schreiben.

    Die Standardfrist sind 14 Tage, bei der letzten Nachfrist 7 — dann ist
    bereits eine Frist verstrichen.
    """
    heute_iso = heute_iso or heute()
    if frist_tage is None:
        frist_tage = 7 if art == "nachfrist" else 14
    frist = plus_tage(heute_iso, frist_tage)
    zeilen = {
        "anzeige": lambda: _anzeige(fall, frist, heute_iso),
        "nachfrist": lambda: _nachfrist(fall, frist),
        "wandlung": lambda: _wandlung(fall, frist),
        "ablehnung": lambda: _antwort(fall, frist, ablehnung_id, heute_iso),
    }[art]()
    luecken = _luecken(fall)
    if art == "wandlung":
        luecken.append("Bankverbindung für die Rückzahlung")
    titel = _titel(art, ablehnung_id)
    betreff_titel = {"anzeige": "Mängelanzeige",
                     "nachfrist": "Letzte Nachfrist",
                     "wandlung": "Vertragsauflösung",
                     "ablehnung": "Ihre Ablehnung"}[art]
    return Schreiben(art=art, titel=titel, wann=WANN[art],
                     betreff=_betreff(betreff_titel, fall),
                     text=_zusammensetzen(zeilen), luecken=luecken)


def naechstes_schreiben(fall: Fall) -> str:
    """Welches Schreiben nach dem aktuellen Stand an der Reihe ist."""
    return {"abgelehnt": "ablehnung", "eskaliert": "wandlung",
            "gemeldet": "nachfrist"}.get(fall.status, "anzeige")


def als_gesendet_vermerken(fall: Fall, schreiben: Schreiben, frist: str,
                           heute_iso: str) -> None:
    """Trägt ein gesendetes Schreiben in den Fall ein.

    Drei Dinge in einem Schritt: Die Frist kommt in den Fall, der Status
    zieht nach, und im Verlauf stehen zwei Einträge mit Datum — das
    gesendete Schreiben und die gesetzte Frist. Genau diese zwei Einträge
    sind später der Nachweis.
    """
    fall.status = "gemeldet" if schreiben.art == "anzeige" else "eskaliert"
    fall.frist = frist
    empfaenger = fall.haendler or "den Händler"
    fall.ereignisse.append(Ereignis(
        datum=heute_iso, art="gesendet",
        text=f"{schreiben.titel} an {empfaenger}"))
    fall.ereignisse.append(Ereignis(
        datum=heute_iso, art="frist",
        text=f"Frist gesetzt bis {datum_de(frist)}"))
