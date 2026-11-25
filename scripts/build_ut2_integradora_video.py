"""Guía de la práctica integradora con la voz natural y el diseño de UT2."""
import argparse
import asyncio
import json

import build_ut2_almacenamiento_video as video

video.NAME = "practica-integradora"
video.BUILD = video.ROOT / ".venv/ut2-integradora-video"
video.BUILD.mkdir(parents=True, exist_ok=True)
video.RATE = "+0%"
video.NARRATION_SEPARATOR = "\n\n"
video.PRESERVE_NATURAL_PAUSES = True
video.HEADER = "UT2  /  PRÁCTICA INTEGRADORA"
video.TRANSCRIPT_TITLE = "UT2 · PRÁCTICA INTEGRADORA: EL CIERRE Y LA RECEPCIÓN DEL HOTEL"
video.SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/practica-integradora/"
video.TABS = ["EL ENCARGO", "EL CIERRE", "LAS PRUEBAS", "LA ENTREGA"]
video.SCENES = json.loads(
    (video.ROOT / "scripts/ut2_integradora_video.json").read_text(encoding="utf-8")
)
video.NARRATIONS = [scene["narration"] for scene in video.SCENES]
video.base.BUILD = video.BUILD
video.reference.B = video.BUILD
video.reference.NARRATIONS = video.NARRATIONS
standard_render = video.render


def render(scene, index):
    custom = {"flow", "four", "criteria", "timeline", "join", "measurement",
              "backup", "evidence", "hours"}
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

    kind = scene["kind"]
    if kind == "flow":
        for pos, (title, middle, bottom) in enumerate(scene["steps"]):
            left = 45 + pos * 445
            box(left, 305, left + 300, 508)
            centered(left + 150, 322, title, 27, width=272)
            centered(left + 150, 390, middle, 25, base.TEAL, width=272)
            centered(left + 150, 463, bottom, 22, base.MUTED, width=272)
            if pos < 2:
                base.arrow(draw, left + 318, 409, length=105)

    elif kind == "four":
        for pos, (title, value, note) in enumerate(scene["items"]):
            left = 45 + pos * 310
            box(left, 305, left + 265, 508)
            centered(left + 132, 322, title, 26, width=237)
            centered(left + 132, 390, value, 30, base.TEAL, width=237)
            centered(left + 132, 465, note, 21, base.MUTED, width=237)

    elif kind == "criteria":
        for pos, (letter, title, note) in enumerate([
            ("a", "Elegir", "Volumen y uso"), ("b", "Repartir", "Cálculo comprobado"),
            ("c", "Probar fallos", "Efecto y recuperación"), ("d", "Reutilizar", "Otra pregunta"),
            ("e", "Ampliar", "Un módulo real")
        ]):
            left = 45 + pos * 240
            box(left, 305, left + 230, 508)
            centered(left + 115, 322, letter + ")", 38, base.TEAL, width=202)
            centered(left + 115, 397, title, 27, width=202)
            centered(left + 115, 469, note, 20, base.MUTED, width=210)

    elif kind == "timeline":
        box(45, 305, 590, 435)
        box(690, 305, 1235, 435)
        centered(317, 318, "23:00 · Finanzas cierra", 30, width=515)
        centered(317, 380, "Histórico conservado", 26, base.TEAL, width=515)
        centered(962, 318, "8:00 · Gerencia consulta", 30, width=515)
        centered(962, 380, "Informe contrastado", 26, base.TEAL, width=515)
        base.arrow(draw, 606, 372, length=68)
        box(45, 455, 1235, 511, "#DFE6E3")
        centered(640, 468, "Recepción continúa · Buscar y modificar una reserva", 28)

    elif kind == "join":
        for left, title, line1, line2 in [
            (45, "Reserva", "R-17 · Laredo", "importe: 180 €"),
            (490, "Cobro", "id_reserva: R-17", "cobrado: 160 €"),
            (935, "Informe", "Hotel: Laredo", "Sumamos: 160 €")
        ]:
            box(left, 305, left + 300, 508)
            centered(left + 150, 322, title, 29, width=272)
            centered(left + 150, 389, line1, 27, width=272)
            centered(left + 150, 462, line2, 29, base.TEAL, width=272)
        base.arrow(draw, 363, 409, length=105)
        base.arrow(draw, 808, 409, length=105)

    elif kind == "measurement":
        for left, title, measures, median in [
            (45, "1 trabajador", "12 s · 10 s · 11 s", "Mediana: 11 s"),
            (690, "2 trabajadores", "9 s · 13 s · 10 s", "Mediana: 10 s")
        ]:
            box(left, 305, left + 545, 508)
            centered(left + 272, 322, title, 30, width=515)
            centered(left + 272, 389, measures, 34, width=515)
            centered(left + 272, 462, median, 31, base.TEAL, width=515)

    elif kind == "backup":
        for left, title, line1, line2 in [
            (45, "Réplica", "Sigue los cambios", "También puede copiar un borrado"),
            (690, "Copia de seguridad", "Conserva otra versión", "Permite recuperar un estado anterior")
        ]:
            box(left, 305, left + 545, 508)
            centered(left + 272, 322, title, 30, width=515)
            centered(left + 272, 390, line1, 30, base.TEAL, width=515)
            centered(left + 272, 465, line2, 25, base.MUTED, width=515)

    elif kind == "evidence":
        for pos, (title, line1, line2) in enumerate([
            ("1 · Predicción", "Qué espero", "Total de referencia"),
            ("2 · Operación", "Qué ejecuto", "Versión y nodo"),
            ("3 · Salida", "Qué aparece", "Resultado literal"),
            ("4 · Interpretación", "Qué demuestra", "Condiciones y límites")
        ]):
            left = 45 + pos * 310
            box(left, 305, left + 265, 508)
            centered(left + 132, 322, title, 25, width=237)
            centered(left + 132, 390, line1, 28, base.TEAL, width=237)
            centered(left + 132, 465, line2, 22, base.MUTED, width=237)

    elif kind == "hours":
        for pos, (title, hours, note) in enumerate([
            ("Almacenes", "3 h", "Bloque 1"), ("Cierre", "5 h", "Bloque 2"),
            ("Fallo", "2 h", "Bloque 3"), ("Recepción", "5 h", "Bloque 4"),
            ("Crecimiento", "3 h", "Bloque 5"), ("Pregunta", "2 h", "Bloque 6")
        ]):
            left = 45 + pos * 200
            box(left, 305, left + 185, 508)
            centered(left + 92, 322, title, 24, width=165)
            centered(left + 92, 387, hours, 42, base.TEAL, width=165)
            centered(left + 92, 465, note, 24, base.MUTED, width=165)
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
