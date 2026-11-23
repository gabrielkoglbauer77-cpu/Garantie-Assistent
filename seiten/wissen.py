"""Die Rechtslage zum Nachlesen — ohne Fallbezug.

Die Liste der Ablehnungen kommt aus derselben Quelle wie die
Konterfunktion in der Akte, damit beides nicht auseinanderläuft.
"""

from __future__ import annotations

import streamlit as st

from recht.ablehnungen import ABLEHNUNGEN

GEWAEHRLEISTUNG = """
- Schuldet der **Verkäufer**, nicht der Hersteller.
- Zwei Jahre ab Übergabe (AT: § 933 ABGB, DE: § 438 BGB).
- Erste zwölf Monate: Der Verkäufer muss beweisen, dass die Ware in
  Ordnung war.
- Gegenüber Verbrauchern nicht abdingbar — auch nicht durch AGB.
- Gilt unabhängig davon, ob eine Garantie besteht oder abgelaufen ist.
"""

GARANTIE = """
- Schuldet, wer sie gegeben hat — meist der Hersteller.
- Dauer und Inhalt stehen in der Zusage, nicht im Gesetz.
- Darf Bedingungen enthalten (Registrierung, Servicepartner).
- Tritt neben die Gewährleistung, ersetzt sie nicht
  (AT: § 9b KSchG, DE: § 443 BGB).
- Ihr Ablauf sagt über die gesetzlichen Rechte nichts aus.
"""

REIHENFOLGE = [
    ("1. Verbesserung oder Austausch",
     "AT § 932 Abs 1, 2 ABGB · DE § 439 BGB",
     "Zuerst darf nachgebessert oder ersetzt werden. Die Wahl liegt bei "
     "dir, solange sie nicht unverhältnismäßig ist."),
    ("2. Preisminderung", "AT § 932 Abs 4 ABGB · DE § 441 BGB",
     "Scheitert die Verbesserung, wird sie verweigert oder dauert sie zu "
     "lange: Kaufpreis anteilig herabsetzen. Die Sache bleibt bei dir."),
    ("3. Wandlung — Vertragsauflösung",
     "AT § 932 Abs 4 ABGB · DE §§ 437 Nr. 2, 323 BGB",
     "Bei nicht geringfügigem Mangel: Ware zurück, voller Kaufpreis "
     "zurück — in Geld, nicht als Gutschein."),
    ("+ Schadenersatz daneben", "AT § 933a ABGB · DE § 280 BGB",
     "Porto, Einschreiben, Fahrt- und Gutachterkosten. Läuft zusätzlich."),
]

KEINE_REAKTION = """
- **Schlichtung.** In Österreich die Schlichtung für
  Verbrauchergeschäfte, in Deutschland die Universalschlichtungsstelle des
  Bundes. Kostenlos für Verbraucher.
- **Bei Kauf im EU-Ausland.** Das Europäische Verbraucherzentrum vermittelt
  grenzüberschreitend.
- **Bei Kartenzahlung.** Chargeback über die eigene Bank prüfen — mit
  eigenen, oft kürzeren Fristen.
- **Mahnung mit Verzugszinsen.** Nach Fristablauf schuldet der Händler
  Verzugszinsen und die Kosten der Rechtsverfolgung.
- **Gericht.** In Österreich beim Bezirksgericht bis 15.000 Euro ohne
  Anwaltspflicht; in Deutschland beim Amtsgericht bis 5.000 Euro.
"""


def _gegenueberstellung() -> None:
    st.subheader("Gewährleistung und Garantie sind nicht dasselbe")
    links, rechts = st.columns(2)
    with links.container(border=True):
        st.markdown("**:green[Gewährleistung — gesetzlich]**")
        st.markdown(GEWAEHRLEISTUNG)
    with rechts.container(border=True):
        st.markdown("**Garantie — freiwillig**")
        st.markdown(GARANTIE)


def _reihenfolge() -> None:
    st.subheader("Die Reihenfolge der Rechte")
    for titel, norm, text in REIHENFOLGE:
        with st.container(border=True):
            st.markdown(f"**{titel}**  \n:blue[{norm}]")
            st.caption(text)
    st.caption("Preisminderung und Wandlung entstehen erst, wenn die "
               "Verbesserung gescheitert oder eine angemessene Frist "
               "fruchtlos verstrichen ist. Ohne Datum gibt es keinen "
               "Fristablauf.")


def _ablehnungen() -> None:
    st.subheader(f"Die {len(ABLEHNUNGEN)} Standardablehnungen")
    for ablehnung in ABLEHNUNGEN:
        with st.expander(ablehnung.label):
            st.write(ablehnung.entgegnung)
            st.markdown(f":blue[AT: {ablehnung.norm['AT']} · "
                        f"DE: {ablehnung.norm['DE']}]")


def wissen_seite() -> None:
    """Die Seite „Rechtslage“."""
    st.title("Rechtslage")
    _gegenueberstellung()
    _reihenfolge()
    _ablehnungen()
    st.subheader("Wenn der Händler nicht reagiert")
    st.markdown(KEINE_REAKTION)
    st.info("Diese App ist Orientierung und keine Rechtsberatung. Bei "
            "größeren Beträgen oder Streit über die Ursache des Mangels: "
            "Arbeiterkammer, VKI, Verbraucherzentrale oder Anwalt.")
