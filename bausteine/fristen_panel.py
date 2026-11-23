"""Fristen und der eine nächste Schritt.

Der nächste Schritt steht oben und ist genau einer. Alles darunter ist der
Beleg dafür, warum er der nächste ist.
"""

from __future__ import annotations

import streamlit as st

from bausteine.gemeinsam import FRIST_TON, marke
from bausteine.zeitstrahl_anzeige import legende_zeigen, zeitstrahl_zeigen
from daten import Fall, datum_de
from recht.fristen import fristen_fuer, naechster_schritt, rest_text


def naechster_schritt_zeigen(fall: Fall, heute_iso: str) -> None:
    """Der Kasten mit dem nächsten Schritt; rot, wenn es dringend ist."""
    schritt = naechster_schritt(fall, heute_iso)
    text = f"**Nächster Schritt: {schritt.titel}**  \n{schritt.warum}"
    if schritt.dringend:
        st.error(text)
    else:
        st.info(text)


def fristen_zeigen(fall: Fall, heute_iso: str) -> None:
    """Die Karte „Fristen“ in der Akte."""
    with st.container(border=True):
        st.subheader("Fristen")
        naechster_schritt_zeigen(fall, heute_iso)
        if fall.kaufdatum:
            zeitstrahl_zeigen(fall.kaufdatum, fall.garantie_monate,
                              heute_iso)
            legende_zeigen()
        liste = fristen_fuer(fall, heute_iso)
        if not liste:
            st.caption("Noch keine Frist berechenbar — es fehlt das "
                       "Kaufdatum.")
        for frist in liste:
            links, rechts = st.columns([3, 1])
            links.markdown(f"**{frist.titel}**  \n{frist.bedeutung}")
            rechts.markdown(
                marke(rest_text(frist.tage_rest), FRIST_TON[frist.zustand])
                + f"  \n{datum_de(frist.ziel)}"
            )
