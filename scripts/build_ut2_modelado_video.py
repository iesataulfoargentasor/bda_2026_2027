"""Modelado documental con la voz natural y el diseño de los vídeos de UT2."""
import argparse
import asyncio
import json

import build_ut2_almacenamiento_video as video

video.NAME = "modelado-documental"
video.BUILD = video.ROOT / ".venv/ut2-modelado-video"
video.BUILD.mkdir(parents=True, exist_ok=True)
video.RATE = "+0%"
video.NARRATION_SEPARATOR = "\n\n"
video.PRESERVE_NATURAL_PAUSES = True
video.HEADER = "UT2 · 2.7  /  MODELADO DOCUMENTAL"
video.TRANSCRIPT_TITLE = "UT2 · 2.7 · MODELADO DOCUMENTAL: ORGANIZAR Y CONSERVAR EL SIGNIFICADO"
video.SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/modelado/"
video.TABS = ["LAS PREGUNTAS", "ORGANIZAR", "EVOLUCIONAR", "COMPROBAR"]
video.SCENES = json.loads(
    (video.ROOT / "scripts/ut2_modelado_video.json").read_text(encoding="utf-8")
)
video.NARRATIONS = [scene["narration"] for scene in video.SCENES]
video.base.BUILD = video.BUILD
video.reference.B = video.BUILD
video.reference.NARRATIONS = video.NARRATIONS

standard_render = video.render


def render(scene, index):
    custom = {"embedref", "history", "association", "rates", "versions", "transition",
              "load", "buckets", "late", "outlier", "validation", "practice"}
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

    if scene["kind"] == "embedref":
        box(45, 299, 595, 510)
        centered(320, 313, "Embeber · dentro de la reserva", 27, width=510)
        box(102, 375, 538, 481, "#DFE6E3")
        centered(320, 390, "Datos de llegada", 29, base.TEAL, width=400)
        centered(320, 439, "Hora y matrícula", 25, width=400)
        box(645, 299, 1235, 510)
        centered(940, 313, "Referenciar · apuntar al hotel", 27, width=548)
        box(669, 386, 877, 483, "#DFE6E3")
        centered(773, 417, "Reserva", 27, base.TEAL, width=180)
        base.arrow(draw, 891, 434, length=90)
        box(997, 386, 1211, 483, "#DFE6E3")
        centered(1104, 417, "Hotel", 27, base.TEAL, width=185)

    elif scene["kind"] == "history":
        box(45, 303, 595, 505)
        centered(320, 319, "R27-1 · fotografía de lo acordado", 27, width=510)
        centered(320, 378, "Nombre histórico: Laredo", 29, base.TEAL, width=510)
        centered(320, 435, "3 noches · importe 186,50 €", 28, width=510)
        box(645, 303, 1235, 505)
        centered(940, 319, "Hotel · agenda actualizada", 28, width=550)
        centered(940, 378, "Nombre y teléfono vigentes", 29, base.TEAL, width=550)
        centered(940, 435, "Se consultan por la referencia", 26, width=550)

    elif scene["kind"] == "association":
        for left, width, title, detail in [
            (45, 280, "Habitación", "Hotel + número"),
            (410, 460, "Asociación", "Precio · vigencia · condiciones"),
            (955, 280, "Servicio", "Parking / cuna")
        ]:
            box(left, 326, left + width, 495)
            centered(left + width / 2, 351, title, 29, width=width - 30)
            centered(left + width / 2, 426, detail, 25, base.TEAL, width=width - 30)
        draw.line((325, 404, 410, 404), fill=base.TEAL, width=4)
        draw.line((870, 404, 955, 404), fill=base.TEAL, width=4)

    elif scene["kind"] == "rates":
        centered(640, 295, "Una lista de tarifas · cada elemento conserva canal, precio y moneda", 27)
        for position, (channel, price) in enumerate([
            ("web", "90 EUR"), ("ota", "110 EUR"),
            ("recepcion", "100 EUR"), ("agencias", "95 EUR")
        ]):
            left = 45 + position * 310
            box(left, 353, left + 265, 505, "#DFE6E3" if position == 3 else "white")
            centered(left + 132, 373, channel, 28, width=235)
            centered(left + 132, 441, price, 33, base.TEAL, width=235)

    elif scene["kind"] == "versions":
        for left, title, rows in [
            (45, "Versión 1 · campos separados", ["hotel: texto", "telefono_hotel: texto"]),
            (715, "Versión 2 · hotel como objeto", ["hotel: id + nombre + teléfono", "Noches e importe conservados"])
        ]:
            box(left, 307, left + 520, 507)
            centered(left + 260, 326, title, 26, width=484)
            for row, label in enumerate(rows):
                centered(left + 260, 389 + row * 59, label, 25, base.TEAL, width=484)
        base.arrow(draw, 587, 408, length=106)

    elif scene["kind"] == "transition":
        for position, (number, title, detail) in enumerate([
            ("1", "Lectores compatibles", "Entienden ambos formatos"),
            ("2", "Nueva escritura", "Empieza el formato nuevo"),
            ("3", "Migración si procede", "Transformar y comprobar")
        ]):
            left = 45 + position * 415
            box(left, 303, left + 365, 508)
            centered(left + 182, 315, number, 43, base.TEAL)
            centered(left + 182, 385, title, 27, width=335)
            centered(left + 182, 459, detail, 23, base.MUTED, width=335)

    elif scene["kind"] == "load":
        for position, (number, label, detail) in enumerate([
            ("800", "medidas / minuto", "Todo el grupo"),
            ("48 000", "medidas / hora", "Todo el grupo"),
            ("60", "medidas / hora", "Por sensor")
        ]):
            left = 45 + position * 415
            box(left, 303, left + 365, 508)
            centered(left + 182, 315, number, 53, base.TEAL, width=335)
            centered(left + 182, 394, label, 28, width=335)
            centered(left + 182, 461, detail, 24, base.MUTED, width=335)

    elif scene["kind"] == "buckets":
        for left, title, total, mean in [
            (45, "08:00–09:00 UTC", "1470", "24,5 °C"),
            (645, "09:00–10:00 UTC", "1590", "26,5 °C")
        ]:
            box(left, 303, left + 550, 508)
            centered(left + 275, 317, title, 30, width=510)
            centered(left + 275, 375, f"60 medidas · suma {total}", 28, width=510)
            centered(left + 275, 440, f"Media: {mean}", 36, base.TEAL, width=510)

    elif scene["kind"] == "late":
        box(45, 303, 595, 508)
        centered(320, 318, "Si falta una lectura", 28, width=510)
        centered(320, 380, "Media = suma / 59", 34, base.TEAL, width=510)
        centered(320, 455, "Cobertura incompleta", 25, width=510)
        box(645, 303, 1235, 508)
        centered(940, 318, "Dato tardío: 30 °C a las 09:30:30", 27, width=550)
        centered(940, 380, "Media = 1620 / 61", 34, base.TEAL, width=550)
        centered(940, 455, "Ejercicio sobre una copia", 25, width=550)

    elif scene["kind"] == "outlier":
        for left, width, number, label in [
            (45, 340, "6", "Dentro de la reserva"),
            (475, 340, "194", "En la continuación"),
            (905, 330, "200", "Extras conservados")
        ]:
            box(left, 319, left + width, 496)
            centered(left + width / 2, 333, number, 57, base.TEAL, width=width - 30)
            centered(left + width / 2, 438, label, 25, width=width - 30)
        centered(430, 380, "+", 42)
        centered(860, 380, "=", 42)

    elif scene["kind"] == "validation":
        for position, (title, value, result, color) in enumerate([
            ("Noches enteras", "2", "Tipo admitido", base.TEAL),
            ("Noches como texto", '"dos"', "No cumple el contrato", base.AMBER),
            ("Campo adicional", "mascota: true", "Permitido en el ejemplo", base.TEAL)
        ]):
            left = 45 + position * 415
            box(left, 303, left + 365, 508)
            centered(left + 182, 321, title, 26, width=335)
            centered(left + 182, 385, value, 34, color, width=335)
            centered(left + 182, 462, result, 24, color, width=335)

    elif scene["kind"] == "practice":
        for position, (number, label, detail) in enumerate([
            ("1", "Hotel", "Compartido"),
            ("1", "Reserva", "Con referencia"),
            ("1", "Ficha de tarifas", "Tres precios"),
            ("2", "Reservas", "Dos estructuras"),
            ("120", "Medidas", "Dos horas")
        ]):
            left = 45 + position * 240
            box(left, 311, left + 225, 505)
            centered(left + 112, 324, number, 47, base.TEAL, width=195)
            centered(left + 112, 399, label, 25, width=200)
            centered(left + 112, 461, detail, 23, base.MUTED, width=200)
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
