"""Kleine Bausteine, die mehrere Seiten brauchen: Marken und Navigation.

Navigation in Streamlit: Die gewählte Seite steht in
``st.session_state["seite"]``, der geöffnete Fall in
``st.session_state["fall_id"]``. Weil "seite" zugleich der Schlüssel des
Auswahlfelds in der Seitenleiste ist, darf sie nur in einem Callback
(``on_click``) geändert werden — also bevor das Feld neu gezeichnet wird.
"""

from __future__ import annotations

import streamlit as st

# Ton ist eine Bedeutung, keine Farbe: "gefahr" heißt, dass etwas
# verloren geht.
FARBE = {
    "neutral": "gray",
    "ok": "green",
    "warn": "orange",
    "gefahr": "red",
    "akzent": "blue",
}

STATUS_TON = {
    "neu": "akzent",
    "gemeldet": "akzent",
    "abgelehnt": "gefahr",
    "eskaliert": "warn",
    "geloest": "ok",
    "aufgegeben": "neutral",
}

FRIST_TON = {
    "offen": "neutral",
    "knapp": "warn",
    "heute": "warn",
    "ueberschritten": "gefahr",
}


def marke(text: str, ton: str = "neutral") -> str:
    """Farbiger Text für Markdown, z. B. ``:green[**Gelöst**]``."""
    sauber = text.replace("[", "(").replace("]", ")")
    return f":{FARBE[ton]}[**{sauber}**]"


def fall_oeffnen(fall_id: str) -> None:
    """Callback: zur Akte eines Falls wechseln."""
    st.session_state["seite"] = "Fälle"
    st.session_state["fall_id"] = fall_id


def zur_liste() -> None:
    """Callback: zurück zur Fallliste."""
    st.session_state["fall_id"] = None


def meldung_merken(text: str) -> None:
    """Merkt eine Meldung, die nach dem Neuladen einmal angezeigt wird."""
    st.session_state["meldung"] = text


def meldung_zeigen() -> None:
    """Zeigt eine gemerkte Meldung einmal an."""
    text = st.session_state.pop("meldung", None)
    if text:
        st.success(text)
