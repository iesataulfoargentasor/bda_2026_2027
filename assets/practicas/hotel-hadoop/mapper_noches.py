#!/usr/bin/env python3
"""Mapper: hotel -> noches. Salta la cabecera del CSV de reservas."""
import sys

for linea in sys.stdin:
    linea = linea.strip()
    if not linea or linea.startswith("id_"):
        continue
    partes = linea.split(",")
    if len(partes) < 4:
        continue
    hotel, noches = partes[1], partes[3]
    try:
        print(f"{hotel}\t{int(noches)}")
    except ValueError:
        continue
