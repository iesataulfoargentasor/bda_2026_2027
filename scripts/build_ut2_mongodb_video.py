"""Introducción a MongoDB con la voz natural y el diseño de los vídeos de UT2."""
import argparse
import asyncio
import json

import build_ut2_almacenamiento_video as video

video.NAME = "mongodb-explicado"
video.BUILD = video.ROOT / ".venv/ut2-mongodb-video"
video.BUILD.mkdir(parents=True, exist_ok=True)
video.RATE = "+0%"
video.NARRATION_SEPARATOR = "\n\n"
video.PRESERVE_NATURAL_PAUSES = True
video.HEADER = "UT2 · 2.6  /  MONGODB"
video.TRANSCRIPT_TITLE = "UT2 · 2.6 · MONGODB: CONSULTAR, MODIFICAR Y COMPROBAR"
video.SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/mongodb/"
video.TABS = ["PREPARAR", "CONSULTAR", "MODIFICAR", "COMPROBAR"]
video.SCENES = json.loads(
    (video.ROOT / "scripts/ut2_mongodb_video.json").read_text(encoding="utf-8")
)
video.NARRATIONS = [scene["narration"] for scene in video.SCENES]
video.base.BUILD = video.BUILD
video.reference.B = video.BUILD
video.reference.NARRATIONS = video.NARRATIONS

standard_render = video.render


def render(scene, index):
    custom = {"dataset", "hierarchy", "types", "filter", "samecomment", "dates",
              "cursor", "arrayupdate"}
    if scene["kind"] not in custom:
        return standard_render(scene, index)
    image = standard_render(dict(scene, kind="normal", heading="", body=""), index)
    base = video.base
    draw = base.ImageDraw.Draw(image)
    draw.rectangle((44, 290, 1236, 518), fill=base.BG)

    def box(left, top, right, bottom, fill="white"):
        draw.rounded_rectangle((left, top, right, bottom), radius=14,
                               fill=fill, outline="#D7E0DF", width=2)

    def centered(x, y, label, size=27, color=None, width=1190):
        bounds = draw.textbbox((0, 0), label, font=base.font(size, True))
        assert bounds[2] - bounds[0] <= width, label
        draw.text((x, y), label, font=base.font(size, True),
                  fill=color or base.INK, anchor="mt")

    if scene["kind"] == "dataset":
        for position, (number, label) in enumerate([
            ("15", "reservas"), ("6", "opiniones"), ("46", "noches reservadas")
        ]):
            left = 45 + position * 415
            box(left, 302, left + 365, 457)
            centered(left + 182, 314, number, 60, base.TEAL)
            centered(left + 182, 399, label, 28, width=333)
        centered(640, 482, "Seis hoteles · incluidos Noja y Reinosa", 26)

    elif scene["kind"] == "hierarchy":
        for position, (title, example, analogy) in enumerate([
            ("Base", "hotel", "Armario"), ("Colección", "reservas", "Carpeta"),
            ("Documento", "Una reserva", "Ficha"), ("Campo", "noches: 3", "Casilla")
        ]):
            left = 45 + position * 310
            box(left, 314, left + 265, 495)
            centered(left + 132, 331, title, 27, width=237)
            centered(left + 132, 393, example, 29, base.TEAL, width=237)
            centered(left + 132, 451, analogy, 24, base.MUTED, width=237)

    elif scene["kind"] == "types":
        for position, (title, value, detail) in enumerate([
            ("Número", "3", "Permite sumar noches"),
            ("Texto", '"3"', "Es una cadena"),
            ("Fecha BSON", "12 / 04 / 2026", "Se importa como fecha")
        ]):
            left = 45 + position * 415
            box(left, 305, left + 365, 505)
            centered(left + 182, 323, title, 28, width=333)
            centered(left + 182, 379, value, 38, base.TEAL, width=333)
            centered(left + 182, 459, detail, 24, base.MUTED, width=333)

    elif scene["kind"] == "filter":
        for position, label in enumerate(["hotel: Laredo", "canal: web", "noches: al menos 3"]):
            left = 45 + position * 415
            box(left, 300, left + 365, 375)
            centered(left + 182, 323, label, 27, base.TEAL, width=335)
        for x in (227, 642, 1057):
            draw.line((x, 378, x, 408), fill=base.TEAL, width=3)
        box(190, 411, 1090, 508)
        centered(640, 425, "Una reserva cumple las tres condiciones", 28)
        centered(640, 471, "Laredo · web · 3 noches · 186,50 €", 26, base.TEAL)

    elif scene["kind"] == "samecomment":
        centered(640, 298, "Buscamos: autora Ana Ruiz + correo luis@ejemplo.es", 26)
        for row, (author, email, note) in enumerate([
            ("Ana Ruiz", "ana@ejemplo.es", "Coincide el nombre"),
            ("Luis Sainz", "luis@ejemplo.es", "Coincide el correo")
        ]):
            top = 349 + row * 87
            box(65, top, 1215, top + 71)
            centered(220, top + 23, author, 27, base.TEAL, width=270)
            centered(619, top + 25, email, 26, width=410)
            centered(1010, top + 26, note, 23, base.AMBER, width=350)

    elif scene["kind"] == "dates":
        centered(640, 300, "Abril de 2026 · 3 reservas", 31, base.TEAL)
        draw.line((155, 405, 1125, 405), fill=base.TEAL, width=8)
        draw.ellipse((143, 393, 167, 417), fill=base.TEAL)
        draw.ellipse((1113, 393, 1137, 417), fill=base.BG, outline=base.TEAL, width=4)
        centered(245, 350, "Desde: incluido", 27, width=360)
        centered(1025, 350, "Hasta: excluido", 27, width=360)
        centered(245, 445, "1 abril · 00:00 UTC", 27, width=370)
        centered(1025, 445, "1 mayo · 00:00 UTC", 27, width=370)
        centered(640, 486, "Con fechas BSON, no con texto", 24, base.MUTED)

    elif scene["kind"] == "cursor":
        for position, (hotel, amount) in enumerate([
            ("Potes", "490 €"), ("Noja", "210 €"), ("Laredo", "186,50 €"),
            ("Santander", "150 €"), ("Reinosa", "140 €"), ("Comillas", "89,90 €")
        ]):
            left = 45 + position * 200
            color = base.MUTED if position < 4 else base.TEAL
            box(left, 315, left + 185, 464, "#DFE6E3" if position < 4 else "white")
            centered(left + 92, 333, hotel, 25, color, width=167)
            centered(left + 92, 390, amount, 29, color, width=167)
        centered(430, 486, "Saltar 4", 26, base.MUTED, width=750)
        centered(1037, 486, "Quedan 2", 26, base.TEAL, width=370)

    elif scene["kind"] == "arrayupdate":
        for position, (title, value, detail) in enumerate([
            ("Estado inicial", "[ ]", "Lista vacía"),
            ("Primera vez", '[ "parking" ]', "$addToSet incorpora"),
            ("Segunda vez", '[ "parking" ]', "$addToSet no repite")
        ]):
            left = 45 + position * 415
            box(left, 305, left + 365, 505)
            centered(left + 182, 323, title, 28, width=333)
            centered(left + 182, 385, value, 34, base.TEAL, width=333)
            centered(left + 182, 459, detail, 24, base.MUTED, width=333)
    return image


video.render = render

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    arguments = parser.parse_args()
    if arguments.preview:
        video.render_preview()
    else:
        asyncio.run(video.main())
