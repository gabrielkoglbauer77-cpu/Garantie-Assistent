"""Garantie-Assistent — Einstiegspunkt der App.

Starten mit:

    streamlit run app.py

Diese Datei baut nur den Rahmen: Seitenleiste mit Navigation und den
Hinweis, wo die Daten liegen. Was auf den Seiten steht, entscheiden die
Module im Ordner ``seiten``.
"""

import streamlit as st

from bausteine.gemeinsam import meldung_merken, zur_liste
from demo import (beim_ersten_start_anlegen, demo_aktiv, demo_ausschalten,
                  demo_einschalten)
from seiten.akte import akte_seite
from seiten.faelle import faelle_seite
from seiten.geraete import geraete_seite
from seiten.wissen import wissen_seite

SEITEN = {
    "Fälle": faelle_seite,
    "Geräte": geraete_seite,
    "Rechtslage": wissen_seite,
}


def demo_umschalten() -> None:
    """Callback des Demo-Schalters: Demo-Einträge hinzufügen oder entfernen."""
    if st.session_state["demo_an"]:
        demo_einschalten()
        meldung_merken("Demo eingeschaltet: 5 Fälle und 5 Geräte.")
    else:
        demo_ausschalten()
        meldung_merken("Demo ausgeschaltet. Deine eigenen Fälle und Geräte "
                       "bleiben erhalten.")
    zur_liste()


def seitenleiste() -> None:
    """Navigation und Hinweise in der Seitenleiste."""
    with st.sidebar:
        st.title("🛡️ Garantie-Assistent")
        st.radio("Bereich", list(SEITEN), key="seite", on_change=zur_liste)
        # Vor dem Zeichnen auf den gespeicherten Stand setzen.
        st.session_state["demo_an"] = demo_aktiv()
        st.toggle("Demo-Daten", key="demo_an", on_change=demo_umschalten,
                  help="Fünf Beispielfälle und fünf Beispielgeräte. "
                       "Ausschalten entfernt nur diese, eigene Einträge "
                       "bleiben.")
        st.caption(
            "Gewährleistung und Garantie durchsetzen: Fristen rechnen, "
            "Rechte benennen, Ablehnungen kontern, Schreiben erzeugen."
        )
        st.divider()
        st.caption(
            "Orientierung, keine Rechtsberatung. Alle Daten liegen lokal im "
            "Ordner `daten`. Für Österreich (ABGB, KSchG) und Deutschland "
            "(BGB)."
        )


def main() -> None:
    """Rahmen zeichnen und die gewählte Seite anzeigen."""
    st.set_page_config(page_title="Garantie-Assistent", page_icon="🛡️",
                       layout="wide")
    st.session_state.setdefault("seite", "Fälle")
    st.session_state.setdefault("fall_id", None)
    if beim_ersten_start_anlegen():
        meldung_merken("Demo eingeschaltet: 5 Fälle und 5 Geräte. Links "
                       "unter „Demo-Daten“ lässt sie sich abschalten.")
    seitenleiste()
    fall_id = st.session_state["fall_id"]
    if st.session_state["seite"] == "Fälle" and fall_id:
        akte_seite(fall_id)
    else:
        SEITEN[st.session_state["seite"]]()


if __name__ == "__main__":
    main()
