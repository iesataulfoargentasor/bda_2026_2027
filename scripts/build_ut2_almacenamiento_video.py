"""Genera la introducción de UT2 2.1 con la voz y el diseño de la UT1.

Reutiliza los recursos gráficos, subtítulos y ajuste de pausas del vídeo
de almacenamiento de UT1. Requiere pillow, edge-tts 7.3.1 e imageio-ffmpeg.
"""
import argparse
import asyncio
import hashlib
import json
import math
import unicodedata
from pathlib import Path

import edge_tts

import build_caso_hotel_resumen as base
import build_almacenamiento_revisado_video as reference

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / ".venv/ut2-almacenamiento-video"
OUTPUT = ROOT / "docs/assets/ut2"
NAME = "por-que-almacenamiento"
VOICE = "es-ES-XimenaNeural"
RATE = "-5%"
NARRATION_SEPARATOR = " "
PRESERVE_NATURAL_PAUSES = False
HEADER = "UT2 · 2.1  /  POR QUÉ UN ALMACÉN MASIVO"
TRANSCRIPT_TITLE = "UT2 · 2.1 · POR QUÉ UN ALMACÉN MASIVO"
SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/por-que-almacenamiento/"
TABS = ["EL HOTEL", "LOS DATOS", "EL TIEMPO", "RECUPERACIÓN"]
SCENES = json.loads(
    (ROOT / "scripts/ut2_almacenamiento_video.json").read_text(encoding="utf-8")
)
NARRATIONS = [scene["narration"] for scene in SCENES]
BUILD.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)

# El ajuste de pausas utiliza estas rutas y los límites del nuevo guion.
base.BUILD = BUILD
reference.B = BUILD
reference.NARRATIONS = NARRATIONS


def render(scene, index):
    image = base.Image.new("RGB", (1280, 720), base.BG)
    draw = base.ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1280, 8), fill=base.TEAL)
    base.text(draw, (44, 24), HEADER,
              18, base.MUTED, bold=True)
    draw.text((1235, 25), f"{index + 1} / {len(SCENES)}",
              font=base.font(18), fill=base.MUTED, anchor="ra")
    title_end = base.text(draw, (44, 71), scene["title"], 35, base.INK, 1190, True)
    if title_end > 125:
        raise ValueError(f"Título demasiado largo: {scene['title']}")
    base.text(draw, (46, 130), scene["label"], 23, base.TEAL, 1180)

    for position, name in enumerate(TABS):
        left = 45 + position * 310
        active = scene["active"] == position
        draw.rounded_rectangle((left, 200, left + 265, 263), radius=12,
                               fill=base.TEAL if active else "#DFE6E3")
        draw.text((left + 132, 232), name, font=base.font(21, True),
                  fill="white" if active else base.MUTED, anchor="mm")

    kind = scene["kind"]
    if kind in ("three", "two"):
        count = len(scene["cards"])
        width = 365 if count == 3 else 550
        step = 415 if count == 3 else 600
        for position, (title, body) in enumerate(scene["cards"]):
            base.card(draw, 45 + position * step, 310, width, 185, title, body)
    elif kind == "formula":
        draw.rounded_rectangle((65, 298, 1215, 505), radius=18,
                               fill="white", outline="#D7E0DF", width=2)
        draw.text((640, 330), scene["formula"], font=base.font(42, True),
                  fill=base.TEAL, anchor="mt")
        draw.text((640, 397), scene["heading"], font=base.font(30, True),
                  fill=base.INK, anchor="mt")
        draw.text((640, 455), scene["body"], font=base.font(23),
                  fill=base.MUTED, anchor="mt")
    elif kind == "clock":
        base.card(draw, 65, 305, 510, 190, "23:00 · cierre", "Finanzas fija el corte.")
        base.card(draw, 705, 305, 510, 190, "08:00 · informe", "Gerencia consulta el cierre.")
        base.arrow(draw, 590, 405, 98)
        draw.text((640, 340), "9 h", font=base.font(33, True),
                  fill=base.TEAL, anchor="mt")
    elif kind == "hotels":
        for position, name in enumerate(["Santander", "Laredo", "Comillas", "Potes"]):
            center = 190 + position * 300
            base.hotel(draw, center - 35, 320, base.TEAL if position < 3 else base.AMBER)
            draw.text((center, 425), name, font=base.font(29, True),
                      fill=base.INK, anchor="mt")
    else:
        base.card(draw, 65, 310, 1150, 185, scene["heading"], scene["body"])

    end = base.text(draw, (65, 528), scene["takeaway"], 25, base.INK, 1160, True)
    if end > 582:
        raise ValueError(f"Texto inferior demasiado largo: {scene['title']}")
    draw.rectangle((0, 585, 1280, 720), fill=base.INK)
    draw.rectangle((0, 714, int(1280 * (index + 1) / len(SCENES)), 719), fill=base.TEAL)
    return image


def render_preview():
    sheet = base.Image.new("RGB", (1280, math.ceil(len(SCENES) / 3) * 240), "white")
    for index, scene in enumerate(SCENES):
        slide = render(scene, index)
        slide.save(BUILD / f"{index:02}.png")
        sheet.paste(slide.resize((426, 240)), ((index % 3) * 426, (index // 3) * 240))
    sheet.save(BUILD / "revision-escenas.jpg", quality=95)
    render(SCENES[0], 0).save(OUTPUT / f"{NAME}-portada.jpg", quality=92)
    print(f"Revisadas las dimensiones de {len(SCENES)} escenas.", flush=True)


async def speech():
    narration = NARRATION_SEPARATOR.join(NARRATIONS)
    fingerprint = hashlib.sha256((VOICE + RATE + narration).encode("utf-8")).hexdigest()
    metadata_path = BUILD / "marcas.json"
    audio_path = BUILD / "narracion.mp3"
    if metadata_path.exists() and audio_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata["fingerprint"] == fingerprint:
            print("Reutilizando la narración completa del mismo guion.", flush=True)
            return metadata["events"]

    temporary_audio = BUILD / "narracion-parcial.mp3"
    print(f"Generando narración continua con Ximena, ritmo {RATE}.", flush=True)
    for attempt in range(3):
        try:
            events = []
            with temporary_audio.open("wb") as output:
                stream = edge_tts.Communicate(narration, VOICE, rate=RATE, boundary="WordBoundary")
                async for chunk in stream.stream():
                    if chunk["type"] == "audio":
                        output.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        events.append(chunk)
            words = narration.split()
            if len(events) != len(words):
                raise ValueError(f"Marcas de voz {len(events)} y palabras {len(words)}")
            # El servicio entrega palabras sin puntuación. Conservamos la puntuación del guion.
            def normalized(word):
                return "".join(c for c in unicodedata.normalize("NFKD", word.casefold())
                               if c.isalnum())
            if any(normalized(event["text"]) != normalized(word)
                   for event, word in zip(events, words)):
                raise ValueError("La secuencia de marcas de voz difiere del guion")
            events = [dict(event, text=word) for event, word in zip(events, words)]
            temporary_audio.replace(audio_path)
            metadata_path.write_text(
                json.dumps({"fingerprint": fingerprint, "events": events}, ensure_ascii=False),
                encoding="utf-8",
            )
            return events
        except Exception:
            if attempt == 2:
                raise
            print(f"Reintentando la generación completa de voz ({attempt + 2}/3).", flush=True)
            await asyncio.sleep(2)


async def main():
    render_preview()
    events = await speech()
    if PRESERVE_NATURAL_PAUSES:
        base.run(["-i", "narracion.mp3", "-ac", "1", "-ar", "24000",
                  "-c:a", "pcm_s16le", "narracion.wav"])
        print("Conservadas la entonación y las pausas originales de la voz.", flush=True)
    else:
        events = reference.smooth_audio(events)
    (BUILD / "marcas-ajustadas.json").write_text(
        json.dumps(events, ensure_ascii=False), encoding="utf-8"
    )
    cues = base.captions(events)
    base.write_srt(cues, BUILD / "subtitulos.srt")
    base.write_srt(cues, OUTPUT / f"{NAME}.es.srt")
    vtt = "WEBVTT\n\n" + "\n\n".join(
        f"{base.stamp(start, '.')} --> {base.stamp(end, '.')}\n{text}"
        for start, end, text in cues
    ) + "\n"
    (OUTPUT / f"{NAME}.es.vtt").write_text(vtt, encoding="utf-8")

    starts = [0.0]
    word_index = 0
    for paragraph in NARRATIONS[:-1]:
        word_index += len(paragraph.split())
        before = events[word_index - 1]
        after = events[word_index]
        starts.append(round((before["offset"] + before["duration"] + after["offset"]) / 2e7, 2))
    duration = math.ceil((base.duration(BUILD / "narracion.wav") + 0.5) * 25) / 25
    boundaries = starts + [duration]
    concat = []
    chapters = []
    for index, scene in enumerate(SCENES):
        concat.extend([f"file '{index:02}.png'",
                       f"duration {boundaries[index + 1] - boundaries[index]:.3f}"])
        chapters.append({"inicio": starts[index], "titulo": scene["title"]})
    concat.append(f"file '{len(SCENES) - 1:02}.png'")
    (BUILD / "imagenes.txt").write_text("\n".join(concat), encoding="utf-8")
    (BUILD / "capitulos.json").write_text(
        json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    transcript = (
        f"{TRANSCRIPT_TITLE}\n"
        "BDA · IES Ataúlfo Argenta\n"
        "Voz sintética Ximena, español de España. Ejemplos ficticios.\n"
        f"Fuente: {SOURCE_URL}\n\n"
    )
    transcript += "\n\n".join(
        f"{base.stamp(chapter['inicio'], '.')[:8]} · {scene['title']}\n{scene['narration']}"
        for chapter, scene in zip(chapters, SCENES)
    )
    (OUTPUT / f"{NAME}.txt").write_text(transcript + "\n", encoding="utf-8")

    style = ("FontName=Segoe UI,FontSize=13,PrimaryColour=&H00FFFFFF,"
             "OutlineColour=&H00432D14,BorderStyle=1,Outline=1,Shadow=0,"
             "Alignment=2,MarginV=20")
    print(f"Montando {duration:.2f} segundos con {len(cues)} subtítulos.", flush=True)
    temporary_video = BUILD / "video-completo.mp4"
    base.run([
        "-f", "concat", "-safe", "0", "-i", "imagenes.txt", "-i", "narracion.wav",
        "-vf", f"fps=25,subtitles=subtitulos.srt:force_style='{style}'",
        "-af", "loudnorm=I=-18:TP=-1.5:LRA=11,apad",
        "-t", str(duration), "-c:v", "libx264", "-preset", "veryfast",
        "-tune", "stillimage", "-crf", "23", "-threads", "4", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(temporary_video),
    ])
    temporary_video.replace(OUTPUT / f"{NAME}.mp4")
    print(f"Completado. Duración {duration:.2f} s. "
          f"Tamaño {(OUTPUT / (NAME + '.mp4')).stat().st_size / 1024**2:.1f} MiB.",
          flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    arguments = parser.parse_args()
    if arguments.preview:
        render_preview()
    else:
        asyncio.run(main())
