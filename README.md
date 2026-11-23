# Garantie-Assistent

## Was ist das?

Eine App, mit der man Gewährleistung und Garantie gegenüber Händlern
durchsetzt. Sie rechnet die Fristen, benennt die Rechte mit der passenden
Norm (Österreich: ABGB/KSchG, Deutschland: BGB), erkennt die üblichen
Ablehnungen in der Antwort des Händlers und erzeugt daraus das passende
Schreiben.

Kein Konto, keine Schlüssel, kein Sprachmodell. Die Daten liegen lokal im
Ordner `daten` neben dem Programm.

## Voraussetzungen

Python 3.9 oder neuer.

## Installation

Im Projektordner (dort, wo `requirements.txt` liegt):

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

## Starten

```bash
streamlit run app.py
```

Der Browser öffnet sich mit der App (sonst <http://localhost:8501>).
Beenden mit `Strg + C` im Terminal.

Beim ersten Start ist die **Demo** eingeschaltet: fünf Beispielfälle und
fünf Beispielgeräte in allen Zuständen. In der Seitenleiste lässt sie sich
mit dem Schalter **„Demo-Daten“** aus- und wieder einschalten. Ausschalten
entfernt nur die Beispiele; eigene Fälle und Geräte bleiben erhalten.

Neue Fälle und Geräte legt man über „➕ Neuen Fall anlegen“ bzw.
„➕ Neues Gerät anlegen“ an.

## Prüfungen

```bash
python pruefung.py
```

Prüft Datumsrechnung, Rechtslage, nächsten Schritt, Ablehnungen, Schreiben,
Zeitstrahl, Speicher und Demo-Daten — ohne die Oberfläche zu starten.

## Was sie kann

- **Fälle:** Jeder Fall ist eine Akte mit Stammdaten, Fristen, Rechten,
  Schreiben, Verlauf und Belegen. Die Startseite sortiert nach
  Dringlichkeit und nennt zu jedem Fall genau einen nächsten Schritt.
- **Fristen:** Eigene Frist an den Händler, zwölf Monate Beweislastumkehr,
  zwei Jahre Gewährleistung und Herstellergarantie werden gleichzeitig
  gerechnet.
- **Rechte:** Verbesserung, Preisminderung, Wandlung, Beweislast,
  Schadenersatz, Garantie — jeweils mit Norm und ob es gerade zur
  Verfügung steht.
- **Ablehnungen kontern:** Zwölf Standardablehnungen („Garantie
  abgelaufen“, „Fotos fehlen“, „normaler Verschleiß“ …) werden im
  Antworttext erkannt und mit Gegenargument, Norm und fertigem Absatz
  beantwortet.
- **Schreiben:** Mängelanzeige, Antwort auf Ablehnung, letzte Nachfrist,
  Vertragsauflösung — zum Kopieren, Herunterladen oder Öffnen im
  Mailprogramm.
- **Geräte mit Zeitstrahl:** Käufe eintragen, solange alles funktioniert;
  ein farbiger Balken zeigt, wo das Gerät rechtlich steht.
- **Rechtslage:** eine Erklärseite in der App.

## Aufbau

```
app.py              Einstieg: Seitenleiste und Navigation
daten.py            Datenmodell (Fall, Gerät, Verlauf, Beleg) und JSON-Speicher
demo.py             Beispieldaten, relativ zum heutigen Datum
zeitstrahl.py       Rechnung hinter dem farbigen Balken
bilder.py           Fotos verkleinern
recht/              Rechtslogik ohne Oberfläche
  gewaehrleistung.py  Rechtslage: Monate, Beweislast, Rechte, Normen
  fristen.py          vier Fristen und der nächste Schritt
  ablehnungen.py      zwölf Standardablehnungen und ihre Erkennung
  schreiben.py        die vier Briefe
seiten/             was auf dem Bildschirm steht
  faelle.py           Fallliste
  akte.py             Akte eines Falls
  geraete.py          Geräteliste
  wissen.py           Rechtslage zum Nachlesen
bausteine/          wiederverwendbare Teile der Oberfläche
pruefung.py         Prüfungen der Logik
```

Die Regel dahinter: `recht/` kennt Streamlit nicht und rechnet nur.
`seiten/` und `bausteine/` zeigen an und rufen die Rechtslogik auf.

## Bekannte Einschränkungen

- **Keine Mehrbenutzer-Verwaltung.** Die Daten liegen lokal in
  `daten/faelle.json` und `daten/geraete.json`, Belege in `daten/belege/`.
- **Sicherung ohne Dateien.** „Sichern“ exportiert Fälle und Geräte als
  JSON; Fotos und PDFs der Belege sind darin nicht enthalten.
- **Erkennung über Stichwörter.** Formulierungen, die nicht in der Liste
  stehen, werden nicht erkannt; dann wählt man die passende Ablehnung von
  Hand aus der vollständigen Liste.
- **Nur Österreich und Deutschland.**
- **Orientierung, keine Rechtsberatung.** Bei größeren Beträgen oder Streit
  über die Ursache: Arbeiterkammer, VKI, Verbraucherzentrale oder Anwalt.
