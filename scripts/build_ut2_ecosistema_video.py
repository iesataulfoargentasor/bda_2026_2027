"""Introducción al ecosistema Hadoop: mismo montaje, voz y diseño que UT2 2.1."""
import argparse
import asyncio
import json

import build_ut2_almacenamiento_video as video

video.NAME = "ecosistema-hadoop"
video.BUILD = video.ROOT / ".venv/ut2-ecosistema-video"
video.BUILD.mkdir(parents=True, exist_ok=True)
video.HEADER = "UT2 · 2.2  /  ECOSISTEMA HADOOP"
video.TRANSCRIPT_TITLE = "UT2 · 2.2 · ECOSISTEMA HADOOP"
video.SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/ecosistema/"
video.TABS = ["EL HOTEL", "LAS PIEZAS", "EL CÁLCULO", "COMPROBAR"]
video.SCENES = json.loads(
    (video.ROOT / "scripts/ut2_ecosistema_video.json").read_text(encoding="utf-8")
)
video.NARRATIONS = [scene["narration"] for scene in video.SCENES]
video.base.BUILD = video.BUILD
video.reference.B = video.BUILD
video.reference.NARRATIONS = video.NARRATIONS

standard_render = video.render


def render(scene, index):
    if scene["kind"] != "totals":
        return standard_render(scene, index)
    # Cinco subtotales en una sola fila, con el total y su ámbito bien visibles.
    image = standard_render(dict(scene, kind="normal", heading="", body=""), index)
    base = video.base
    draw = base.ImageDraw.Draw(image)
    draw.rectangle((44, 290, 1236, 518), fill=base.BG)
    for position, (hotel, nights) in enumerate(scene["totals"]):
        left = 45 + 240 * position
        draw.rounded_rectangle((left, 304, left + 225, 452), radius=15,
                               fill="white", outline="#D7E0DF", width=2)
        draw.text((left + 112, 328), hotel, font=base.font(25, True),
                  fill=base.INK, anchor="mt")
        draw.text((left + 112, 377), str(nights), font=base.font(43, True),
                  fill=base.TEAL, anchor="mt")
    draw.text((640, 472), "20 reservas  →  5 hoteles  →  62 noches",
              font=base.font(30, True), fill=base.INK, anchor="mt")
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
