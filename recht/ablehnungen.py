"""Was Händler antworten, wenn sie eine Reklamation loswerden wollen — und
was rechtlich dagegen steht.

Die häufigste Ablehnung ist kein Rechtsstandpunkt, sondern ein
Textbaustein: „Bitte senden Sie Fotos“, „kein Gewährleistungsfall“,
„Garantie abgelaufen“. Wer darauf nichts erwidert, verliert einen Anspruch,
der bestanden hätte.

Die Erkennung läuft über Stichwörter, nicht über ein Sprachmodell. Sie ist
sofort da, kostet nichts und ist nachvollziehbar.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Ablehnung:  # pylint: disable=too-many-instance-attributes
    """Eine Standardablehnung mit Gegenargument und fertigem Absatz."""

    id: str
    label: str
    muster: list[str]
    behauptung: str
    entgegnung: str
    norm: dict[str, str]
    beweis: list[str]
    absatz: str
    danach: str


ABLEHNUNGEN = [
    Ablehnung(
        id="garantie_abgelaufen",
        label="Garantie ist abgelaufen",
        muster=["garantie abgelaufen", "garantiezeit",
                "außerhalb der garantie", "herstellergarantie",
                "garantie ist vorbei"],
        behauptung="Die Garantiezeit sei vorbei, daher bestünden keine "
                   "Ansprüche.",
        entgegnung=(
            "Garantie und Gewährleistung sind zwei verschiedene Dinge. Die "
            "Garantie ist eine freiwillige Zusage, die Gewährleistung ist "
            "gesetzlich, schuldet sie der Verkäufer, und sie besteht "
            "unabhängig davon, ob eine Garantie läuft. Das ist die häufigste "
            "und folgenreichste Verwechslung."
        ),
        norm={"AT": "§ 932 ABGB, § 9b KSchG", "DE": "§ 437 BGB, § 443 BGB"},
        beweis=["Kaufbeleg mit Datum", "Datum, an dem der Mangel auftrat"],
        absatz=(
            "Ich stütze meinen Anspruch nicht auf eine Garantie, sondern auf "
            "die gesetzliche Gewährleistung. Diese steht mir gegenüber Ihnen "
            "als meinem Vertragspartner zu und besteht unabhängig davon, ob "
            "eine Herstellergarantie noch läuft. Die Gewährleistungsfrist "
            "war zum Zeitpunkt meiner Anzeige nicht abgelaufen."
        ),
        danach="Schlichtungsstelle anrufen — die Rechtslage ist hier "
               "eindeutig.",
    ),
    Ablehnung(
        id="fotos",
        label="Fotos fehlen / Bildmaterial unzureichend",
        muster=["foto", "bilder", "bildmaterial", "aufnahmen",
                "nachweis in form von"],
        behauptung="Ohne (bessere) Fotos werde die Reklamation nicht "
                   "bearbeitet.",
        entgegnung=(
            "Fotos anzufordern ist zulässig, sie sind aber keine "
            "Anspruchsvoraussetzung. In den ersten zwölf Monaten muss nicht "
            "der Käufer beweisen, dass der Mangel von Anfang an bestand — "
            "der Verkäufer muss das Gegenteil beweisen. Die Bearbeitung darf "
            "daran nicht scheitern, und die Frist läuft weiter."
        ),
        norm={"AT": "§ 924 ABGB", "DE": "§ 477 BGB"},
        beweis=[
            "Gesamtansicht, Mangel in Nahaufnahme, Typenschild/Seriennummer",
            "Kaufbeleg",
            "ein kurzes Video, wenn der Mangel nur im Betrieb sichtbar ist",
        ],
        absatz=(
            "Ich habe Ihnen Bildmaterial übermittelt. Sollten Sie weitere "
            "Aufnahmen benötigen, teilen Sie mir bitte konkret mit, welcher "
            "Umstand darauf erkennbar sein soll. Innerhalb der "
            "Vermutungsfrist trifft nicht mich die Beweislast für das "
            "Vorliegen des Mangels bei Übergabe, sondern Sie die Beweislast "
            "für das Gegenteil. Die Bearbeitung ist unabhängig davon "
            "fortzusetzen."
        ),
        danach="Nachfrist mit Datum setzen und die Rechtsfolgen benennen.",
    ),
    Ablehnung(
        id="kein_fall",
        label="Kein Gewährleistungsfall / normaler Verschleiß",
        muster=["kein gewährleistungsfall", "kein garantiefall",
                "verschleiß", "abnutzung", "gebrauchsspur",
                "nicht als mangel"],
        behauptung="Der Zustand sei üblicher Verschleiß oder gar kein "
                   "Mangel.",
        entgegnung=(
            "Maßgeblich ist, ob die Sache die gewöhnlich vorausgesetzte "
            "Beschaffenheit und Haltbarkeit aufweist. Verschleiß weit vor "
            "der erwartbaren Lebensdauer ist sehr wohl ein Mangel. Die bloße "
            "Behauptung „Verschleiß“ ersetzt keine Begründung — und in den "
            "ersten zwölf Monaten muss der Verkäufer sie beweisen."
        ),
        norm={"AT": "§ 922 ABGB, § 924 ABGB",
              "DE": "§ 434 Abs 3 BGB, § 477 BGB"},
        beweis=["Alter und Nutzungsintensität",
                "Herstellerangaben zur Lebensdauer",
                "Sachverständigengutachten"],
        absatz=(
            "Ihre Einordnung als Verschleiß ist nicht begründet. Ein Produkt "
            "muss die gewöhnlich vorausgesetzte Beschaffenheit und "
            "Haltbarkeit aufweisen; ein Defekt nach dieser kurzen "
            "Nutzungsdauer entspricht dem nicht. Ich ersuche um eine "
            "konkrete, nachvollziehbare Begründung. Andernfalls werde ich "
            "ein Sachverständigengutachten einholen und dessen Kosten "
            "geltend machen."
        ),
        danach="Gutachten einholen oder Schlichtungsstelle anrufen.",
    ),
    Ablehnung(
        id="selbst_verursacht",
        label="Schaden selbst verursacht / unsachgemäße Nutzung",
        muster=["unsachgemäß", "selbst verursacht", "eigenverschulden",
                "fremdeinwirkung", "bedienfehler", "sturzschaden"],
        behauptung="Der Mangel beruhe auf falscher Behandlung durch den "
                   "Käufer.",
        entgegnung=(
            "Eine Behauptung, für die in den ersten zwölf Monaten der "
            "Verkäufer beweispflichtig ist. Ohne Prüfbericht oder Gutachten "
            "ist sie unbelegt — und eine unbelegte Behauptung beendet die "
            "Gewährleistung nicht."
        ),
        norm={"AT": "§ 924 ABGB", "DE": "§ 477 BGB"},
        beweis=["Schilderung der tatsächlichen Nutzung",
                "Fotos ohne Fremdeinwirkung", "ggf. Gegengutachten"],
        absatz=(
            "Sie behaupten eine unsachgemäße Nutzung, ohne dies zu belegen. "
            "Innerhalb der Vermutungsfrist trifft Sie die Beweislast dafür, "
            "dass der Mangel bei Übergabe nicht vorlag. Ich ersuche um "
            "Übermittlung des Prüfberichts, auf den Sie sich stützen. Bis "
            "dahin halte ich meinen Anspruch vollumfänglich aufrecht."
        ),
        danach="Prüfbericht verlangen; bleibt er aus, Gutachten einholen.",
    ),
    Ablehnung(
        id="zu_spaet",
        label="Zu spät gemeldet / Rügefrist versäumt",
        muster=["zu spät", "rügefrist", "unverzüglich", "fristversäumnis",
                "hätten sie sofort"],
        behauptung="Der Mangel hätte sofort gemeldet werden müssen.",
        entgegnung=(
            "Eine Rügepflicht gilt nur zwischen Unternehmern. Als "
            "Verbraucher gibt es keine Pflicht, einen Mangel unverzüglich "
            "anzuzeigen — maßgeblich ist allein, dass der Anspruch innerhalb "
            "der Gewährleistungsfrist geltend gemacht wird."
        ),
        norm={"AT": "§ 377 UGB gilt nur beidseitig unternehmerisch",
              "DE": "§ 377 HGB gilt nur unter Kaufleuten"},
        beweis=["Kaufdatum", "Datum der ersten Anzeige mit Zeitstempel"],
        absatz=(
            "Die Rügeobliegenheit gilt ausschließlich für beidseitige "
            "Unternehmergeschäfte. Ich bin Verbraucher; eine Pflicht zur "
            "unverzüglichen Mängelanzeige besteht nicht. Entscheidend ist "
            "allein die Geltendmachung innerhalb der Gewährleistungsfrist, "
            "die gewahrt ist."
        ),
        danach="Nachfrist setzen; bei Beharren Schlichtung.",
    ),
    Ablehnung(
        id="hersteller",
        label="Wenden Sie sich an den Hersteller",
        muster=["an den hersteller", "herstellerservice",
                "direkt beim hersteller", "nicht zuständig",
                "servicepartner"],
        behauptung="Für Mängel sei der Hersteller zuständig.",
        entgegnung=(
            "Gewährleistung schuldet der Vertragspartner, also der "
            "Verkäufer. Ein Verweis an den Hersteller ist als Angebot "
            "zulässig, nicht als Ablehnung — darauf muss man sich nicht "
            "einlassen."
        ),
        norm={"AT": "§§ 922 ff ABGB", "DE": "§ 437 BGB"},
        beweis=["Bestellbestätigung, aus der der Verkäufer hervorgeht"],
        absatz=(
            "Mein Gewährleistungsanspruch richtet sich gegen Sie als meinen "
            "Vertragspartner, nicht gegen den Hersteller. Ein Verweis auf "
            "den Herstellerservice entbindet Sie nicht von Ihrer "
            "gesetzlichen Verpflichtung. Ich ersuche um Bearbeitung durch "
            "Sie selbst."
        ),
        danach="Nachfrist setzen, danach Preisminderung oder Wandlung "
               "erklären.",
    ),
    Ablehnung(
        id="nur_reparatur",
        label="Nur Reparatur, kein Austausch oder Geld",
        muster=["nur reparatur", "instandsetzung", "nachbesserung",
                "reparieren wir", "austausch nicht möglich"],
        behauptung="Es werde ausschließlich repariert.",
        entgegnung=(
            "Zwischen Verbesserung und Austausch wählt zunächst der Käufer; "
            "der Verkäufer darf nur auf die andere Abhilfe verweisen, wenn "
            "die gewählte unverhältnismäßig ist. Scheitert die Verbesserung "
            "oder dauert sie unzumutbar lange, entstehen Preisminderung und "
            "Wandlung."
        ),
        norm={"AT": "§ 932 ABGB", "DE": "§ 439 BGB, § 440 BGB"},
        beweis=["Datum der Übergabe zur Reparatur", "Anzahl der Versuche",
                "Dauer des Ausfalls"],
        absatz=(
            "Die Wahl zwischen Verbesserung und Austausch steht mir zu. Ich "
            "setze Ihnen für die Verbesserung eine Frist bis zum [FRIST]. "
            "Nach fruchtlosem Ablauf, bei einem weiteren erfolglosen Versuch "
            "oder bei unangemessenen Unannehmlichkeiten werde ich "
            "Preisminderung geltend machen bzw. die Wandlung erklären."
        ),
        danach="Nach dem zweiten Fehlversuch die Wandlung erklären.",
    ),
    Ablehnung(
        id="gutschein",
        label="Nur Gutschein statt Geld",
        muster=["gutschein", "guthaben", "coupon", "wertgutschein",
                "credit"],
        behauptung="Erstattet werde nur in Form eines Gutscheins.",
        entgegnung=(
            "Wird der Vertrag rückabgewickelt, besteht Anspruch auf "
            "Rückzahlung in Geld, und zwar auf dem Weg, auf dem gezahlt "
            "wurde. Ein Gutschein muss nicht angenommen werden."
        ),
        norm={"AT": "§ 932 Abs 4 ABGB",
              "DE": "§ 437 Nr. 2 BGB, § 357 Abs 3 BGB"},
        beweis=["Zahlungsnachweis"],
        absatz=(
            "Ein Gutschein stellt keine Erfüllung dar. Bei Rückabwicklung "
            "habe ich Anspruch auf Rückzahlung in Geld, und zwar auf dem "
            "Weg, auf dem ich gezahlt habe. Ich fordere Sie auf, den Betrag "
            "bis zum [FRIST] auf mein Konto zu überweisen."
        ),
        danach="Bei Kartenzahlung zusätzlich Chargeback prüfen — dort läuft "
               "eine eigene Frist.",
    ),
    Ablehnung(
        id="transport",
        label="Transportschaden — nicht unser Problem",
        muster=["transportschaden", "versanddienstleister",
                "beim paketdienst", "spedition", "beschädigt übergeben"],
        behauptung="Für Schäden auf dem Transportweg hafte der "
                   "Versanddienstleister.",
        entgegnung=(
            "Beim Versand an einen Verbraucher geht die Gefahr erst mit der "
            "Übergabe an den Verbraucher über. Ein Transportschaden ist "
            "damit ein Mangel bei Übergabe; das Verhältnis zwischen Händler "
            "und Paketdienst ist für den Käufer ohne Bedeutung."
        ),
        norm={"AT": "§ 7b KSchG", "DE": "§ 475 Abs 2 BGB"},
        beweis=["Fotos von Verpackung UND Ware", "Lieferdatum",
                "ggf. Schadensvermerk bei Zustellung"],
        absatz=(
            "Beim Versendungskauf an einen Verbraucher geht die Gefahr erst "
            "mit der Übergabe an mich über. Ein auf dem Transportweg "
            "entstandener Schaden liegt damit in Ihrer Sphäre. Ihr "
            "Verhältnis zum Versanddienstleister berührt meinen Anspruch "
            "nicht."
        ),
        danach="Nachfrist, dann Wandlung.",
    ),
    Ablehnung(
        id="verpackung",
        label="Originalverpackung fehlt / Siegel gebrochen",
        muster=["originalverpackung", "versiegelt", "siegel", "geöffnet",
                "nicht originalverpackt"],
        behauptung="Ohne Originalverpackung bestehe kein Anspruch.",
        entgegnung=(
            "Die Originalverpackung ist keine Voraussetzung der "
            "Gewährleistung. Ein Produkt wird benutzt, nicht aufbewahrt — "
            "und für den Mangel ist die Verpackung ohne Bedeutung."
        ),
        norm={"AT": "§§ 922 ff ABGB", "DE": "§ 437 BGB"},
        beweis=["Fotos der Ware", "Kaufbeleg"],
        absatz=(
            "Die Originalverpackung ist keine Anspruchsvoraussetzung für die "
            "Gewährleistung. Ich ersuche um Bearbeitung meiner "
            "Mängelanzeige in der Sache."
        ),
        danach="Schlichtungsstelle — solche Fälle werden dort regelmäßig "
               "zugunsten der Verbraucher erledigt.",
    ),
    Ablehnung(
        id="hinhalten",
        label="Wird noch geprüft / in Bearbeitung",
        muster=["in bearbeitung", "wird geprüft", "bitte um geduld",
                "rückmeldung erfolgt", "leiten wir weiter"],
        behauptung="Der Fall werde noch bearbeitet — ohne Ergebnis und ohne "
                   "Termin.",
        entgegnung=(
            "Hinhalten ist keine Erfüllung. Abhilfe ist in angemessener "
            "Frist zu leisten; läuft sie ab, entstehen die weiteren Rechte. "
            "Eine Frist ohne Datum ist keine Frist."
        ),
        norm={"AT": "§ 932 ABGB, § 918 ABGB", "DE": "§ 439 BGB, § 323 BGB"},
        beweis=["Datum der ersten Meldung",
                "alle Nachfragen ohne Ergebnis"],
        absatz=(
            "Seit meiner Meldung liegt kein Ergebnis vor. Ich setze Ihnen "
            "eine letzte Frist bis zum [FRIST]. Nach fruchtlosem Ablauf "
            "werde ich ohne weitere Ankündigung die mir zustehenden Rechte "
            "ausüben und die entstehenden Kosten geltend machen."
        ),
        danach="Nach Fristablauf Wandlung erklären und Verzugszinsen "
               "ansetzen.",
    ),
    Ablehnung(
        id="kulanz",
        label="Nur aus Kulanz, ohne Anerkennung",
        muster=["kulanz", "ohne anerkennung", "aus kulanzgründen",
                "entgegenkommen"],
        behauptung="Man komme entgegen, ohne eine Rechtspflicht "
                   "anzuerkennen.",
        entgegnung=(
            "Kulanz ist nicht schlecht, solange sie das volle Ergebnis "
            "bringt. Problematisch wird sie, wenn sie mit einem Verzicht auf "
            "weitere Ansprüche verknüpft ist oder unter dem liegt, was "
            "gesetzlich zusteht."
        ),
        norm={"AT": "§ 1380 ABGB (Vergleich)", "DE": "§ 779 BGB (Vergleich)"},
        beweis=["Wortlaut des Angebots", "Berechnung des vollen Anspruchs"],
        absatz=(
            "Ich nehme Ihr Angebot ausdrücklich nur als Teilleistung an; auf "
            "weitergehende Ansprüche verzichte ich nicht. Sofern die "
            "Annahme nach Ihrer Auffassung einen Verzicht bedeuten soll, "
            "gilt sie als nicht erklärt."
        ),
        danach="Differenz separat weiterverfolgen — eine Teilzahlung "
               "erkennt den Anspruch faktisch an.",
    ),
]


def ablehnungen_erkennen(text: str) -> list[tuple[Ablehnung, int]]:
    """Findet Standardablehnungen im Antworttext des Händlers.

    Gibt Paare aus Ablehnung und Anzahl der Fundstellen zurück, sortiert
    nach Fundstellen — damit der Hauptgrund oben steht.
    """
    klein = text.lower()
    treffer = []
    for ablehnung in ABLEHNUNGEN:
        anzahl = sum(1 for muster in ablehnung.muster if muster in klein)
        if anzahl > 0:
            treffer.append((ablehnung, anzahl))
    return sorted(treffer, key=lambda paar: paar[1], reverse=True)


def ablehnung_nach(ablehnung_id: str | None) -> Ablehnung | None:
    """Sucht eine Ablehnung über ihre Kennung."""
    return next((a for a in ABLEHNUNGEN if a.id == ablehnung_id), None)
