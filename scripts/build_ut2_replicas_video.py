"""Réplicas y particiones con la voz natural y el diseño de los vídeos de UT2."""
import argparse
import asyncio
import json

import build_ut2_almacenamiento_video as video

video.NAME = "replicas-particiones"
video.BUILD = video.ROOT / ".venv/ut2-replicas-video"
video.BUILD.mkdir(parents=True, exist_ok=True)
video.RATE = "+0%"
video.NARRATION_SEPARATOR = "\n\n"
video.PRESERVE_NATURAL_PAUSES = True
video.HEADER = "UT2 · 2.8  /  RÉPLICAS Y PARTICIONES"
video.TRANSCRIPT_TITLE = "UT2 · 2.8 · RÉPLICAS Y PARTICIONES: RECUPERAR Y REPARTIR"
video.SOURCE_URL = "https://iesataulfoargentasor.github.io/bda_2026_2027/ut2/replicas-shards/"
video.TABS = ["LAS COPIAS", "LAS GARANTÍAS", "LAS PARTES", "COMPROBAR"]
video.SCENES = json.loads(
    (video.ROOT / "scripts/ut2_replicas_video.json").read_text(encoding="utf-8")
)
video.NARRATIONS = [scene["narration"] for scene in video.SCENES]
video.base.BUILD = video.BUILD
video.reference.B = video.BUILD
video.reference.NARRATIONS = video.NARRATIONS

standard_render = video.render


def render(scene, index):
    custom = {"copiesparts", "replicas", "journal", "majorities", "isolated", "rollback",
              "controls", "lag", "recovery", "capacity", "architecture", "register",
              "splitmove", "conservation"}
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

    def triple(entries):
        for position, (title, middle, bottom) in enumerate(entries):
            left = 45 + position * 415
            box(left, 305, left + 365, 508)
            centered(left + 182, 321, title, 27, width=335)
            centered(left + 182, 389, middle, 28, base.TEAL, width=335)
            centered(left + 182, 462, bottom, 23, base.MUTED, width=335)

    if scene["kind"] == "copiesparts":
        for left, title, values in [
            (45, "Replicar · misma carpeta", ["A B C", "A B C", "A B C"]),
            (645, "Particionar · secciones distintas", ["A", "B", "C"])
        ]:
            box(left, 303, left + 550, 508)
            centered(left + 275, 321, title, 28, width=510)
            for pos, label in enumerate(values):
                x = left + 22 + pos * 174
                box(x, 388, x + 158, 480, "#DFE6E3")
                centered(x + 79, 417, label, 31, base.TEAL, width=136)

    elif scene["kind"] == "replicas":
        triple([("Laredo", "Todas las reservas", "Primario en este ejemplo"),
                ("Potes", "Todas las reservas", "Secundario"),
                ("Noja", "Todas las reservas", "Secundario")])

    elif scene["kind"] == "journal":
        for left, title, detail in [(45, "Cambio en el primario", "Reserva o actualización"),
                                    (490, "Diario · oplog", "Historial limitado"),
                                    (935, "Secundario", "Aplica los cambios")]:
            box(left, 326, left + 300, 495)
            centered(left + 150, 350, title, 25, width=272)
            centered(left + 150, 431, detail, 23, base.TEAL, width=272)
        base.arrow(draw, 364, 409, length=105)
        base.arrow(draw, 809, 409, length=105)

    elif scene["kind"] == "majorities":
        for left, total, needed in [(45, 3, 2), (645, 4, 3)]:
            box(left, 303, left + 550, 508)
            centered(left + 275, 320, f"{total} votantes configurados", 29, width=510)
            start = left + 275 - (total - 1) * 48
            for voter in range(total):
                x = start + voter * 96
                color = base.TEAL if voter < needed else "#DFE6E3"
                draw.ellipse((x - 27, 385, x + 27, 439), fill=color)
            centered(left + 275, 462, f"Mayoría: {needed}", 28, base.TEAL, width=510)

    elif scene["kind"] == "isolated":
        for pos, (title, status) in enumerate([("Miembro 1", "Accesible"),
                                               ("Miembro 2", "No responde"),
                                               ("Miembro 3", "No responde")]):
            left = 45 + pos * 415
            box(left, 305, left + 365, 445, "white" if pos == 0 else "#DFE6E3")
            centered(left + 182, 325, title, 29, width=335)
            centered(left + 182, 388, status, 28, base.TEAL if pos == 0 else base.MUTED, width=335)
        centered(640, 475, "1 de 3 · Sin mayoría para continuar las escrituras", 30, base.AMBER)

    elif scene["kind"] == "rollback":
        triple([("Antes de la caída", "Solo Laredo tiene R", "Confirmación w: 1"),
                ("Nueva elección", "Potes no tiene R", "Continúa otro historial"),
                ("Laredo vuelve", "Deshace ese cambio", "Rollback de R")])

    elif scene["kind"] == "controls":
        triple([("readPreference", "¿Dónde leo?", "Selecciona el miembro"),
                ("readConcern", "¿Qué puedo ver?", "Define la visibilidad"),
                ("writeConcern", "¿Qué confirmación?", "Condiciones de escritura")])

    elif scene["kind"] == "lag":
        for pos, (title, line1, line2) in enumerate([
            ("Primario", "Cambio aplicado", "Confirma"),
            ("Secundario 1", "Cambio recibido", "Confirma"),
            ("Noja · secundario", "Estado anterior", "Pendiente de aplicar")
        ]):
            left = 45 + pos * 415
            box(left, 303, left + 365, 466)
            centered(left + 182, 319, title, 26, width=335)
            centered(left + 182, 375, line1, 28, base.TEAL if pos < 2 else base.AMBER, width=335)
            centered(left + 182, 430, line2, 23, base.MUTED, width=335)
        centered(640, 486, "Escritura mayoritaria · Noja aún puede ir por detrás", 27)

    elif scene["kind"] == "recovery":
        for pos, (title, line1, line2) in enumerate([
            ("Antes", "3 miembros sanos", "Reserva 01 confirmada"),
            ("Parada", "Primario detenido", "Se observa la elección"),
            ("Nuevo primario", "Lee la reserva 01", "Confirma la reserva 02"),
            ("Recuperación", "Arranca el detenido", "Conserva ambas fichas")
        ]):
            left = 45 + pos * 310
            box(left, 310, left + 265, 505)
            centered(left + 132, 328, title, 26, width=235)
            centered(left + 132, 400, line1, 23, base.TEAL, width=239)
            centered(left + 132, 459, line2, 21, base.MUTED, width=239)

    elif scene["kind"] == "capacity":
        for pos in range(3):
            left = 45 + pos * 415
            box(left, 303, left + 365, 458)
            centered(left + 182, 318, f"Copia {pos + 1}", 28, width=335)
            centered(left + 182, 375, "100 GB", 46, base.TEAL, width=335)
        centered(640, 482, "100 GB lógicos · Tres copias del mismo contenido", 30)

    elif scene["kind"] == "architecture":
        box(45, 367, 260, 464)
        centered(152, 400, "Aplicación", 27, width=189)
        base.arrow(draw, 277, 416, length=90)
        box(385, 367, 610, 464)
        centered(497, 383, "mongos", 30, base.TEAL, width=195)
        centered(497, 430, "Centralita", 23, width=195)
        box(385, 296, 610, 348)
        centered(497, 308, "Config · mapa", 24, width=205)
        draw.line((497, 348, 497, 367), fill=base.TEAL, width=3)
        draw.line((610, 416, 676, 416, 676, 353, 735, 353), fill=base.TEAL, width=3)
        draw.line((676, 416, 676, 461, 735, 461), fill=base.TEAL, width=3)
        for top, title, detail in [(305, "Shard A · parte A", "Copias de A dentro del grupo"),
                                   (413, "Shard B · parte B", "Copias de B dentro del grupo")]:
            box(735, top, 1235, top + 95)
            centered(985, top + 12, title, 27, base.TEAL, width=464)
            centered(985, top + 55, detail, 24, width=464)

    elif scene["kind"] == "register":
        for left, title, main, note in [
            (45, "Antes del registro", "1 shard", "Un grupo incorporado"),
            (715, "Después del registro", "2 shards", "Se añade otro grupo")
        ]:
            box(left, 305, left + 520, 508)
            centered(left + 260, 321, title, 29, width=484)
            centered(left + 260, 382, main, 46, base.TEAL, width=484)
            centered(left + 260, 463, note, 25, base.MUTED, width=484)
        base.arrow(draw, 587, 408, length=106)

    elif scene["kind"] == "splitmove":
        for pos, (title, line1, line2) in enumerate([
            ("1 · Inspeccionar", "Dónde está el rango", "Elegir otro destino"),
            ("2 · Dividir", "Crear un límite", "No cambia de shard"),
            ("3 · Mover", "Cambiar ubicación", "Conservar el contenido")
        ]):
            left = 45 + pos * 415
            box(left, 305, left + 365, 508)
            centered(left + 182, 321, title, 28, width=335)
            centered(left + 182, 390, line1, 28, base.TEAL, width=335)
            centered(left + 182, 462, line2, 24, base.MUTED, width=335)

    elif scene["kind"] == "conservation":
        centered(640, 297, "Noches por hotel · Total: 46", 30, base.TEAL)
        for pos, (hotel, nights) in enumerate([
            ("Comillas", "4"), ("Laredo", "11"), ("Noja", "4"),
            ("Potes", "13"), ("Reinosa", "6"), ("Santander", "8")
        ]):
            left = 45 + pos * 200
            box(left, 355, left + 185, 502)
            centered(left + 92, 372, hotel, 25, width=165)
            centered(left + 92, 426, nights, 43, base.TEAL, width=165)
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
