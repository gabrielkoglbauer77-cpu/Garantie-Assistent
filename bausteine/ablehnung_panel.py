"""Die Antwort des Händlers einordnen und kontern.

Der Text wird eingefügt, die Stichwortsuche findet die
Standardablehnungen, und zu jeder steht da, was rechtlich dagegen spricht.
Was die Suche nicht findet, lässt sich aus der vollständigen Liste von Hand
wählen.
"""

from __future__ import annotations

import streamlit as st

from daten import Fall, fall_finden, fall_sichern
from recht.ablehnungen import ABLEHNUNGEN, Ablehnung, ablehnungen_erkennen


def absatz_uebernehmen(fall_id: str, ablehnung_id: str) -> None:
    """Callback: wechselt im Schreiben auf die Antwort zu dieser Ablehnung.

    Läuft als ``on_click``, weil er das Auswahlfeld des Schreibens ändert —
    das geht nur, bevor es neu gezeichnet wird.
    """
    st.session_state[f"art_{fall_id}"] = "ablehnung"
    st.session_state[f"ablehnung_{fall_id}"] = ablehnung_id
    fall = fall_finden(fall_id)
    if fall and fall.status in ("neu", "gemeldet"):
        fall.status = "abgelehnt"
        fall_sichern(fall)


def _ablehnung_zeigen(fall: Fall, ablehnung: Ablehnung,
                      erkannt: bool) -> None:
    titel = ablehnung.label + ("  — erkannt" if erkannt else "")
    with st.expander(titel, expanded=erkannt):
        st.markdown(f"**Behauptung:** {ablehnung.behauptung}")
        st.markdown(f"**Was dagegen steht:** {ablehnung.entgegnung}")
        st.markdown(f"**Norm:** :blue[{ablehnung.norm[fall.recht]}]")
        beweise = "\n".join(f"- {b}" for b in ablehnung.beweis)
        st.markdown(f"**Was die Sache entscheidet:**\n{beweise}")
        st.markdown("**Absatz für die Antwort** (Kopieren-Symbol rechts "
                    "oben):")
        st.code(ablehnung.absatz, language=None, wrap_lines=True)
        st.button("In Antwortschreiben übernehmen",
                  key=f"uebernehmen_{fall.id}_{ablehnung.id}",
                  on_click=absatz_uebernehmen,
                  args=(fall.id, ablehnung.id))
        st.caption(f"Wenn er dabei bleibt: {ablehnung.danach}")


def ablehnung_zeigen(fall: Fall) -> None:
    """Die Karte „Ablehnung kontern“ in der Akte."""
    with st.container(border=True):
        st.subheader("Ablehnung kontern")
        text = st.text_area(
            "Antwort des Händlers einfügen",
            key=f"antwort_{fall.id}", height=110,
            placeholder="„Leider handelt es sich hier um normalen "
                        "Verschleiß, zudem ist die Garantie bereits "
                        "abgelaufen …“")
        treffer = ablehnungen_erkennen(text) if text.strip() else []
        alle = st.toggle(f"Alle {len(ABLEHNUNGEN)} Ablehnungen zeigen",
                         key=f"alle_{fall.id}")
        if text.strip():
            st.caption(f"{len(treffer)} Baustein(e) erkannt." if treffer
                       else "Kein bekannter Baustein erkannt — unten "
                            "stehen alle Ablehnungsarten zur Auswahl.")
        erkannte = [ablehnung for ablehnung, _ in treffer]
        gezeigt = ABLEHNUNGEN if alle or not erkannte else erkannte
        for ablehnung in gezeigt:
            _ablehnung_zeigen(fall, ablehnung, ablehnung in erkannte)
