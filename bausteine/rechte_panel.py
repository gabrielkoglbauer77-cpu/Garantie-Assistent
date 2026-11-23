"""Welche Rechte der Fall hergibt — jedes mit der Norm, aus der es folgt.

Nicht verfügbare Rechte werden gezeigt, nicht ausgeblendet: Zu wissen,
dass die Beweislastvermutung in drei Wochen endet, ist mehr wert als eine
aufgeräumte Liste.
"""

from __future__ import annotations

import streamlit as st

from bausteine.gemeinsam import marke
from daten import Fall
from recht.gewaehrleistung import Recht, lage_ermitteln


def _recht_zeigen(recht: Recht) -> None:
    with st.container(border=True):
        status = marke("verfügbar", "ok") if recht.verfuegbar else marke(
            "derzeit nicht", "neutral")
        st.markdown(f"**{recht.titel}** · {status}")
        st.markdown(f":blue[{recht.norm}]")
        st.caption(recht.erklaerung)
        if recht.hinweis:
            st.caption(f"⚠️ {recht.hinweis}")


def rechte_zeigen(fall: Fall, heute_iso: str) -> None:
    """Die Karte „Deine Rechte“ in der Akte."""
    lage = lage_ermitteln(fall, heute_iso)
    with st.container(border=True):
        st.subheader("Deine Rechte")
        st.caption(lage.kernsatz)
        for recht in lage.rechte:
            _recht_zeigen(recht)
        fallen = "\n".join(f"- {text}" for text in lage.fallen)
        st.warning(f"**Worauf Händler setzen**\n\n{fallen}")
