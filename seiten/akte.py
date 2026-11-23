"""Die Akte: alles zu einem Fall.

Die Reihenfolge folgt der Dringlichkeit, nicht dem Thema: Was ist jetzt zu
tun (Fristen), was geht hinaus (Schreiben), was ist passiert (Verlauf),
womit begründe ich es (Rechte), was hat er geantwortet (Ablehnung), was
kann ich belegen (Belege). Die Stammdaten stehen unten und eingeklappt.

Jede Änderung wird sofort mit ``fall_sichern`` gespeichert. Die Akte liest
den Fall bei jedem Durchlauf neu aus der Datei — es gibt keine zweite Kopie,
die abweichen könnte.
"""

from __future__ import annotations

import streamlit as st

from bausteine.ablehnung_panel import ablehnung_zeigen
from bausteine.belege_panel import belege_zeigen
from bausteine.fall_formular import fall_formular
from bausteine.fristen_panel import fristen_zeigen
from bausteine.gemeinsam import marke, zur_liste
from bausteine.rechte_panel import rechte_zeigen
from bausteine.schreiben_panel import schreiben_zeigen
from bausteine.verlauf_panel import verlauf_zeigen
from daten import (STATUS_TEXT, Ereignis, Fall, datum_de, euro, fall_finden,
                   fall_loeschen, fall_sichern, heute)
from recht.gewaehrleistung import lage_ermitteln


def status_setzen(fall_id: str) -> None:
    """Callback: neuen Status speichern und im Verlauf vermerken."""
    fall = fall_finden(fall_id)
    neu = st.session_state[f"status_{fall_id}"]
    if fall is None or neu == fall.status:
        return
    fall.status = neu
    fall.ereignisse.append(Ereignis(datum=heute(), art="status",
                                    text=f"Status: {STATUS_TEXT[neu]}"))
    fall_sichern(fall)


def loeschen(fall_id: str) -> None:
    """Callback: Fall löschen und zurück zur Liste."""
    fall_loeschen(fall_id)
    zur_liste()


def _kopf(fall: Fall, heute_iso: str) -> None:
    st.button("← Alle Fälle", on_click=zur_liste)
    st.title(fall.produkt or "Ohne Produktnamen")
    lage = lage_ermitteln(fall, heute_iso)
    teile = [fall.haendler or "Händler fehlt"]
    if fall.preis is not None:
        teile.append(euro(fall.preis))
    if fall.kaufdatum:
        teile.append(f"gekauft am {datum_de(fall.kaufdatum)}")
    frist = (marke(f"Gewährleistung läuft bis {datum_de(lage.frist_ende)}",
                   "ok") if lage.in_frist
             else marke("Gewährleistung abgelaufen", "gefahr"))
    beweis = (marke("Händler muss beweisen", "ok")
              if lage.beweislast_beim_haendler
              else marke("Du musst beweisen", "warn"))
    st.markdown(" · ".join(teile) + f"  \n{frist} {beweis}")


def _verwaltung(fall: Fall) -> None:
    links, rechts = st.columns([3, 1])
    # Vor dem Zeichnen auf den gespeicherten Stand setzen: Der Status kann
    # sich auch durch „Als gesendet vermerken“ geändert haben.
    st.session_state[f"status_{fall.id}"] = fall.status
    links.selectbox("Status", list(STATUS_TEXT),
                    format_func=STATUS_TEXT.get, key=f"status_{fall.id}",
                    on_change=status_setzen, args=(fall.id,))
    bestaetigt = rechts.checkbox("Löschen bestätigen",
                                 key=f"bestaetigen_{fall.id}")
    rechts.button("Fall löschen", disabled=not bestaetigt,
                  on_click=loeschen, args=(fall.id,))


def akte_seite(fall_id: str) -> None:
    """Die Akte eines Falls."""
    fall = fall_finden(fall_id)
    if fall is None:
        st.warning("Diesen Fall gibt es nicht mehr. Er wurde gelöscht oder "
                   "die Daten wurden ersetzt.")
        st.button("Zurück zur Liste", on_click=zur_liste)
        return
    tag = heute()
    _kopf(fall, tag)
    _verwaltung(fall)
    links, rechts = st.columns(2)
    with links:
        fristen_zeigen(fall, tag)
        schreiben_zeigen(fall)
        verlauf_zeigen(fall)
    with rechts:
        rechte_zeigen(fall, tag)
        ablehnung_zeigen(fall)
        belege_zeigen(fall)
    with st.expander("Stammdaten bearbeiten"):
        if fall_formular(fall, knopf="Änderungen speichern"):
            st.rerun()
