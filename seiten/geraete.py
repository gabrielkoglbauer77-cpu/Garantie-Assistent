"""Die Geräteliste — der vorbeugende Teil der App.

Wer seine Käufe einträgt, während noch alles funktioniert, hat das
Kaufdatum zur Hand, wenn es darauf ankommt. Sortiert wird nach
verbleibender Gewährleistung: Was zuerst abläuft, steht oben. Geräte ohne
Kaufdatum stehen ganz oben — diese Lücke will man schließen.
"""

from __future__ import annotations

from dataclasses import replace

import streamlit as st

from bausteine.fall_formular import als_datum, als_iso
from bausteine.gemeinsam import (fall_oeffnen, marke, meldung_merken,
                                 meldung_zeigen)
from bausteine.zeitstrahl_anzeige import legende_zeigen, zeitstrahl_zeigen
from daten import (Fall, Geraet, datum_de, euro, fall_sichern,
                   geraet_loeschen, geraet_sichern, geraete_laden, heute)
from recht.gewaehrleistung import lage_ermitteln, monate_zwischen


def sortierschluessel(geraet: Geraet, heute_iso: str) -> tuple[int, int]:
    """Ohne Kaufdatum zuerst, dann das älteste Gerät."""
    if not geraet.kaufdatum:
        return (0, 0)
    return (1, -monate_zwischen(geraet.kaufdatum, heute_iso))


def fall_aus_geraet(geraet_id: str) -> None:
    """Callback: aus einem Gerät einen Fall machen und ihn öffnen."""
    geraet = next(g for g in geraete_laden() if g.id == geraet_id)
    produkt = " ".join(t for t in (geraet.hersteller, geraet.name) if t)
    beschreibung = ""
    if geraet.seriennummer:
        beschreibung = f"Seriennummer: {geraet.seriennummer}"
    fall = Fall(produkt=produkt or geraet.name, haendler=geraet.haendler,
                kaufdatum=geraet.kaufdatum, preis=geraet.preis,
                garantie_monate=geraet.garantie_monate,
                beschreibung=beschreibung)
    fall_sichern(fall)
    geraet_sichern(replace(geraet, fall_id=fall.id))
    fall_oeffnen(fall.id)


def _formularfelder(geraet: Geraet) -> dict:
    links, rechts = st.columns(2)
    preis = float(geraet.preis) if geraet.preis is not None else None
    return {
        "name": links.text_input("Was ist es?", geraet.name,
                                 placeholder="z. B. Waschmaschine"),
        "hersteller": rechts.text_input("Hersteller", geraet.hersteller),
        "haendler": links.text_input("Händler", geraet.haendler),
        "kaufdatum": rechts.date_input(
            "Kaufdatum", als_datum(geraet.kaufdatum), format="DD.MM.YYYY",
            help="Die wichtigste Angabe."),
        "preis": links.number_input("Preis (€)", min_value=0.0, value=preis,
                                    step=1.0, format="%.2f"),
        "garantie_monate": rechts.number_input(
            "Garantie (Monate)", min_value=0, value=geraet.garantie_monate,
            step=1),
        "seriennummer": links.text_input("Seriennummer",
                                         geraet.seriennummer),
        "notiz": rechts.text_input("Notiz", geraet.notiz),
    }


def _formular(geraet: Geraet, knopf: str = "Speichern") -> bool:
    """Formular für ein Gerät. Gibt True zurück, wenn gespeichert wurde."""
    with st.form(f"geraet_{geraet.id}"):
        st.caption("Name und Kaufdatum reichen. Alles andere hilft später "
                   "beim Schreiben.")
        werte = _formularfelder(geraet)
        speichern = st.form_submit_button(knopf, type="primary")
    if not speichern:
        return False
    if not werte["name"].strip():
        st.warning("Bitte einen Namen eintragen.")
        return False
    werte["name"] = werte["name"].strip()
    werte["kaufdatum"] = als_iso(werte["kaufdatum"])
    if werte["garantie_monate"] is not None:
        werte["garantie_monate"] = int(werte["garantie_monate"])
    geraet_sichern(replace(geraet, **werte))
    return True


def _neues_geraet(offen: bool) -> None:
    """Formular für ein neues Gerät, immer erreichbar.

    Der Entwurf liegt in ``st.session_state``, damit das Formular zwischen
    zwei Durchläufen dieselbe Kennung behält.
    """
    entwurf = st.session_state.setdefault("neues_geraet_entwurf", Geraet())
    with st.expander("➕ Neues Gerät anlegen", expanded=offen):
        gespeichert = _formular(entwurf, knopf="Gerät anlegen")
    if gespeichert:
        del st.session_state["neues_geraet_entwurf"]
        meldung_merken(f"{entwurf.name or 'Gerät'} angelegt.")
        st.rerun()


def _bearbeiten(geraet: Geraet) -> None:
    """Das Bearbeitungsformular unter einem Gerät."""
    if _formular(geraet):
        st.session_state["geraet_bearbeiten"] = None
        meldung_merken("Änderungen gespeichert.")
        st.rerun()
    if st.button("Abbrechen", key=f"abbrechen_{geraet.id}"):
        st.session_state["geraet_bearbeiten"] = None
        st.rerun()


def _marken(geraet: Geraet, heute_iso: str) -> str:
    if not geraet.kaufdatum:
        return marke("Kaufdatum fehlt", "warn")
    lage = lage_ermitteln(Fall(kaufdatum=geraet.kaufdatum,
                               garantie_monate=geraet.garantie_monate),
                          heute_iso)
    if lage.in_frist:
        rest = 24 - lage.monate
        text = f"noch {rest} Monat{'' if rest == 1 else 'e'} Gewährleistung"
        teile = [marke(text, "warn" if rest <= 3 else "ok")]
    else:
        teile = [marke("Gewährleistung abgelaufen", "neutral")]
    if lage.garantie_laeuft:
        teile.append(marke("Garantie läuft", "akzent"))
    return " ".join(teile)


def _knoepfe(geraet: Geraet) -> None:
    eins, zwei, drei = st.columns(3)
    if geraet.fall_id:
        eins.button("Zum Fall", key=f"zum_fall_{geraet.id}",
                    on_click=fall_oeffnen, args=(geraet.fall_id,))
    else:
        eins.button("Mangel melden — Fall anlegen",
                    key=f"melden_{geraet.id}", on_click=fall_aus_geraet,
                    args=(geraet.id,))
    if zwei.button("Bearbeiten", key=f"bearbeiten_{geraet.id}"):
        st.session_state["geraet_bearbeiten"] = geraet.id
        st.rerun()
    drei.button("Löschen", key=f"geraet_loeschen_{geraet.id}",
                on_click=geraet_loeschen, args=(geraet.id,))


def _geraet_zeigen(geraet: Geraet, heute_iso: str) -> None:
    with st.container(border=True):
        titel = geraet.name or "Ohne Namen"
        if geraet.hersteller:
            titel += f" · {geraet.hersteller}"
        st.markdown(f"#### {titel}")
        st.markdown(f"{_marken(geraet, heute_iso)} · {euro(geraet.preis)}")
        angaben = [geraet.haendler, geraet.seriennummer]
        if geraet.kaufdatum:
            angaben.insert(1, f"gekauft am {datum_de(geraet.kaufdatum)}")
        st.caption(" · ".join(a for a in angaben if a)
                   or "Keine weiteren Angaben")
        zeitstrahl_zeigen(geraet.kaufdatum, geraet.garantie_monate,
                          heute_iso)
        if geraet.notiz:
            st.caption(geraet.notiz)
        _knoepfe(geraet)
        if st.session_state.get("geraet_bearbeiten") == geraet.id:
            _bearbeiten(geraet)


def geraete_seite() -> None:
    """Alle eingetragenen Geräte mit Zeitstrahl."""
    tag = heute()
    geraete = geraete_laden()
    st.title("Geräte")
    laufend = [g for g in geraete
               if g.kaufdatum and monate_zwischen(g.kaufdatum, tag) < 24]
    st.caption(f"{len(geraete)} Geräte · {len(laufend)} noch in "
               "Gewährleistung" if geraete
               else "Trag deine Käufe ein, solange sie funktionieren.")
    meldung_zeigen()
    _neues_geraet(offen=not geraete)
    if not geraete:
        st.info("Wenn ein Gerät nach 20 Monaten ausfällt, entscheidet eine "
                "einzige Zahl darüber, ob du Anspruch hast: das Kaufdatum. "
                "Wer es hier einträgt, sieht am Zeitstrahl sofort, woran "
                "er ist.")
        return
    legende_zeigen()
    for geraet in sorted(geraete, key=lambda g: sortierschluessel(g, tag)):
        _geraet_zeigen(geraet, tag)
