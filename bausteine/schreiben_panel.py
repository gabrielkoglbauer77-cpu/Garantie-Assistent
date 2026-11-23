"""Das Schreiben, das jetzt hinausgeht.

„Als gesendet vermerken“ ist der wichtigste Knopf der App: Er schreibt die
Frist in den Fall und legt zwei Einträge im Verlauf an. Erst damit lässt
sich später belegen, wann was gefordert wurde.
"""

from __future__ import annotations

from urllib.parse import quote

import streamlit as st

from daten import Fall, datum_de, fall_sichern, heute, plus_tage
from recht.schreiben import (ARTEN, Schreiben, als_gesendet_vermerken,
                             naechstes_schreiben, schreiben_bauen)


def _mailto(fall: Fall, schreiben: Schreiben) -> str:
    return (f"mailto:{quote(fall.haendler_email)}"
            f"?subject={quote(schreiben.betreff)}"
            f"&body={quote(schreiben.text)}")


def _auswahl(fall: Fall) -> tuple[str, int]:
    """Welcher Brief, mit wie vielen Tagen Frist."""
    schluessel = f"art_{fall.id}"
    if schluessel not in st.session_state:
        st.session_state[schluessel] = naechstes_schreiben(fall)
    art = st.radio("Welches Schreiben?", list(ARTEN), key=schluessel,
                   format_func=ARTEN.get, horizontal=True)
    tage = st.number_input("Frist in Tagen", min_value=1, max_value=60,
                           value=14, key=f"tage_{fall.id}")
    frist = plus_tage(heute(), int(tage))
    hinweis = f"Ergibt den {datum_de(frist)}."
    if tage < 7:
        hinweis += " Unter sieben Tagen gilt eine Frist leicht als " \
                   "unangemessen."
    st.caption(hinweis)
    return art, int(tage)


def _knoepfe(fall: Fall, schreiben: Schreiben, frist: str) -> None:
    links, mitte, rechts = st.columns(3)
    if links.button("Als gesendet vermerken", type="primary",
                    key=f"gesendet_{fall.id}"):
        als_gesendet_vermerken(fall, schreiben, frist, heute())
        fall_sichern(fall)
        st.rerun()
    mitte.download_button(
        "Als Textdatei", f"{schreiben.betreff}\n\n{schreiben.text}",
        file_name=f"{schreiben.art}.txt", key=f"download_{fall.id}")
    if fall.haendler_email:
        rechts.link_button("Im Mailprogramm öffnen",
                           _mailto(fall, schreiben))
    else:
        rechts.caption("E-Mail des Händlers fehlt")


def schreiben_zeigen(fall: Fall) -> None:
    """Die Karte „Schreiben“ in der Akte."""
    with st.container(border=True):
        st.subheader("Schreiben")
        art, tage = _auswahl(fall)
        schreiben = schreiben_bauen(
            fall, art, frist_tage=tage,
            ablehnung_id=st.session_state.get(f"ablehnung_{fall.id}"))
        st.caption(schreiben.wann)
        if schreiben.luecken:
            st.warning("**Noch einzusetzen:** "
                       + " · ".join(schreiben.luecken))
        st.markdown(f"**Betreff:** {schreiben.betreff}")
        st.code(schreiben.text, language=None, wrap_lines=True)
        _knoepfe(fall, schreiben, plus_tage(heute(), tage))
        st.caption("Bei Beträgen, die wehtun, per Einschreiben: Der Zugang "
                   "ist dann belegt, und auf den Zugang kommt es an.")
