"""Introducción a HDFS con la voz y el diseño conversacional de UT2 2.2."""
import argparse
import asyncio
import json

import build_ut2_almacenamiento_video as video

video.NAME = "hdfs-explicado"
video.BUILD = video.ROOT / ".venv/ut2-hdfs-video"
video.BUILD.mkdir(parents=True, exist_ok=True)
video.RATE = "+0%"
video.NARRATION_SEPARATOR = "\n\n"
video.PRESERVE_NATURAL_PAUSES = True
video.HEADER = "UT2 · 2.3  /  HDFS"
video.TRANSCRIPT_TITLE = "UT2 · 2.3 · HDFS: BLOQUES, RÉPLICAS Y RECUPERACIÓN"
video.SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/hdfs/"
video.TABS = ["EL ARCHIVO", "BLOQUES Y COPIAS", "LEER Y ESCRIBIR", "COMPROBAR"]
video.SCENES = json.loads(
    (video.ROOT / "scripts/ut2_hdfs_video.json").read_text(encoding="utf-8")
)
video.NARRATIONS = [scene["narration"] for scene in video.SCENES]
video.base.BUILD = video.BUILD
video.reference.B = video.BUILD
video.reference.NARRATIONS = video.NARRATIONS

standard_render = video.render


def render(scene, index):
    if scene["kind"] not in {"blocks", "replicas", "read", "write"}:
        return standard_render(scene, index)
    image = standard_render(dict(scene, kind="normal", heading="", body=""), index)
    base = video.base
    draw = base.ImageDraw.Draw(image)
    draw.rectangle((44, 290, 1236, 518), fill=base.BG)

    def box(left, top, right, bottom):
        draw.rounded_rectangle((left, top, right, bottom), radius=15,
                               fill="white", outline="#D7E0DF", width=2)

    def centered(x, y, label, size=26, color=None):
        draw.text((x, y), label, font=base.font(size, True),
                  fill=color or base.INK, anchor="mt")

    if scene["kind"] == "blocks":
        for position, size in enumerate([128, 128, 128, 128, 88]):
            left = 45 + 240 * position
            box(left, 309, left + 225, 450)
            centered(left + 112, 329, f"Bloque {position + 1}", 25)
            centered(left + 112, 380, f"{size} MiB", 35,
                     base.AMBER if position == 4 else base.TEAL)
        centered(640, 474, "128 + 128 + 128 + 128 + 88 = 600 MiB", 29)

    elif scene["kind"] == "replicas":
        for position, node in enumerate(["A", "B", "C"]):
            left = 45 + 415 * position
            box(left, 296, left + 365, 513)
            centered(left + 182, 307, f"DataNode {node}", 27)
            for block, size in enumerate([128, 128, 128, 128, 88]):
                top = 350 + block * 30
                color = base.AMBER if block == 4 else base.TEAL
                draw.rounded_rectangle((left + 23, top, left + 342, top + 26),
                                       radius=5, fill="#F5F2EA")
                centered(left + 182, top, f"B{block + 1}  ·  {size} MiB", 20, color)

    elif scene["kind"] == "read":
        for top, source, label, color in [
            (307, "NameNode", "1. Ubicaciones", base.TEAL),
            (423, "DataNode", "2. Bytes del bloque", base.AMBER),
        ]:
            box(65, top, 420, top + 83)
            box(860, top, 1215, top + 83)
            centered(242, top + 23, source, 29)
            centered(1037, top + 23, "Cliente", 29)
            centered(640, top - 1, label, 23, color)
            draw.line((445, top + 55, 835, top + 55), fill=color, width=5)
            draw.polygon([(835, top + 55), (819, top + 45),
                          (819, top + 65)], fill=color)

    elif scene["kind"] == "write":
        centered(640, 296, "El NameNode indica los destinos del bloque.", 26)
        for position, label in enumerate(["Cliente", "DataNode A", "DataNode B", "DataNode C"]):
            left = 45 + 310 * position
            box(left, 351, left + 265, 428)
            centered(left + 132, 374, label, 27)
            if position < 3:
                base.arrow(draw, left + 275, 390, length=25)
        centered(640, 446, "Confirmaciones hacia el cliente", 25, base.AMBER)
        draw.line((1105, 495, 177, 495), fill=base.AMBER, width=5)
        draw.polygon([(177, 495), (193, 485), (193, 505)], fill=base.AMBER)
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
