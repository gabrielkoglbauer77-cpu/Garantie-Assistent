"""Der farbige Balken — die Rechtslage eines Geräts in einem Bild.

    grün     Monat 0–12   der Händler muss beweisen
    blau     Monat 12–24  du musst beweisen
    violett  danach       nur noch die Herstellergarantie
    grau     danach       keine Ansprüche auf dem Regelweg

Gerechnet wird in ``zeitstrahl.py``, hier wird nur gezeichnet.
"""

from __future__ import annotations

import streamlit as st

from daten import datum_de
from zeitstrahl import strahl_bauen

FARBE = {
    "beweislast": "#2e9d5b",
    "gewaehrleistung": "#4263eb",
    "garantie": "#9c36b5",
    "vorbei": "#ced4da",
}

LEGENDE = [
    ("#2e9d5b", "0–12 Monate: Händler muss beweisen"),
    ("#4263eb", "12–24 Monate: du musst beweisen"),
    ("#9c36b5", "Herstellergarantie"),
    ("#ced4da", "keine Ansprüche auf dem Regelweg"),
    ("#212529", "heute"),
]


def _prozent(monate: float, gesamt: int) -> str:
    return f"{monate / gesamt * 100:.2f}%"


def _balken_html(strahl) -> str:
    teile = []
    for abschnitt in strahl.abschnitte:
        links = _prozent(abschnitt.start, strahl.gesamt)
        breite = _prozent(abschnitt.breite, strahl.gesamt)
        teile.append(
            f'<div title="{abschnitt.titel}" style="position:absolute;'
            f"top:0;height:100%;left:{links};width:{breite};"
            f'background:{FARBE[abschnitt.id]};opacity:.85"></div>'
        )
    if strahl.garantie > 0:
        teile.append(
            '<div style="position:absolute;bottom:0;left:0;height:6px;'
            f"width:{_prozent(strahl.garantie, strahl.gesamt)};"
            'background:#9c36b5"></div>'
        )
    teile.append(
        '<div title="heute" style="position:absolute;top:0;height:100%;'
        f'width:3px;left:{strahl.heute_prozent:.2f}%;background:#212529">'
        "</div>"
    )
    return (
        '<div style="position:relative;height:26px;border-radius:8px;'
        'overflow:hidden;border:1px solid #dee2e6">' + "".join(teile)
        + "</div>"
    )


def zeitstrahl_zeigen(kaufdatum: str | None, garantie_monate: int | None,
                      heute_iso: str) -> None:
    """Zeichnet den Balken samt Beschriftung."""
    if not kaufdatum:
        st.caption("Ohne Kaufdatum lässt sich nichts einzeichnen.")
        return
    strahl = strahl_bauen(kaufdatum, garantie_monate, heute_iso)
    st.markdown(_balken_html(strahl), unsafe_allow_html=True)
    st.caption(
        f"Kauf am {datum_de(kaufdatum)} · heute Monat {strahl.monate} · "
        f"Balken zeigt {strahl.gesamt} Monate"
    )


def legende_zeigen() -> None:
    """Die Legende — einmal pro Seite, nicht pro Gerät."""
    punkte = "".join(
        f'<span style="margin-right:16px;white-space:nowrap">'
        f'<span style="display:inline-block;width:10px;height:10px;'
        f'border-radius:2px;background:{farbe};margin-right:5px"></span>'
        f"{text}</span>"
        for farbe, text in LEGENDE
    )
    st.markdown(f'<div style="font-size:.8rem">{punkte}</div>',
                unsafe_allow_html=True)
