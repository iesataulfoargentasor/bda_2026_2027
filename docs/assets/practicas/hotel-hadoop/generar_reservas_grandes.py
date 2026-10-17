#!/usr/bin/env python3
"""Genera un CSV de reservas lo bastante grande para ver varios bloques HDFS.

No lo subas a git: es un fichero de laboratorio. En el aula, 3 bloques (~384 MB)
permiten observar el reparto; mide los bytes reales y ajusta --lineas.
"""
import argparse
from pathlib import Path

HOTELES = ("Laredo", "Potes", "Santander", "Noja", "Comillas")
CANALES = ("web", "ota", "recepcion")
parser = argparse.ArgumentParser(description="Genera reservas sintéticas con el contrato CSV de UT2")
parser.add_argument("--lineas", type=int, default=4_500_000)
parser.add_argument("--salida", type=Path, default=Path("reservas_grandes.csv"))
args = parser.parse_args()
if args.lineas < 1:
    parser.error("--lineas debe ser positivo")
LINEAS = args.lineas

destino = args.salida
with destino.open("w", encoding="utf-8", newline="\n") as f:
    f.write("id_reserva,hotel,canal,noches,importe\n")
    for i in range(1, LINEAS + 1):
        hotel = HOTELES[i % len(HOTELES)]
        canal = CANALES[i % len(CANALES)]
        noches = 1 + (i % 7)
        importe = noches * (72.0 + (i % 40))
        f.write(f"{i},{hotel},{canal},{noches},{importe:.2f}\n")

print(f"Escrito {destino.resolve()} ({destino.stat().st_size} bytes)")
