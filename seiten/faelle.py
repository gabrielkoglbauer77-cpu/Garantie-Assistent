"""Die Fallliste.

Sortiert wird nach Dringlichkeit, nicht nach Anlagedatum: Fälle mit
abgelaufener Frist zuerst. Offener Betrag und nächster Schritt stehen in
der Zeile, damit man die Liste lesen kann, ohne jeden Fall zu öffnen.
"""

from __future__ import annotations

import streamlit as st

from bausteine.fall_formular import fall_formular
from bausteine.gemeinsam import (STATUS_TON, fall_oeffnen, marke,
                                 meldung_merken, meldung_zeigen)
from daten import (STATUS_TEXT, Fall, alles_ersetzen, als_json, aus_json,
                   euro, faelle_laden, geraete_laden, heute)
from recht.fristen import fristen_fuer, naechster_schritt, rest_text
from recht.gewaehrleistung import frist_text, lage_ermitteln


def dringlichkeit(fall: Fall, heute_iso: str) -> int:
    """Kleinste Restlaufzeit in Tagen; ohne Frist ganz nach hinten."""
    fristen = fristen_fuer(fall, heute_iso)
    return min((f.tage_rest for f in fristen), default=9999)


def sortieren(faelle: list[Fall], heute_iso: str) -> list[Fall]:
    """Offene Fälle nach Dringlichkeit, erledigte ans Ende."""
    offen = [f for f in faelle if not f.erledigt]
    zu = [f for f in faelle if f.erledigt]
    offen.sort(key=lambda f: dringlichkeit(f, heute_iso))
    return offen + zu


def _marken(fall: Fall, heute_iso: str) -> str:
    teile = [marke(STATUS_TEXT[fall.status], STATUS_TON[fall.status])]
    if fall.erledigt:
        return " ".join(teile)
    lage = lage_ermitteln(fall, heute_iso)
    teile.append(marke(frist_text(lage),
                       "neutral" if lage.in_frist else "gefahr"))
    # Die eigene Frist an den Händler, sonst die nächste bevorstehende.
    fristen = fristen_fuer(fall, heute_iso)
    naechste = next((f for f in fristen if f.art == "haendler"), None) or \
        next((f for f in fristen if 0 <= f.tage_rest <= 30), None)
    if naechste:
        ton = "gefahr" if naechste.tage_rest < 0 else "warn"
        teile.append(marke(f"{naechste.titel}: "
                           f"{rest_text(naechste.tage_rest)}", ton))
    return " ".join(teile)


def _zeile(fall: Fall, heute_iso: str) -> None:
    with st.container(border=True):
        links, rechts = st.columns([5, 1])
        links.markdown(f"#### {fall.produkt or 'Ohne Produktnamen'}")
        links.markdown(_marken(fall, heute_iso))
        haendler = fall.haendler or "Händler fehlt"
        nummer = f" · {fall.bestellnummer}" if fall.bestellnummer else ""
        links.caption(f"{haendler}{nummer} · {euro(fall.preis)}")
        if not fall.erledigt:
            schritt = naechster_schritt(fall, heute_iso)
            ton = "gefahr" if schritt.dringend else "akzent"
            links.markdown(f"{marke(schritt.titel, ton)} — {schritt.warum}")
        rechts.button("Öffnen", key=f"oeffnen_{fall.id}",
                      on_click=fall_oeffnen, args=(fall.id,))


def _neuer_fall(offen: bool) -> None:
    """Formular für einen neuen Fall, immer erreichbar.

    Der Entwurf liegt in ``st.session_state``, damit er zwischen zwei
    Durchläufen dieselbe Kennung behält. Sonst bekäme das Formular nach dem
    Klick auf „Fall anlegen“ eine neue Kennung — Streamlit hielte es für
    ein anderes Formular, und die Eingaben gingen verloren.
    """
    entwurf = st.session_state.setdefault("neuer_fall_entwurf", Fall())
    with st.expander("➕ Neuen Fall anlegen", expanded=offen):
        gespeichert = fall_formular(entwurf, knopf="Fall anlegen")
    if gespeichert:
        del st.session_state["neuer_fall_entwurf"]
        st.session_state["fall_id"] = gespeichert.id
        st.rerun()


def _leer() -> None:
    st.info(
        "Noch kein Fall angelegt. Die häufigste Antwort auf eine "
        "Reklamation ist kein Rechtsstandpunkt, sondern ein Textbaustein: "
        "„Die Garantie ist abgelaufen“, „Bitte senden Sie Fotos“. Diese App "
        "rechnet die Fristen, benennt die Rechte mit der Norm und erzeugt "
        "das passende Schreiben. Leg oben deinen ersten Fall an oder "
        "schalte links die Demo ein."
    )


def _einlesen() -> None:
    datei = st.file_uploader("Sicherung einlesen (JSON)", type=["json"],
                             key="sicherung")
    if datei and st.button("Sicherung übernehmen"):
        faelle, geraete, fehler = aus_json(datei.getvalue().decode("utf-8"))
        if fehler:
            st.error(fehler)
            return
        alles_ersetzen(faelle, geraete)
        meldung_merken(f"{len(faelle)} Fälle und {len(geraete)} Geräte "
                       "übernommen.")
        st.rerun()


def _verwalten(faelle: list[Fall]) -> None:
    with st.expander("Daten verwalten"):
        ersetzen = st.checkbox("Ich weiß, dass Löschen alle Fälle und Geräte "
                               "entfernt.")
        links, rechts = st.columns(2)
        links.download_button(
            "Sichern (JSON)", als_json(faelle, geraete_laden()),
            file_name=f"garantie-faelle-{heute()}.json",
            disabled=not faelle)
        if rechts.button("Alle Daten löschen", disabled=not ersetzen):
            alles_ersetzen([], [])
            meldung_merken("Alle Daten gelöscht.")
            st.rerun()
        _einlesen()


def faelle_seite() -> None:
    """Die Startseite: alle Fälle nach Dringlichkeit."""
    tag = heute()
    faelle = faelle_laden()
    offen = [f for f in faelle if not f.erledigt]
    summe = sum(f.preis or 0 for f in offen)
    st.title("Gewährleistung durchsetzen")
    st.caption(f"{len(offen)} offen · {euro(summe)} im Streit"
               if faelle else "Noch kein Fall angelegt.")
    meldung_zeigen()
    _neuer_fall(offen=not faelle)
    if not faelle:
        _leer()
    for fall in sortieren(faelle, tag):
        _zeile(fall, tag)
    _verwalten(faelle)
