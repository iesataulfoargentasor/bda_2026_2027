"""Introducción a las familias NoSQL con la voz y el diseño natural de UT2."""
import argparse
import asyncio
import json

import build_ut2_almacenamiento_video as video

video.NAME = "familias-nosql"
video.BUILD = video.ROOT / ".venv/ut2-nosql-video"
video.BUILD.mkdir(parents=True, exist_ok=True)
video.RATE = "+0%"
video.NARRATION_SEPARATOR = "\n\n"
video.PRESERVE_NATURAL_PAUSES = True
video.HEADER = "UT2 · 2.5  /  FAMILIAS NoSQL"
video.TRANSCRIPT_TITLE = "UT2 · 2.5 · FAMILIAS NoSQL: CONSULTAS, MODELOS Y GARANTÍAS"
video.SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/nosql/"
video.TABS = ["LA PREGUNTA", "CUATRO FAMILIAS", "LAS GARANTÍAS", "ELEGIR"]
video.SCENES = json.loads(
    (video.ROOT / "scripts/ut2_nosql_video.json").read_text(encoding="utf-8")
)
video.NARRATIONS = [scene["narration"] for scene in video.SCENES]
video.base.BUILD = video.BUILD
video.reference.B = video.BUILD
video.reference.NARRATIONS = video.NARRATIONS

standard_render = video.render


def render(scene, index):
    custom = {"families", "keyvalue", "document", "measurements", "graph", "acid",
              "shards", "cap", "stores", "decision"}
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

    def four_cards(entries):
        for position, (title, line1, line2) in enumerate(entries):
            left = 45 + position * 310
            box(left, 307, left + 265, 505)
            title_end = base.text(draw, (left + 17, 326), title, 26, base.INK, 231, True)
            assert title_end < 398, title
            centered(left + 132, 414, line1, 23, base.TEAL, width=237)
            centered(left + 132, 455, line2, 22, base.MUTED, width=237)

    if scene["kind"] == "families":
        four_cards([("Clave-valor", "Un ticket", "Sesión por clave"),
                    ("Documento", "Una ficha", "Reserva y extras"),
                    ("Familias de columnas", "Un cuaderno", "Medidas por periodo"),
                    ("Grafo", "Un mapa", "Relaciones")])

    elif scene["kind"] == "keyvalue":
        box(65, 312, 505, 493)
        centered(285, 331, "Ticket / clave conocida", 27, width=405)
        centered(285, 397, "S-991", 44, base.TEAL)
        base.arrow(draw, 535, 405, length=140)
        box(705, 312, 1215, 493)
        centered(960, 331, "Valor asociado", 27)
        centered(960, 399, "Sesión del huésped", 31, base.TEAL, width=470)

    elif scene["kind"] == "document":
        box(45, 296, 1235, 513)
        centered(640, 307, "Reserva · ficha conceptual", 28)
        for position, (title, value) in enumerate([
            ("Estancia", "Laredo · 3 noches"), ("Huésped", "Ana"),
            ("Extras", "Solicita parking")
        ]):
            left = 68 + 396 * position
            box(left, 365, left + 353, 490, "#F5F2EA")
            centered(left + 176, 379, title, 25)
            centered(left + 176, 435, value, 27, base.TEAL, width=322)

    elif scene["kind"] == "measurements":
        box(45, 303, 530, 510)
        centered(287, 319, "Clave de partición ilustrativa", 25, width=453)
        centered(287, 384, "Laredo · 214 · 01/04/2026", 27, base.TEAL, width=453)
        centered(287, 455, "Hotel · Habitación · Día", 25, width=453)
        base.arrow(draw, 551, 405, length=58)
        box(630, 303, 1235, 510)
        centered(932, 316, "Medidas ordenadas por instante", 26, width=570)
        for row, (time, temperature) in enumerate([("08:00", "21,4 °C"),
                                                  ("08:05", "21,6 °C"),
                                                  ("08:10", "21,5 °C")]):
            centered(932, 367 + row * 43, f"{time}  →  {temperature}", 27, base.TEAL)

    elif scene["kind"] == "graph":
        centered(640, 302, "Luis → su amiga Ana → hotel recomendado por Ana", 28)
        for left, label in [(45, "Luis"), (490, "Ana"), (935, "Hotel Potes")]:
            box(left, 390, left + 300, 493)
            centered(left + 150, 423, label, 32, base.TEAL, width=270)
        for left, label in [(365, "AMIGO"), (810, "RECOMENDÓ")]:
            centered(left + 52, 352, label, 20, width=142)
            base.arrow(draw, left, 443, length=105)

    elif scene["kind"] == "acid":
        four_cards([("A · Atomicidad", "Todo o nada", "Cambios relacionados"),
                    ("C · Consistencia", "Cumplir reglas", "Invariantes definidos"),
                    ("I · Aislamiento", "Interferencias", "Según el nivel"),
                    ("D · Durabilidad", "Lo confirmado", "Fallos cubiertos")])

    elif scene["kind"] == "shards":
        for position, name in enumerate(["A", "B", "C"]):
            left = 45 + position * 415
            centered(left + 182, 297, f"Shard {name} · 30 GB lógicos", 25, width=365)
            for row, label in enumerate(["Copia 1 · 30 GB", "Copia 2 · 30 GB"]):
                top = 345 + row * 88
                box(left, top, left + 365, top + 72)
                centered(left + 182, top + 19, label, 28, base.TEAL, width=330)

    elif scene["kind"] == "cap":
        centered(640, 297, "Una plaza disponible · dos solicitudes de confirmación", 28)
        for left, title in [(45, "Grupo de nodos A"), (835, "Grupo de nodos B")]:
            box(left, 354, left + 400, 509)
            centered(left + 200, 369, title, 27, width=368)
            centered(left + 200, 421, "Solicita confirmar", 25, base.TEAL, width=368)
            centered(left + 200, 460, "la última plaza", 25, base.TEAL, width=368)
        centered(640, 366, "Sin comunicación", 24, base.AMBER, width=330)
        draw.line((475, 447, 607, 447), fill=base.MUTED, width=4)
        draw.line((673, 447, 805, 447), fill=base.MUTED, width=4)
        draw.line((624, 431, 656, 463), fill=base.AMBER, width=5)
        draw.line((624, 463, 656, 431), fill=base.AMBER, width=5)

    elif scene["kind"] == "stores":
        four_cards([("Cobros", "Relacional", "Transacciones"),
                    ("Fichas", "Documental", "Consultas previstas"),
                    ("Sesiones", "Clave-valor", "Caducidad definida"),
                    ("Histórico", "HDFS / objetos", "Archivos conservados")])

    elif scene["kind"] == "decision":
        entries = [("Dato", "Sesión"), ("Consulta", "Por identificador"),
                   ("Garantía", "Puede caducar"), ("Modelo", "Clave-valor"),
                   ("Coste", "Reconstrucción")]
        for position, (title, value) in enumerate(entries):
            left = 45 + position * 240
            box(left, 323, left + 225, 482)
            centered(left + 112, 345, title, 27, width=199)
            centered(left + 112, 416, value, 23, base.TEAL, width=203)
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
