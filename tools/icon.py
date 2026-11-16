"""Erzeugt das Integrations-Icon (brand/icon.png, icon@2x.png, dark_icon*.png): python tools/icon.py"""
import math
import pathlib

from PIL import Image, ImageDraw

ZIEL = pathlib.Path(__file__).parents[1] / "custom_components" / "rollladensteuerung" / "brand"
N = 1024  # gezeichnet wird groß, dann verkleinert (Kantenglättung)


def zeichnen(dunkel: bool) -> Image.Image:
    bild = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(bild)
    rahmen = (176, 190, 197) if dunkel else (69, 90, 100)

    # Sonne oben rechts, teilweise hinter dem Fenster
    sx, sy, sr = 770, 245, 135
    for i in range(12):
        w = math.radians(i * 30 + 15)
        d.line([(sx + math.cos(w) * (sr + 30), sy + math.sin(w) * (sr + 30)),
                (sx + math.cos(w) * (sr + 95), sy + math.sin(w) * (sr + 95))], fill=(255, 179, 0), width=34)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 193, 7))

    # Fenster mit Glas
    x0, y0, x1, y1 = 120, 250, 740, 930
    d.rounded_rectangle([x0, y0, x1, y1], radius=56, fill=rahmen)
    innen = [x0 + 44, y0 + 44, x1 - 44, y1 - 44]
    d.rounded_rectangle(innen, radius=22, fill=(179, 229, 252))
    # Fensterkreuz
    mx = (innen[0] + innen[2]) // 2
    d.rectangle([mx - 14, innen[1], mx + 14, innen[3]], fill=rahmen)

    # Rollladenkasten
    d.rounded_rectangle([x0 - 30, y0 - 70, x1 + 30, y0 + 40], radius=30, fill=(94, 53, 177))

    # Lamellen bis gut zur Hälfte herunter
    unten = innen[1] + int((innen[3] - innen[1]) * 0.58)
    y = innen[1]
    while y < unten:
        d.rounded_rectangle([innen[0] - 6, y, innen[2] + 6, min(y + 50, unten)], radius=10, fill=(149, 117, 205))
        d.line([(innen[0] + 10, y + 50), (innen[2] - 10, y + 50)], fill=(94, 53, 177), width=8)
        y += 62
    # Unterleiste
    d.rounded_rectangle([innen[0] - 10, unten - 6, innen[2] + 10, unten + 26], radius=12, fill=(94, 53, 177))
    return bild


ZIEL.mkdir(exist_ok=True)
for dunkel, name in ((False, "icon"), (True, "dark_icon")):
    gross = zeichnen(dunkel)
    gross.resize((512, 512), Image.LANCZOS).save(ZIEL / f"{name}@2x.png", optimize=True)
    gross.resize((256, 256), Image.LANCZOS).save(ZIEL / f"{name}.png", optimize=True)
print("ok", sorted(p.name for p in ZIEL.iterdir()))
