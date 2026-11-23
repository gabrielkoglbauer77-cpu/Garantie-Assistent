"""Gewährleistung gegen Garantie — der Unterschied, an dem die meisten
Ansprüche scheitern.

Händler beantworten einen Gewährleistungsanspruch routinemäßig mit „die
Garantie ist abgelaufen". Das ist keine Antwort, sondern eine Verwechslung:

    Gewährleistung  gesetzlich · schuldet der VERKÄUFER · zwei Jahre ab
                    Übergabe · gegenüber Verbrauchern nicht abdingbar
    Garantie        freiwillig · schuldet, wer sie gegeben hat (meist der
                    Hersteller) · Inhalt und Dauer stehen in der Zusage

Dieses Modul rechnet ausschließlich. Jede Aussage nennt die Norm, aus der
sie folgt. Orientierung, keine Rechtsberatung.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

from daten import Fall


@dataclass
class Recht:
    """Ein Recht des Käufers mit Norm und Verfügbarkeit."""

    id: str
    titel: str
    norm: str
    erklaerung: str
    verfuegbar: bool
    hinweis: str | None = None


@dataclass
class Lage:  # pylint: disable=too-many-instance-attributes
    """Die Rechtslage eines Falls an einem bestimmten Tag."""

    monate: int | None
    in_frist: bool
    beweislast_beim_haendler: bool
    garantie_laeuft: bool
    frist_ende: str | None
    beweislast_ende: str | None
    rechte: list[Recht]
    kernsatz: str
    fallen: list[str]


# Die Texte der sechs Rechte. Die Norm steht je Rechtsordnung dabei.
RECHTE_TEXTE = [
    {
        "id": "verbesserung",
        "titel": "Reparatur oder Austausch verlangen",
        "norm": {"AT": "§ 932 Abs 1 und 2 ABGB", "DE": "§ 439 BGB"},
        "erklaerung": (
            "Der Verkäufer darf zuerst nachbessern oder ersetzen. Zwischen "
            "beidem wählst du, solange deine Wahl nicht unverhältnismäßig "
            "ist. Beides muss kostenlos und ohne erhebliche "
            "Unannehmlichkeiten erfolgen."
        ),
    },
    {
        "id": "preisminderung",
        "titel": "Preis mindern",
        "norm": {"AT": "§ 932 Abs 4 ABGB", "DE": "§ 441 BGB"},
        "erklaerung": (
            "Scheitert die Verbesserung, wird sie verweigert oder dauert sie "
            "unzumutbar lange, kannst du den Kaufpreis anteilig herabsetzen "
            "und die Differenz zurückfordern."
        ),
        "hinweis": (
            "Setzt in der Regel einen gescheiterten oder verweigerten "
            "Verbesserungsversuch voraus."
        ),
    },
    {
        "id": "wandlung",
        "titel": "Vertrag auflösen, voller Kaufpreis zurück",
        "norm": {"AT": "§ 932 Abs 4 ABGB", "DE": "§§ 437 Nr. 2, 323 BGB"},
        "erklaerung": (
            "Bei einem nicht geringfügigen Mangel kannst du den Vertrag "
            "rückgängig machen: Ware zurück, Geld zurück — und zwar in Geld, "
            "nicht als Gutschein."
        ),
        "hinweis": (
            "Nur bei nicht geringfügigem Mangel und grundsätzlich erst nach "
            "gescheiterter Verbesserung."
        ),
    },
    {
        "id": "beweislast",
        "titel": "Der Händler muss beweisen, dass die Ware in Ordnung war",
        "norm": {"AT": "§ 924 ABGB", "DE": "§ 477 BGB"},
        "erklaerung": (
            "Zeigt sich der Mangel in den ersten zwölf Monaten, wird "
            "vermutet, dass er schon bei der Übergabe vorlag. Das Gegenteil "
            "muss der Verkäufer beweisen — nicht du."
        ),
    },
    {
        "id": "schadenersatz",
        "titel": "Begleitkosten zusätzlich fordern",
        "norm": {"AT": "§ 933a ABGB", "DE": "§ 280 BGB"},
        "erklaerung": (
            "Porto, Einschreiben, Fahrt- und Gutachterkosten, die durch den "
            "Mangel entstanden sind, kannst du neben der Gewährleistung "
            "ersetzt verlangen."
        ),
    },
    {
        "id": "garantie",
        "titel": "Zusätzlich die Herstellergarantie nutzen",
        "norm": {"AT": "§ 9b KSchG", "DE": "§ 443 BGB"},
        "erklaerung": (
            "Eine Garantie tritt neben die Gewährleistung, sie ersetzt sie "
            "nicht. Du kannst wählen, welchen Weg du gehst — oder beide."
        ),
    },
]

HINWEIS_BEWEISLAST_VORBEI = (
    "Diese Vermutung ist abgelaufen. Jetzt musst du belegen, dass der Mangel "
    "von Anfang an bestand — etwa durch ein Gutachten."
)
HINWEIS_KEINE_GARANTIE = (
    "Keine laufende Garantie erfasst. Das ändert an den gesetzlichen Rechten "
    "nichts."
)


def _datum(iso: str) -> date:
    return date.fromisoformat(iso[:10])


def monate_zwischen(von_iso: str, bis_iso: str) -> int:
    """Volle Kalendermonate zwischen zwei Daten.

    Nicht Tage durch 30: Die Zweijahresfrist endet am selben Kalendertag.
    Der laufende Monat zählt erst, wenn der Kalendertag erreicht ist.
    """
    von, bis = _datum(von_iso), _datum(bis_iso)
    roh = (bis.year - von.year) * 12 + (bis.month - von.month)
    return roh - 1 if bis.day < von.day else roh


def plus_monate(iso: str, monate: int) -> str:
    """Datum plus n Monate; der 31.01. plus ein Monat wird zum 28.02."""
    start = _datum(iso)
    index = start.month - 1 + monate
    jahr, monat = start.year + index // 12, index % 12 + 1
    tag = min(start.day, calendar.monthrange(jahr, monat)[1])
    return date(jahr, monat, tag).isoformat()


def _verfuegbarkeit(lage_werte: dict) -> dict:
    """Welches Recht steht nach der verstrichenen Zeit zur Verfügung?"""
    in_frist = lage_werte["in_frist"]
    return {
        "verbesserung": in_frist,
        "preisminderung": in_frist,
        "wandlung": in_frist,
        "beweislast": lage_werte["beweislast"],
        "schadenersatz": True,
        "garantie": lage_werte["garantie"],
    }


def _rechte(recht: str, lage_werte: dict) -> list[Recht]:
    """Baut die sechs Rechte mit Norm der jeweiligen Rechtsordnung."""
    verfuegbar = _verfuegbarkeit(lage_werte)
    ergebnis = []
    for text in RECHTE_TEXTE:
        ergebnis.append(Recht(
            id=text["id"],
            titel=text["titel"],
            norm=text["norm"][recht],
            erklaerung=text["erklaerung"],
            verfuegbar=verfuegbar[text["id"]],
            hinweis=text.get("hinweis"),
        ))
    beweislast, garantie = ergebnis[3], ergebnis[5]
    if not beweislast.verfuegbar:
        beweislast.hinweis = HINWEIS_BEWEISLAST_VORBEI
    if not garantie.verfuegbar:
        garantie.hinweis = HINWEIS_KEINE_GARANTIE
    return ergebnis


def _fallen(at: bool, beweislast: bool, monate: int | None) -> list[str]:
    """Die Fallen, die in der Praxis am meisten kosten."""
    gesetz = "§ 377 UGB gilt nur zwischen Unternehmern" if at else (
        "§ 377 HGB gilt nur unter Kaufleuten")
    fallen = [
        "„Die Garantie ist abgelaufen“ ist keine Antwort auf einen "
        "Gewährleistungsanspruch. Die Gewährleistung ist gesetzlich und "
        "läuft unabhängig davon.",
        "Gewährleistung schuldet der Verkäufer, nicht der Hersteller. Lass "
        "dich nicht an den Hersteller weiterschieben.",
        "Gegenüber Verbrauchern kann die Gewährleistung nicht durch AGB "
        "ausgeschlossen oder verkürzt werden.",
        "Ein Gutschein ist keine Erfüllung, wenn du die Vertragsauflösung "
        "verlangst — dann steht dir Geld zu.",
        f"Eine Rügepflicht trifft dich als Verbraucher nicht; {gesetz}.",
    ]
    if not beweislast and monate is not None:
        fallen.append(
            f"Seit dem Kauf sind {monate} Monate vergangen. Sichere jetzt "
            "alles, was belegt, dass der Mangel von Anfang an bestand."
        )
    return fallen


def _kernsatz(at: bool, in_frist: bool) -> str:
    """Der Satz, der in jedes Schreiben gehört."""
    if in_frist:
        norm = "§ 932 ABGB" if at else "§ 437 BGB"
        return (
            f"Ich mache Gewährleistungsansprüche nach {norm} geltend. Diese "
            "bestehen gesetzlich gegenüber Ihnen als Verkäufer und sind von "
            "einer allfälligen Herstellergarantie unabhängig."
        )
    norm = "§ 933 ABGB" if at else "§ 438 BGB"
    return (
        "Auch nach Ablauf der zweijährigen Gewährleistungsfrist bleiben "
        "Ansprüche möglich, wenn der Mangel bereits bei Übergabe vorlag "
        f"({norm}) — die Beweislast dafür liegt dann bei mir."
    )


def lage_ermitteln(fall: Fall, heute_iso: str) -> Lage:
    """Beantwortet aus Kaufdatum und Rechtsordnung die ganze Rechtslage.

    Ohne Kaufdatum wird zugunsten des Nutzers angenommen, dass die Fristen
    noch laufen — ihm auf Verdacht zu sagen, seine Rechte seien abgelaufen,
    wäre der teurere Irrtum.
    """
    at = fall.recht == "AT"
    monate = None
    if fall.kaufdatum:
        monate = monate_zwischen(fall.kaufdatum, heute_iso)
    in_frist = monate is None or monate < 24
    beweislast = monate is None or monate < 12
    garantie = (
        fall.garantie_monate is not None
        and monate is not None
        and monate < fall.garantie_monate
    )
    werte = {"in_frist": in_frist, "beweislast": beweislast,
             "garantie": garantie}
    kauf = fall.kaufdatum
    return Lage(
        monate=monate,
        in_frist=in_frist,
        beweislast_beim_haendler=beweislast,
        garantie_laeuft=garantie,
        frist_ende=plus_monate(kauf, 24) if kauf else None,
        beweislast_ende=plus_monate(kauf, 12) if kauf else None,
        rechte=_rechte(fall.recht, werte),
        kernsatz=_kernsatz(at, in_frist),
        fallen=_fallen(at, beweislast, monate),
    )


def frist_text(lage: Lage) -> str:
    """Kurzform für Listen: „noch 14 Monate“ oder „abgelaufen“."""
    if lage.monate is None:
        return "Kaufdatum fehlt"
    if not lage.in_frist:
        return "Gewährleistung abgelaufen"
    rest = 24 - lage.monate
    return f"noch {rest} Monat{'' if rest == 1 else 'e'}"
