#!/usr/bin/env python3
"""Genera el cierre ficticio de la Práctica Integradora de la UT2.

Perfil de aula, semilla 2026: 3.000.000 reservas, un cobro por cada reserva
confirmada, 1.000.000 opiniones y 15.000.000 lecturas de sensores. Los hoteles
son Santander, Laredo, Comillas y Potes. No incluye Noja ni Reinosa.

Escribe cuatro CSV en la carpeta de salida y no modifica totales_esperados.json
salvo que se pase --escribir-totales. El bruto no se sube a git.

Reglas del cierre, las mismas que fija totales_esperados.json:

- noches por hotel: suma de noches de las reservas con estado confirmada.
- importe por hotel: suma de cobrado, en céntimos, unida a la reserva. No se
  suma la columna importe de reservas.csv.
- cancelaciones por canal: reservas con estado cancelada.
- sensores por hotel: número de lecturas.

Uso:
  python generar_cierre.py --salida datos/bruto
  python generar_cierre.py --salida datos/bruto --comprobar datos/totales_esperados.json
"""
from __future__ import annotations

import argparse
import array
import json
import random
from pathlib import Path

SEMILLA = 2026
HOTELES = ("Santander", "Laredo", "Comillas", "Potes")
CANALES = ("web", "ota", "recepcion")
ZONAS = ("hall", "habitacion", "cocina", "clima")
FRASES = (
    "Habitacion correcta y desayuno justo",
    "Ruido por la noche y ducha escasa",
    "Buen trato en recepcion y cama comoda",
    "Vista agradable y wifi irregular",
)
PERFILES = {
    "aula": {"reservas": 3_000_000, "opiniones": 1_000_000, "sensores": 15_000_000},
    "prueba": {"reservas": 3_000, "opiniones": 1_000, "sensores": 12_000},
}


def euros(centimos: int) -> str:
    signo = "-" if centimos < 0 else ""
    centimos = abs(centimos)
    return f"{signo}{centimos // 100}.{centimos % 100:02d}"


def vacios() -> dict:
    return {hotel: 0 for hotel in HOTELES}


def generar(destino: Path, perfil: str) -> dict:
    cuentas = PERFILES[perfil]
    rng = random.Random(SEMILLA)
    destino.mkdir(parents=True, exist_ok=True)
    rutas = {
        "reservas": destino / "reservas.csv",
        "cobros": destino / "cobros.csv",
        "opiniones": destino / "opiniones.csv",
        "sensores": destino / "sensores.csv",
    }
    noches = vacios()
    importe = vacios()
    sensores = vacios()
    cancelaciones = {canal: 0 for canal in CANALES}
    n_cobros = 0

    with rutas["reservas"].open("w", encoding="utf-8", newline="\n") as fres, rutas[
        "cobros"
    ].open("w", encoding="utf-8", newline="\n") as fcob:
        fres.write("id_reserva,hotel,canal,noches,estado,importe,fecha\n")
        fcob.write("id_cobro,id_reserva,cobrado\n")
        for i in range(1, cuentas["reservas"] + 1):
            hotel = HOTELES[rng.randrange(len(HOTELES))]
            canal = CANALES[rng.randrange(len(CANALES))]
            noches_reserva = 1 + rng.randrange(14)
            cancelada = rng.randrange(100) < 12
            precio = noches_reserva * (9_000 + rng.randrange(3_000))
            cobrado = noches_reserva * (7_500 + rng.randrange(2_500))
            dia = rng.randrange(365)
            fecha = f"2026-{(dia % 12) + 1:02d}-{(dia % 28) + 1:02d}"
            estado = "cancelada" if cancelada else "confirmada"
            fres.write(
                f"{i},{hotel},{canal},{noches_reserva},{estado},{euros(precio)},{fecha}\n"
            )
            if cancelada:
                cancelaciones[canal] += 1
                continue
            n_cobros += 1
            noches[hotel] += noches_reserva
            importe[hotel] += cobrado
            fcob.write(f"{n_cobros},{i},{euros(cobrado)}\n")

    with rutas["opiniones"].open("w", encoding="utf-8", newline="\n") as fop:
        fop.write("id_opinion,id_reserva,hotel,puntuacion,texto\n")
        n_reservas = cuentas["reservas"]
        for i in range(1, cuentas["opiniones"] + 1):
            id_reserva = 1 + rng.randrange(n_reservas)
            hotel = HOTELES[rng.randrange(len(HOTELES))]
            puntuacion = 1 + rng.randrange(5)
            frase = FRASES[rng.randrange(len(FRASES))]
            fop.write(f'{i},{id_reserva},{hotel},{puntuacion},{frase}. Hotel {hotel}.\n')

    with rutas["sensores"].open("w", encoding="utf-8", newline="\n") as fse:
        fse.write("id_lectura,hotel,zona,instante,valor\n")
        for i in range(1, cuentas["sensores"] + 1):
            hotel = HOTELES[rng.randrange(len(HOTELES))]
            zona = ZONAS[rng.randrange(len(ZONAS))]
            dia = rng.randrange(365)
            hora = rng.randrange(24)
            minuto = rng.randrange(60)
            instante = f"2026-{(dia % 12) + 1:02d}-{(dia % 28) + 1:02d}T{hora:02d}:{minuto:02d}:00"
            valor = 1_600 + rng.randrange(1_201)
            sensores[hotel] += 1
            fse.write(f"{i},{hotel},{zona},{instante},{euros(valor)}\n")

    bytes_bruto = sum(ruta.stat().st_size for ruta in rutas.values())
    return {
        "semilla": SEMILLA,
        "perfil": perfil,
        "filas": {
            "reservas": cuentas["reservas"],
            "cobros": n_cobros,
            "opiniones": cuentas["opiniones"],
            "sensores": cuentas["sensores"],
        },
        "bytes_bruto": bytes_bruto,
        "noches_por_hotel": noches,
        "importe_centimos_por_hotel": importe,
        "importe_por_hotel": {hotel: euros(importe[hotel]) for hotel in HOTELES},
        "cancelaciones_por_canal": cancelaciones,
        "sensores_por_hotel": sensores,
        "reglas": {
            "noches_por_hotel": "Suma de noches de las reservas con estado confirmada.",
            "importe_por_hotel": "Suma de cobrado agrupada por el hotel de la reserva. No se suma la columna importe.",
            "cancelaciones_por_canal": "Reservas con estado cancelada. No tienen fila en cobros.csv.",
            "sensores_por_hotel": "Número de filas de sensores.csv por hotel.",
        },
    }


def comprobar(destino: Path, esperados: dict) -> None:
    noches = vacios()
    importe = vacios()
    sensores = vacios()
    cancelaciones = {canal: 0 for canal in CANALES}
    n_reservas = 0
    n_cobros = 0
    n_opiniones = 0
    hotel_de: array.array | None = None

    with (destino / "reservas.csv").open(encoding="utf-8", newline="\n") as f:
        next(f)
        for linea in f:
            id_reserva, hotel, canal, noches_txt, estado, _precio, _fecha = linea.rstrip("\n").split(",")
            n_reservas += 1
            if hotel_de is None:
                hotel_de = array.array("B", bytes(esperados["filas"]["reservas"] + 1))
            hotel_de[int(id_reserva)] = HOTELES.index(hotel)
            if estado == "cancelada":
                cancelaciones[canal] += 1
            else:
                noches[hotel] += int(noches_txt)

    with (destino / "cobros.csv").open(encoding="utf-8", newline="\n") as f:
        next(f)
        for linea in f:
            _id_cobro, id_reserva, cobrado = linea.rstrip("\n").split(",")
            hotel = HOTELES[hotel_de[int(id_reserva)]]
            euros_txt, centimos_txt = cobrado.split(".")
            importe[hotel] += int(euros_txt) * 100 + int(centimos_txt)
            n_cobros += 1

    with (destino / "opiniones.csv").open(encoding="utf-8", newline="\n") as f:
        next(f)
        for _linea in f:
            n_opiniones += 1

    with (destino / "sensores.csv").open(encoding="utf-8", newline="\n") as f:
        next(f)
        for linea in f:
            _id_lectura, hotel, _zona, _instante, _valor = linea.rstrip("\n").split(",")
            sensores[hotel] += 1

    bytes_bruto = sum((destino / nombre).stat().st_size for nombre in (
        "reservas.csv", "cobros.csv", "opiniones.csv", "sensores.csv"
    ))
    observado = {
        "filas": {
            "reservas": n_reservas,
            "cobros": n_cobros,
            "opiniones": n_opiniones,
            "sensores": sum(sensores.values()),
        },
        "bytes_bruto": bytes_bruto,
        "noches_por_hotel": noches,
        "importe_centimos_por_hotel": importe,
        "cancelaciones_por_canal": cancelaciones,
        "sensores_por_hotel": sensores,
    }
    errores = []
    for clave, valor in observado.items():
        if esperados[clave] != valor:
            errores.append(f"{clave}: esperado {esperados[clave]} observado {valor}")
    if errores:
        raise SystemExit("Totales distintos:\n" + "\n".join(errores))


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera el cierre ficticio de la UT2")
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--perfil", choices=tuple(PERFILES), default="aula")
    parser.add_argument("--escribir-totales", type=Path)
    parser.add_argument("--comprobar", type=Path, help="JSON de totales ya publicado")
    args = parser.parse_args()
    if args.comprobar and args.escribir_totales:
        parser.error("Usa solo una de las dos opciones")
    if args.comprobar:
        esperados = json.loads(args.comprobar.read_text(encoding="utf-8"))
        if esperados["perfil"] != "aula" and args.perfil == "aula":
            pass
        comprobar(args.salida, esperados)
        print(f"Coincide con {args.comprobar}")
        return
    totales = generar(args.salida, args.perfil)
    print(
        f"{totales['filas']} · {totales['bytes_bruto']} bytes · "
        f"noches {totales['noches_por_hotel']} · "
        f"importe {totales['importe_por_hotel']} · "
        f"cancelaciones {totales['cancelaciones_por_canal']} · "
        f"sensores {totales['sensores_por_hotel']}"
    )
    if args.escribir_totales:
        if args.perfil != "aula":
            parser.error("--escribir-totales solo vale para el perfil aula")
        args.escribir_totales.write_text(
            json.dumps(totales, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Escritos los totales en {args.escribir_totales}")


if __name__ == "__main__":
    main()
