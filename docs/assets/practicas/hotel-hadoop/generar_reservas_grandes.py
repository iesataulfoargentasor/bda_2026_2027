#!/usr/bin/env python3
"""Genera un CSV de reservas lo bastante grande para ver varios bloques HDFS.

No lo subas a git: es un fichero de laboratorio. En el aula, 3 bloques (~384 MB)
bastan para ver el corte; cambia LINEAS si el profesor pide más.
"""
from pathlib import Path

HOTELES = ("Laredo", "Potes", "Santander", "Noja", "Comillas")
CANALES = ("web", "ota", "recepcion")
LINEAS = 4_500_000  # ~250–300 MB de texto; ajustad en clase

destino = Path("reservas_grandes.csv")
with destino.open("w", encoding="utf-8", newline="\n") as f:
    f.write("id_reserva,hotel,canal,noches,importe\n")
    for i in range(1, LINEAS + 1):
        hotel = HOTELES[i % len(HOTELES)]
        canal = CANALES[i % len(CANALES)]
        noches = 1 + (i % 7)
        importe = noches * (72.0 + (i % 40))
        f.write(f"{i},{hotel},{canal},{noches},{importe:.2f}\n")

print(f"Escrito {destino.resolve()} ({destino.stat().st_size} bytes)")
