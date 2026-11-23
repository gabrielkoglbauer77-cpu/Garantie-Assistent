"""Der Verlauf — die Beweiskette des Falls.

Das Datum ist eingebbar und nicht der Zeitpunkt des Eintragens: Man trägt
ein Telefonat am Abend nach, es hat aber am Vormittag stattgefunden — und
vor Gericht zählt, wann es stattgefunden hat.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from bausteine.gemeinsam import marke
from daten import EREIGNIS_ARTEN, Ereignis, Fall, datum_de, fall_sichern

ART_TON = {"notiz": "neutral", "gesendet": "akzent", "erhalten": "warn",
           "frist": "gefahr", "status": "ok"}


def _eintragen(fall: Fall) -> None:
    with st.form(f"verlauf_neu_{fall.id}", clear_on_submit=True):
        links, mitte = st.columns(2)
        datum = links.date_input("Datum", date.today(), format="DD.MM.YYYY")
        art = mitte.selectbox("Art", list(EREIGNIS_ARTEN),
                              format_func=EREIGNIS_ARTEN.get)
        text = st.text_input("Was ist passiert?")
        if st.form_submit_button("Eintragen") and text.strip():
            fall.ereignisse.append(
                Ereignis(datum=datum.isoformat(), art=art, text=text.strip()))
            fall_sichern(fall)
            st.rerun()


def _eintrag_zeigen(fall: Fall, ereignis: Ereignis) -> None:
    links, rechts = st.columns([5, 1])
    links.markdown(
        f"{marke(EREIGNIS_ARTEN[ereignis.art], ART_TON[ereignis.art])} "
        f"{ereignis.text}  \n{datum_de(ereignis.datum)}")
    if rechts.button("Löschen", key=f"loeschen_{ereignis.id}"):
        fall.ereignisse = [e for e in fall.ereignisse
                           if e.id != ereignis.id]
        fall_sichern(fall)
        st.rerun()


def _aendern(fall: Fall, sortiert: list[Ereignis]) -> None:
    with st.expander("Eintrag ändern"):
        ereignis = st.selectbox(
            "Welcher Eintrag?", sortiert, key=f"wahl_{fall.id}",
            format_func=lambda e: f"{datum_de(e.datum)} · {e.text[:50]}")
        with st.form(f"verlauf_aendern_{fall.id}"):
            datum = st.date_input("Datum", date.fromisoformat(ereignis.datum),
                                  format="DD.MM.YYYY")
            text = st.text_input("Text", ereignis.text)
            if st.form_submit_button("Übernehmen") and text.strip():
                ereignis.datum = datum.isoformat()
                ereignis.text = text.strip()
                fall_sichern(fall)
                st.rerun()


def verlauf_zeigen(fall: Fall) -> None:
    """Die Karte „Verlauf“ in der Akte, das Neueste oben."""
    with st.container(border=True):
        st.subheader("Verlauf")
        st.caption("Jeder Kontakt mit Datum. Das ist später der Beleg dafür, "
                   "wann du was gefordert hast.")
        _eintragen(fall)
        sortiert = sorted(fall.ereignisse, key=lambda e: e.datum,
                          reverse=True)
        if not sortiert:
            st.caption("Noch kein Eintrag.")
            return
        for ereignis in sortiert:
            _eintrag_zeigen(fall, ereignis)
        _aendern(fall, sortiert)
