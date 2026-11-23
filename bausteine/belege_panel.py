"""Belege zum Fall — Fotos, Rechnung, Schriftverkehr als PDF.

Die Dateien liegen im Ordner ``daten/belege``, im Fall steht nur ihr Name.
Bilder werden vor dem Speichern verkleinert.
"""

from __future__ import annotations

import streamlit as st

from bilder import MAX_BYTES, bild_verkleinern, bytes_text, ist_bild
from daten import Beleg, Fall, beleg_ablegen, beleg_pfad, datum_de
from daten import fall_sichern


def _hochladen(fall: Fall) -> None:
    zaehler = st.session_state.setdefault(f"upload_{fall.id}", 0)
    dateien = st.file_uploader(
        "Dateien auswählen", type=["jpg", "jpeg", "png", "webp", "pdf"],
        accept_multiple_files=True, key=f"dateien_{fall.id}_{zaehler}")
    if not dateien or not st.button("Hinzufügen", key=f"dazu_{fall.id}"):
        return
    for datei in dateien:
        inhalt = datei.getvalue()
        if ist_bild(datei.type):
            inhalt = bild_verkleinern(inhalt)
        if len(inhalt) > MAX_BYTES:
            st.error(f"{datei.name} ist mit {bytes_text(len(inhalt))} zu "
                     "groß.")
            continue
        typ = "image/jpeg" if ist_bild(datei.type) else datei.type
        name = datei.name
        if ist_bild(datei.type):
            name = name.rsplit(".", 1)[0] + ".jpg"
        fall.belege.append(beleg_ablegen(name, typ, inhalt))
    fall_sichern(fall)
    # Neuer Schlüssel leert das Auswahlfeld.
    st.session_state[f"upload_{fall.id}"] = zaehler + 1
    st.rerun()


def _beleg_zeigen(fall: Fall, beleg: Beleg) -> None:
    pfad = beleg_pfad(beleg)
    with st.container(border=True):
        if not pfad.exists():
            st.caption(f"{beleg.name}: Datei fehlt")
        elif beleg.typ.startswith("image/"):
            st.image(str(pfad))
        else:
            st.download_button("PDF öffnen", pfad.read_bytes(),
                               file_name=beleg.name,
                               key=f"pdf_{beleg.id}")
        st.caption(f"{beleg.name} · {bytes_text(beleg.groesse)} · "
                   f"{datum_de(beleg.belegt)}")
        if st.button("Entfernen", key=f"entfernen_{beleg.id}"):
            pfad.unlink(missing_ok=True)
            fall.belege = [b for b in fall.belege if b.id != beleg.id]
            fall_sichern(fall)
            st.rerun()


def belege_zeigen(fall: Fall) -> None:
    """Die Karte „Belege“ in der Akte."""
    with st.container(border=True):
        st.subheader("Belege")
        st.caption("Rechnung, Fotos des Mangels, Typenschild, "
                   "Schriftverkehr. Bilder werden automatisch verkleinert.")
        _hochladen(fall)
        if not fall.belege:
            st.caption("Noch kein Beleg. Die Rechnung ist der wichtigste — "
                       "ohne Kaufdatum ist alles andere Auslegung.")
        spalten = st.columns(3)
        for nummer, beleg in enumerate(fall.belege):
            with spalten[nummer % 3]:
                _beleg_zeigen(fall, beleg)
        st.caption("Welche Aufnahmen zählen: Gesamtansicht, Mangel in "
                   "Nahaufnahme, Typenschild oder Seriennummer, bei "
                   "Mängeln im Betrieb ein kurzes Video.")
