"""Fotos verkleinern, bevor sie als Beleg gespeichert werden.

Ein Handyfoto hat 3–8 MB. 1600 Pixel Kantenlänge reichen, damit ein
Mangel, eine Seriennummer oder ein Beleg erkennbar bleibt; das Ergebnis
liegt bei 150–400 KB.
"""

from __future__ import annotations

from io import BytesIO

from PIL import Image

MAX_KANTE = 1600
QUALITAET = 82
MAX_BYTES = 10_000_000


def ist_bild(typ: str) -> bool:
    """Ist die Datei ein Bild (und kein PDF)?"""
    return typ.startswith("image/")


def bild_verkleinern(inhalt: bytes) -> bytes:
    """Rechnet ein Bild auf höchstens 1600 Pixel und gibt JPEG zurück.

    Transparente Stellen bekommen einen weißen Grund, sonst würden sie im
    JPEG schwarz.
    """
    with Image.open(BytesIO(inhalt)) as bild:
        bild.thumbnail((MAX_KANTE, MAX_KANTE))
        grund = Image.new("RGB", bild.size, (255, 255, 255))
        if bild.mode in ("RGBA", "LA", "P"):
            rgba = bild.convert("RGBA")
            grund.paste(rgba, mask=rgba.getchannel("A"))
        else:
            grund.paste(bild.convert("RGB"))
    ausgabe = BytesIO()
    grund.save(ausgabe, format="JPEG", quality=QUALITAET)
    return ausgabe.getvalue()


def bytes_text(anzahl: int) -> str:
    """1234 → „1 KB“. Nur für die Anzeige."""
    if anzahl < 1024:
        return f"{anzahl} B"
    if anzahl < 1024 * 1024:
        return f"{round(anzahl / 1024)} KB"
    return f"{anzahl / (1024 * 1024):.1f} MB".replace(".", ",")
