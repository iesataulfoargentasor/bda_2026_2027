"""MongoDB y Python con la voz natural y el diseño de los vídeos de UT2."""
import argparse
import asyncio
import json

import build_ut2_almacenamiento_video as video

video.NAME = "mongodb-python"
video.BUILD = video.ROOT / ".venv/ut2-pymongo-video"
video.BUILD.mkdir(parents=True, exist_ok=True)
video.RATE = "+0%"
video.NARRATION_SEPARATOR = "\n\n"
video.PRESERVE_NATURAL_PAUSES = True
video.HEADER = "UT2 · 2.9  /  MONGODB Y PYTHON"
video.TRANSCRIPT_TITLE = "UT2 · 2.9 · MONGODB Y PYTHON: DEL PARTE A LA APLICACIÓN"
video.SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/pymongo/"
video.TABS = ["CONECTAR", "CONSULTAR", "MODIFICAR", "COMPROBAR"]
video.SCENES = json.loads(
    (video.ROOT / "scripts/ut2_pymongo_video.json").read_text(encoding="utf-8")
)
video.NARRATIONS = [scene["narration"] for scene in video.SCENES]
video.base.BUILD = video.BUILD
video.reference.B = video.BUILD
video.reference.NARRATIONS = video.NARRATIONS
standard_render = video.render


def render(scene, index):
    if scene["kind"] not in {"flow", "metrics", "cursor", "ledger", "ranking", "parking"}:
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

    if scene["kind"] in {"flow", "metrics"}:
        flow = scene["kind"] == "flow"
        width, step = (300, 445) if flow else (365, 415)
        for pos, (title, middle, bottom) in enumerate(scene["steps"]):
            left = 45 + pos * step
            box(left, 305, left + width, 508)
            centered(left + width // 2, 322, title, 28, width=width - 28)
            centered(left + width // 2, 390, middle, 25 if flow else 32,
                     base.TEAL, width=width - 28)
            centered(left + width // 2, 463, bottom, 22, base.MUTED, width=width - 28)
            if flow and pos < 2:
                base.arrow(draw, left + width + 18, 409, length=105)

    elif scene["kind"] == "cursor":
        for pos, (title, detail) in enumerate([
            ("MongoDB", "Resultado filtrado"), ("Lotes", "Fichas según avance"),
            ("Python", "Procesa cada ficha")
        ]):
            left = 45 + pos * 445
            box(left, 305, left + 300, 508)
            centered(left + 150, 322, title, 29, width=272)
            if pos == 1:
                for k in range(3):
                    box(left + 52 + k * 13, 376 + k * 6, left + 220 + k * 13,
                        422 + k * 6, "#DFE6E3")
            else:
                centered(left + 150, 389, "DOCUMENTOS" if pos == 0 else "1 → 2 → 3", 27,
                         base.TEAL, width=272)
            centered(left + 150, 465, detail, 22, base.MUTED, width=272)
            if pos < 2:
                base.arrow(draw, left + 318, 409, length=105)

    elif scene["kind"] == "ledger":
        centered(640, 297, "Parte de gerencia · Todos los canales", 30, base.TEAL)
        for pos, (hotel, nights) in enumerate([
            ("Comillas", "4"), ("Laredo", "11"), ("Noja", "4"),
            ("Potes", "13"), ("Reinosa", "6"), ("Santander", "8")
        ]):
            left = 45 + pos * 200
            box(left, 355, left + 185, 502)
            centered(left + 92, 372, hotel, 25, width=165)
            centered(left + 92, 426, nights, 43, base.TEAL, width=165)

    elif scene["kind"] == "ranking":
        for pos, (title, values, note) in enumerate([
            ("Filtrar Potes", "124 · 490 · 280", "Importes de las reservas"),
            ("Ordenar", "490 · 280 · 124", "De mayor a menor"),
            ("Limitar a 2", "490 · 280", "Resultado esperado")
        ]):
            left = 45 + pos * 445
            box(left, 305, left + 300, 508)
            centered(left + 150, 322, title, 28, width=272)
            centered(left + 150, 389, values, 30, base.TEAL, width=272)
            centered(left + 150, 464, note, 22, base.MUTED, width=272)
            if pos < 2:
                base.arrow(draw, left + 318, 409, length=105)

    elif scene["kind"] == "parking":
        box(45, 302, 1235, 508, "#DFE6E3")
        centered(640, 314, "UNA TRANSACCIÓN", 27, base.TEAL)
        for left, title, before, after in [
            (75, "Cupo de parking", "1 plaza libre", "0 plazas libres"),
            (705, "Libro de reservas", "Sin reserva nueva", "1 reserva nueva")
        ]:
            box(left, 358, left + 500, 488)
            centered(left + 250, 369, title, 27, width=470)
            centered(left + 120, 430, before, 23, width=225)
            base.arrow(draw, left + 247, 447, length=34)
            centered(left + 380, 430, after, 23, base.TEAL, width=225)
        centered(640, 408, "+", 43, base.TEAL, width=95)
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
