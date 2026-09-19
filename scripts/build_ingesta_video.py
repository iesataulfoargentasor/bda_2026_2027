"""Monta el vídeo de estudio de 1.6 Ingesta (diapositivas + narración en español)."""
from __future__ import annotations

import asyncio
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets" / "ut1"
BRAND = ROOT / "docs" / "assets" / "branding" / "logo-ies-ataulfo-argenta.png"
BUILD = ROOT / "scripts" / "_ingesta_video"
OUT = ASSETS / "ingesta-estudio.mp4"

W, H = 1280, 720
NAVY = (0, 0, 0)
GARNET = (155, 0, 0)
INK = (43, 43, 43)
MUTED = (90, 90, 90)
WHITE = (255, 255, 255)
PAPER = (250, 250, 248)
VOICE = "es-ES-ElviraNeural"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    path = Path(r"C:\Windows\Fonts") / name
    return ImageFont.truetype(str(path), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def fit_image(path: Path, box: tuple[int, int, int, int]) -> Image.Image:
    img = Image.open(path).convert("RGBA")
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    img.thumbnail((bw, bh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ox = (bw - img.width) // 2
    oy = (bh - img.height) // 2
    canvas.paste(img, (ox, oy), img)
    return canvas


def base_slide(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 88], fill=NAVY)
    d.rectangle([0, 88, W, 92], fill=GARNET)
    d.rectangle([0, H - 48, W, H], fill=NAVY)
    tf = font(32, True)
    d.text((28, 24), title, font=tf, fill=WHITE)
    if BRAND.exists():
        logo = Image.open(BRAND).convert("RGBA")
        logo.thumbnail((56, 56), Image.Resampling.LANCZOS)
        im.paste(logo, (W - 76, 16), logo)
    foot = font(16)
    d.text(
        (28, H - 34),
        "BDA  ·  1.6 Ingesta de datos  ·  IES Ataúlfo Argenta",
        font=foot,
        fill=WHITE,
    )
    return im, d


def bullets_slide(title: str, lines: list[str]) -> Image.Image:
    im, d = base_slide(title)
    fnt = font(30)
    y = 130
    for line in lines:
        for wrapped in wrap(d, "•  " + line, fnt, W - 100):
            d.text((56, y), wrapped, font=fnt, fill=INK)
            y += 46
        y += 8
    return im


def diagram_slide(title: str, image: Path) -> Image.Image:
    im, _d = base_slide(title)
    fitted = fit_image(image, (40, 112, W - 40, H - 64))
    im.paste(fitted, (40, 112), fitted)
    return im


def title_slide() -> Image.Image:
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.rectangle([0, H - 12, W, H], fill=GARNET)
    if BRAND.exists():
        logo = Image.open(BRAND).convert("RGBA")
        logo.thumbnail((96, 96), Image.Resampling.LANCZOS)
        im.paste(logo, ((W - logo.width) // 2, 70), logo)
    d.text((W // 2, 200), "Big Data Aplicado", font=font(28), fill=(200, 200, 200), anchor="mt")
    d.text((W // 2, 280), "1.6  Ingesta de datos", font=font(54, True), fill=WHITE, anchor="mt")
    d.text(
        (W // 2, 380),
        "Vídeo de apoyo para estudiar",
        font=font(28),
        fill=(230, 180, 180),
        anchor="mt",
    )
    d.text(
        (W // 2, 520),
        "IES Ataúlfo Argenta  ·  curso 2026/2027",
        font=font(22),
        fill=(180, 180, 180),
        anchor="mt",
    )
    d.text(
        (W // 2, 570),
        "No sustituye los apuntes ni Moodle",
        font=font(18),
        fill=(140, 140, 140),
        anchor="mt",
    )
    return im


SLIDES: list[dict] = [
    {
        "id": "00",
        "kind": "title",
        "title": "1.6 Ingesta de datos",
        "narration": (
            "Apuntes de Big Data Aplicado, del IES Ataúlfo Argenta. "
            "Unidad 1, apartado 1.6: ingesta de datos. "
            "Este vídeo resume el tema para estudiar. El detalle, los talleres y las actividades están en la página de apuntes. "
            "No sustituye a Moodle."
        ),
    },
    {
        "id": "01",
        "kind": "diagram",
        "title": "Qué es ingerir datos",
        "image": "ingesta-hotel.png",
        "narration": (
            "Ingerir datos es coger información que ya existe en varios sitios y llevarla a otro sistema. "
            "En el grupo hotelero, recepción pica reservas en el programa del hotel, la pasarela sabe qué se ha cobrado, "
            "y hay sensores de ocupación. Dirección quiere, cada mañana a las 8, ocupación e importe cobrado por hotel. "
            "Esos datos ya existen. No están, de entrada, donde gerencia los mira. Llevarlos de un sitio al otro es ingesta."
        ),
    },
    {
        "id": "02",
        "kind": "bullets",
        "title": "Empieza por el problema, no por la herramienta",
        "bullets": [
            "Diseña hacia atrás: destino, transformación, origen.",
            "¿Qué tiene que ver gerencia a las 8?",
            "¿Hay que cruzar reservas con cobros?",
            "¿El dato vive en el PMS, la pasarela, el FTP o el sensor?",
            "El lago guarda el bruto. El almacén de informes, el dato limpio.",
        ],
        "narration": (
            "Antes de elegir un programa, diseñas hacia atrás. Primero: qué tiene que ver gerencia a las 8. "
            "Segundo: hay que cruzar reservas con cobros, quitar canceladas, unificar el nombre del canal. "
            "Tercero: dónde vive el dato. "
            "El lago de datos guarda lo ingerido en bruto. El almacén de informes es otro sitio, con el dato ya limpio para el panel. "
            "La ingesta suele aterrizar primero en el lago."
        ),
    },
    {
        "id": "03",
        "kind": "diagram",
        "title": "Pipeline: fases, no un producto",
        "image": "pipeline.png",
        "narration": (
            "Un pipeline, o tubería, organiza el trabajo en fases. No es un producto que compras. "
            "En el hotel: recoger el hecho fuera de recepción, guardar un colchón por si el destino va lento, "
            "procesar —filtrar, cruzar, sumar— y dejar algo útil: el panel de las 8. "
            "Un mismo job que lo hace todo parece simple el día 1. El martes que añaden una columna, se rompe todo a la vez."
        ),
    },
    {
        "id": "04",
        "kind": "diagram",
        "title": "OLTP opera; OLAP informa",
        "image": "oltp-olap.png",
        "narration": (
            "Si sumas importes sobre el programa que cobra, el mostrador espera. "
            "Por eso se copia el hecho. O L T P es operar el día a día: picar la reserva. "
            "O L A P es analizar e informar: el panel de Santander, Laredo, Comillas y Potes. "
            "Son dos oficios. El pipeline los separa para que uno no tumbe al otro."
        ),
    },
    {
        "id": "05",
        "kind": "bullets",
        "title": "Pipeline no es lo mismo que E T L",
        "bullets": [
            "Toda E T L es un pipeline: mueve datos en fases.",
            "No todo pipeline es una E T L.",
            "Una cola con un filtro también es tubería.",
            "Data wrangling: dejar el dato listo para usarlo.",
        ],
        "narration": (
            "Aunque se intercambian los términos, pipeline y E T L no son lo mismo. "
            "Toda E T L es un pipeline. No todo pipeline es una E T L. "
            "Un sensor que deja un mensaje en una cola y un filtro que tira duplicados también es tubería, "
            "aunque no hagas un cruce ni una carga a un almacén de informes."
        ),
    },
    {
        "id": "06",
        "kind": "diagram",
        "title": "Quién inicia: push, pull y poll",
        "image": "push-pull-poll.png",
        "narration": (
            "Hay tres formas de iniciar el movimiento. No son tres productos. "
            "Push: el origen envía. Ejemplo: cada alta de reserva. "
            "Pull: el destino va a buscar. Ejemplo: el volcado a las 2 de la madrugada. "
            "Poll: el destino pregunta de vez en cuando; si hay cambio, tira. Ejemplo: la carpeta F T P cada 15 minutos. "
            "En la misma empresa conviven."
        ),
    },
    {
        "id": "07",
        "kind": "diagram",
        "title": "E T L: extraer, transformar, cargar",
        "image": "etl.png",
        "narration": (
            "Una E T L lleva información de un punto A a un punto B en tres fases: extraer, transformar y cargar. "
            "La extracción tiene que ser ligera: recepción casi no se entera, y no se modifica el dato operativo. "
            "Transformar es dejar formato y contenido que el destino entiende: unificar web y WEB, cruzar reservas con cobros. "
            "Sí: mejorar calidad. No: fabricar noches que nadie picó. "
            "Cargar es escribir adaptándote al destino: índices, partición y tamaño de transacción importan."
        ),
    },
    {
        "id": "08",
        "kind": "bullets",
        "title": "Carga: snapshot e incremental",
        "bullets": [
            "Primera carga, o snapshot: una foto de todo, tres años de reservas.",
            "Job del martes, incremental: solo lo nuevo o lo que cambió.",
            "Mezclarlas es un error caro.",
            "También cambia cuánto extraes: no pides tres años cada noche.",
        ],
        "narration": (
            "La primera carga, el snapshot, es una foto de todo: tres años de reservas. "
            "El job del martes es incremental: solo lo nuevo o lo que cambió. "
            "Mezclarlas es un error caro. Eso también cambia cuánto extraes: no pides tres años cada noche."
        ),
    },
    {
        "id": "09",
        "kind": "diagram",
        "title": "E L T: cambia cuándo se limpia",
        "image": "etl-vs-elt.png",
        "narration": (
            "E L T cambia las letras: extraer, cargar y transformar. "
            "Los datos se dejan primero aún sin limpiar, normalmente en el lago. "
            "En la nube, un almacén elástico también puede tragar bruto. "
            "El warehouse clásico de la unidad 1.3 suele querer el dato ya limpio: ahí encaja E T L, no E L T. "
            "En una cadena hotelera real conviven: el cierre de facturación suele ser E T L; el lago de ocupación, E L T."
        ),
    },
    {
        "id": "10",
        "kind": "bullets",
        "title": "Hola E T L: el taller",
        "bullets": [
            "Enseña las tres letras. No pinta el panel de ocupación de las 8.",
            "Reservas del canal web, con cobro, y una etiqueta hotel (web).",
            "pandas: inner join. DuckDB: el mismo oficio en SQL.",
            "pandas escribe un array JSON. DuckDB suele escribir JSONL.",
            "En Pentaho, 1.8, el mismo cruce sale agregado por hotel y canal.",
        ],
        "narration": (
            "El taller Hola E T L enseña las tres letras. No pinta el panel de ocupación de las 8. "
            "Objetivo pequeño: reservas del canal web con cobro, y una etiqueta hotel web. "
            "pandas hace un inner join. Duck D B hace lo mismo en SQL. "
            "Cuidado: pandas escribe un array JSON. Duck D B suele escribir JSONL, una reserva por línea. "
            "No son el mismo fichero. En el 1.8 de Pentaho, el mismo cruce se vuelve informe agregado por hotel y canal."
        ),
    },
    {
        "id": "11",
        "kind": "bullets",
        "title": "La L también elige formato",
        "bullets": [
            "JSON o CSV: para verlo un compañero.",
            "Parquet: lago e informe de las 8. Lee hotel e importe, no las doce columnas.",
            "Avro: colas, cuando el esquema cambia.",
            "to_parquet necesita pyarrow y el cruce de pandas.",
        ],
        "narration": (
            "Escribir un fichero no basta. El JSON del taller vale para ver. "
            "Si el destino es el lago, Parquet: el informe lee hotel e importe y no carga las doce columnas. "
            "Avro encaja en colas, porque cada fila lleva su esquema. "
            "Si usas to parquet en pandas, instala pyarrow. Si solo corriste Duck D B, no existe la variable cruce: se exporta con COPY a Parquet."
        ),
    },
    {
        "id": "12",
        "kind": "diagram",
        "title": "Cola: semáforo, no el panel de las 8",
        "image": "cola-mensajes.png",
        "narration": (
            "Si el sensor de habitación no puede esperar al informe de las 8, hay que desacoplar productor y consumidor. "
            "Una cola de mensajes es un buzón. El productor deja el evento: la habitación se ocupó. "
            "El consumidor es el semáforo de recepción, no el panel de las 8. Ese panel sigue siendo un lote nocturno. "
            "Si el semáforo va lento, la cola aguanta: es un búfer. Frenar al productor es contrapresión, otra idea."
        ),
    },
    {
        "id": "13",
        "kind": "diagram",
        "title": "Capas: la ingesta está abajo",
        "image": "capas-ingesta.png",
        "narration": (
            "La ingesta es la primera capa: lleva el dato desde las fuentes. Las fuentes no son la capa. "
            "Arriba, almacenamiento: lago, dato en bruto, y almacén de informes, dato limpio. Conviven; no es un paso obligado. "
            "Luego procesamiento y el panel de las 8, que es un informe de la mañana, lote nocturno, no tiempo real. "
            "En el 1.5 hay más capas: seguridad y monitorización también cuentan."
        ),
    },
    {
        "id": "14",
        "kind": "bullets",
        "title": "Familias, no logos",
        "bullets": [
            "Lote SQL hacia el lago: Sqoop, un job Spark, Pentaho.",
            "Flujo y mensajería: Kafka, NiFi, Flume. El semáforo, no el cierre de finanzas.",
            "E T L visual en aula: Pentaho, 1.8.",
            "Orquestar pasos: Airflow. No transforma el dato: dispara y avisa si falla.",
        ],
        "narration": (
            "Citas la familia. El producto cambia de año. "
            "Tabla SQL grande de noche hacia el lago: puente por lotes, un job Spark o Pentaho. "
            "Logs o sensores que tienen que verse ya: flujo y mensajería, Kafka o NiFi. "
            "En esta aula la suite visual es Pentaho. Airflow orquesta: no transforma el dato, dispara pasos y avisa si uno falla."
        ),
    },
    {
        "id": "15",
        "kind": "bullets",
        "title": "Criterio b) en un examen",
        "bullets": [
            "Origen y formato. ¿Hay que cruzar dos sistemas?",
            "Quién inicia: push, pull o poll.",
            "Reloj: ¿el dato tarde sigue valiendo?",
            "E T L o E L T. Destino y formato de la carga.",
            "Un nombre de producto solo no puntúa. Di por qué no el de al lado.",
        ],
        "narration": (
            "El criterio b) pide procedimientos y mecanismos para la ingestión. "
            "Clava origen, quién inicia, reloj, E T L o E L T, destino y formato de la carga, y por qué no el de al lado. "
            "Un nombre de producto solo no puntúa. "
            "En la página tienes consideraciones, el taller y las actividades. Moodle sigue mandando la nota."
        ),
    },
]


def render(slide: dict) -> Image.Image:
    kind = slide["kind"]
    if kind == "title":
        return title_slide()
    if kind == "diagram":
        return diagram_slide(slide["title"], ASSETS / slide["image"])
    return bullets_slide(slide["title"], slide["bullets"])


def ffmpeg_exe() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def audio_seconds(ffmpeg: str, path: Path) -> float:
    proc = subprocess.run(
        [ffmpeg, "-i", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    m = re.search(r"Duration: (\d+):(\d+):(\d+)\.(\d+)", proc.stderr)
    if not m:
        return 8.0
    h, mn, s, cs = (int(x) for x in m.groups())
    return h * 3600 + mn * 60 + s + cs / 100.0


async def speak(text: str, dest: Path) -> None:
    import edge_tts

    dest.parent.mkdir(parents=True, exist_ok=True)
    comm = edge_tts.Communicate(text, VOICE, rate="-8%")
    await comm.save(str(dest))


def encode_clip(ffmpeg: str, png: Path, mp3: Path, mp4: Path, seconds: float) -> None:
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-t",
            f"{seconds:.2f}",
            "-i",
            str(png),
            "-i",
            str(mp3),
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-shortest",
            str(mp4),
        ],
        check=True,
        capture_output=True,
    )


def concat(ffmpeg: str, clips: list[Path], out: Path) -> None:
    listing = BUILD / "concat.txt"
    listing.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in clips) + "\n",
        encoding="utf-8",
    )
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(listing),
            "-c:v",
            "libx264",
            "-crf",
            "26",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            str(out),
        ],
        check=True,
        capture_output=True,
    )


async def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    ffmpeg = ffmpeg_exe()
    clips: list[Path] = []
    for slide in SLIDES:
        sid = slide["id"]
        png = BUILD / f"{sid}.png"
        mp3 = BUILD / f"{sid}.mp3"
        mp4 = BUILD / f"{sid}.mp4"
        print(f"Slide {sid}: {slide['title']}", flush=True)
        render(slide).save(png, "PNG")
        await speak(slide["narration"], mp3)
        duration = audio_seconds(ffmpeg, mp3) + 0.6
        encode_clip(ffmpeg, png, mp3, mp4, duration)
        clips.append(mp4)
    print("Concatenando…", flush=True)
    concat(ffmpeg, clips, OUT)
    size_mb = OUT.stat().st_size / (1024 * 1024)
    print(f"Listo: {OUT} ({size_mb:.1f} MB)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
