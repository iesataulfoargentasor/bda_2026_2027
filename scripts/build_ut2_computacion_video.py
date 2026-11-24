"""Introducción a computación distribuida con el estilo y la voz natural de UT2."""
import argparse
import asyncio
import json

import build_ut2_almacenamiento_video as video

video.NAME = "computacion-distribuida"
video.BUILD = video.ROOT / ".venv/ut2-computacion-video"
video.BUILD.mkdir(parents=True, exist_ok=True)
video.RATE = "+0%"
video.NARRATION_SEPARATOR = "\n\n"
video.PRESERVE_NATURAL_PAUSES = True
video.HEADER = "UT2 · 2.4  /  COMPUTACIÓN DISTRIBUIDA"
video.TRANSCRIPT_TITLE = "UT2 · 2.4 · COMPUTACIÓN DISTRIBUIDA: REPARTIR, COMPROBAR Y MEDIR"
video.SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/computacion-distribuida/"
video.TABS = ["EL TRABAJO", "MAPREDUCE", "COMPROBAR", "MEDIR"]
video.SCENES = json.loads(
    (video.ROOT / "scripts/ut2_computacion_video.json").read_text(encoding="utf-8")
)
video.NARRATIONS = [scene["narration"] for scene in video.SCENES]
video.base.BUILD = video.BUILD
video.reference.B = video.BUILD
video.reference.NARRATIONS = video.NARRATIONS

standard_render = video.render


def render(scene, index):
    custom = {"queue", "partials", "shuffle", "average", "totals", "workers", "medians"}
    if scene["kind"] not in custom:
        return standard_render(scene, index)
    image = standard_render(dict(scene, kind="normal", heading="", body=""), index)
    base = video.base
    draw = base.ImageDraw.Draw(image)
    draw.rectangle((44, 290, 1236, 518), fill=base.BG)

    def box(left, top, right, bottom, fill="white"):
        draw.rounded_rectangle((left, top, right, bottom), radius=14,
                               fill=fill, outline="#D7E0DF", width=2)

    def centered(x, y, label, size=27, color=None):
        assert draw.textbbox((0, 0), label, font=base.font(size, True))[2] <= 1190, label
        draw.text((x, y), label, font=base.font(size, True),
                  fill=color or base.INK, anchor="mt")

    if scene["kind"] == "queue":
        centered(640, 292, "Un nodo · dos tareas simultáneas · duraciones simplificadas", 25)
        for column in range(3):
            left = 275 + column * 310
            centered(left + 130, 338, f"Turno {column + 1}", 22, base.MUTED)
            for row in range(2):
                top = 374 + row * 70
                box(left, top, left + 260, top + 56)
                centered(left + 130, top + 11, f"Map {column * 2 + row + 1}", 27, base.TEAL)
        centered(151, 388, "Puesto 1", 25)
        centered(151, 458, "Puesto 2", 25)

    elif scene["kind"] == "partials":
        for left, title, expression in [(65, "Primer grupo", "3 + 2 = 5"),
                                        (665, "Segundo grupo", "1 + 4 + 2 = 7")]:
            box(left, 304, left + 550, 441)
            centered(left + 275, 322, title, 27)
            centered(left + 275, 369, expression, 37, base.TEAL)
        centered(640, 465, "Reunimos: 5 + 7 = 12 noches de Laredo", 32)

    elif scene["kind"] == "shuffle":
        box(45, 303, 435, 507)
        centered(240, 316, "Dos mappers ilustrativos", 24)
        centered(240, 365, "A: Laredo 3 · Potes 5", 25, base.TEAL)
        centered(240, 419, "B: Laredo 2", 25, base.TEAL)
        base.arrow(draw, 465, 403, length=115)
        box(610, 303, 1235, 395)
        box(610, 415, 1235, 507)
        centered(922, 329, "Laredo  →  [3, 2]", 32)
        centered(922, 441, "Potes  →  [5]", 32)

    elif scene["kind"] == "average":
        for left, title, values in [(65, "Grupo [2, 4]", "Suma 6 · Recuento 2"),
                                    (665, "Grupo [10]", "Suma 10 · Recuento 1")]:
            box(left, 304, left + 550, 441)
            centered(left + 275, 322, title, 29)
            centered(left + 275, 378, values, 27, base.TEAL)
        centered(640, 465, "Media conjunta: (6 + 10) / (2 + 1)", 32)

    elif scene["kind"] == "totals":
        for position, (hotel, nights) in enumerate([
            ("Comillas", 11), ("Laredo", 12), ("Noja", 15), ("Potes", 14), ("Santander", 10)
        ]):
            left = 45 + position * 240
            box(left, 304, left + 225, 452)
            centered(left + 112, 327, hotel, 25)
            centered(left + 112, 377, str(nights), 43, base.TEAL)
        centered(640, 472, "20 reservas  →  5 hoteles  →  62 noches", 30)

    elif scene["kind"] == "workers":
        for left, title, nodes in [(45, "A · un trabajador", ["NodeManager 1"]),
                                  (665, "B · dos trabajadores", ["NodeManager 1", "NodeManager 2"])]:
            box(left, 303, left + 570, 453)
            centered(left + 285, 317, title, 29)
            for number, label in enumerate(nodes):
                x = left + 32 + number * 267
                box(x, 375, x + 240, 432, "#DFE6E3")
                centered(x + 120, 390, label, 23, base.TEAL)
        centered(640, 477, "HDFS y ordenador físico compartidos en ambas configuraciones", 26)

    elif scene["kind"] == "medians":
        for left, title, values, median in [(65, "Configuración A", "118 · 120 · 123 s", "120 s"),
                                            (665, "Configuración B", "79 · 80 · 84 s", "80 s")]:
            box(left, 303, left + 550, 510)
            centered(left + 275, 320, title, 29)
            centered(left + 275, 375, values, 32)
            centered(left + 275, 437, f"Mediana: {median}", 31, base.TEAL)
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
