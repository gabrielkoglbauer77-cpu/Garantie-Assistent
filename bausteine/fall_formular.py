"""Die Stammdaten eines Falls.

Kaufdatum und Datum des Mangels stehen oben, weil aus ihnen die gesamte
Rechtslage folgt. Gespeichert wird als Ganzes über ein Formular, nicht bei
jedem Tastendruck: Ein halb eingetragener Fall soll nicht in der Liste
auftauchen.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import streamlit as st

from daten import RECHTSORDNUNGEN, Fall, fall_sichern


def als_datum(iso: str | None) -> date | None:
    """ISO-Text in ein ``date`` für die Datumsfelder."""
    return date.fromisoformat(iso) if iso else None


def als_iso(wert: date | None) -> str | None:
    """``date`` aus dem Datumsfeld zurück in ISO-Text."""
    return wert.isoformat() if wert else None


def _felder_oben(fall: Fall) -> dict:
    links, rechts = st.columns(2)
    # Streamlit verlangt einheitliche Zahlentypen: Preis immer als float.
    preis = float(fall.preis) if fall.preis is not None else None
    werte = {
        "produkt": links.text_input("Produkt", fall.produkt,
                                    placeholder="z. B. Kopfhörer XY"),
        "haendler": rechts.text_input("Händler", fall.haendler,
                                      placeholder="Wer hat verkauft?"),
        "kaufdatum": links.date_input(
            "Kaufdatum", als_datum(fall.kaufdatum), format="DD.MM.YYYY",
            help="Startpunkt aller Fristen."),
        "mangel_seit": rechts.date_input(
            "Mangel aufgetreten am", als_datum(fall.mangel_seit),
            format="DD.MM.YYYY", help="Maßgeblich für die Beweislast."),
        "preis": links.number_input(
            "Kaufpreis (€)", min_value=0.0, value=preis, step=1.0,
            format="%.2f"),
        "bestellnummer": rechts.text_input(
            "Bestell- oder Rechnungsnummer", fall.bestellnummer),
    }
    return werte


def _felder_unten(fall: Fall) -> dict:
    links, mitte, rechts = st.columns([2, 1, 1])
    codes = list(RECHTSORDNUNGEN)
    werte = {
        "haendler_email": links.text_input("E-Mail des Händlers",
                                           fall.haendler_email),
        "recht": mitte.selectbox("Recht", codes,
                                 index=codes.index(fall.recht),
                                 format_func=RECHTSORDNUNGEN.get),
        "garantie_monate": rechts.number_input(
            "Garantie (Monate)", min_value=0, value=fall.garantie_monate,
            step=1, help="Leer lassen, wenn keine zugesagt war."),
        "beschreibung": st.text_area(
            "Was ist defekt?", fall.beschreibung, height=100,
            help="So konkret wie möglich — dieser Text geht in die "
                 "Schreiben."),
    }
    return werte


def _bereinigen(werte: dict) -> dict:
    for feld in ("produkt", "haendler", "haendler_email", "bestellnummer",
                 "beschreibung"):
        werte[feld] = werte[feld].strip()
    werte["kaufdatum"] = als_iso(werte["kaufdatum"])
    werte["mangel_seit"] = als_iso(werte["mangel_seit"])
    if werte["garantie_monate"] is not None:
        werte["garantie_monate"] = int(werte["garantie_monate"])
    return werte


def fall_formular(fall: Fall, knopf: str = "Fall speichern") -> Fall | None:
    """Zeigt das Formular. Gibt den gespeicherten Fall zurück oder None."""
    with st.form(f"stammdaten_{fall.id}"):
        st.caption("Kaufdatum und Datum des Mangels entscheiden über die "
                   "Fristen und darüber, wer was beweisen muss.")
        werte = {**_felder_oben(fall), **_felder_unten(fall)}
        abgeschickt = st.form_submit_button(knopf, type="primary")
    if not abgeschickt:
        return None
    werte = _bereinigen(werte)
    if not werte["produkt"] and not werte["haendler"]:
        st.warning("Bitte mindestens Produkt oder Händler eintragen.")
        return None
    neu = replace(fall, **werte)
    fall_sichern(neu)
    return neu
