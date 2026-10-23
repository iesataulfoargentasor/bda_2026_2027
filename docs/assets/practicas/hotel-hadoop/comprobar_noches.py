#!/usr/bin/env python3
"""Contrasta una salida TSV hotel/noches con su CSV de entrada.

Uso: python comprobar_noches.py reservas.csv noches_local.tsv
Lee la entrada secuencialmente y compara cada hotel, no solo el total.
No ejecuta Hadoop ni demuestra distribución o rendimiento.
"""
import argparse
from collections import Counter
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sys


def referencia(ruta):
    totales = Counter()
    registros = 0
    campos = ["id_reserva", "hotel", "canal", "noches", "importe"]
    with ruta.open(encoding="utf-8-sig", newline="") as entrada:
        lector = csv.reader(entrada, strict=True)
        if next(lector, None) != campos:
            raise ValueError("La cabecera no coincide con el CSV de UT2.")
        for fila in lector:
            if not fila:
                continue
            if len(fila) != 5:
                raise ValueError(f"Entrada, línea {lector.line_num}: se requieren cinco campos.")
            identificador, hotel, canal, noches, importe = fila
            int(identificador)
            n = int(noches)
            precio = Decimal(importe)
            if (not hotel.strip() or "\t" in hotel or "\n" in hotel
                    or "\r" in hotel or not canal.strip()
                    or n < 1 or not precio.is_finite() or precio < 0):
                raise ValueError(f"Entrada, línea {lector.line_num}: dato fuera del contrato.")
            totales[hotel] += n
            registros += 1
    return dict(totales), registros


def leer_salida(ruta):
    resultado = {}
    with ruta.open(encoding="utf-8-sig", newline="") as salida:
        for numero, linea in enumerate(salida, 1):
            linea = linea.rstrip("\r\n")
            if not linea:
                continue
            campos = linea.split("\t")
            if len(campos) != 2:
                raise ValueError(f"Salida, línea {numero}: se espera hotel<TAB>noches.")
            hotel, texto = campos
            total = int(texto)
            if not hotel.strip() or total < 1:
                raise ValueError(f"Salida, línea {numero}: clave o total inválido.")
            if hotel in resultado:
                raise ValueError(f"Hotel repetido en la salida: {hotel!r}.")
            resultado[hotel] = total
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path)
    parser.add_argument("salida", type=Path)
    args = parser.parse_args()
    try:
        esperado, registros = referencia(args.entrada)
        observado = leer_salida(args.salida)
        diferencias = [
            f"{hotel}: esperado={esperado.get(hotel)!r}, obtenido={observado.get(hotel)!r}"
            for hotel in sorted(esperado.keys() | observado.keys())
            if esperado.get(hotel) != observado.get(hotel)
        ]
        if diferencias:
            raise ValueError("Totales distintos por hotel:\n" + "\n".join(diferencias))
    except (OSError, UnicodeError, ValueError, csv.Error, InvalidOperation) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"CORRECTO: {registros} registros, {len(esperado)} hoteles, "
          f"{sum(esperado.values())} noches.")
    for hotel, total in sorted(esperado.items()):
        print(f"{hotel}\t{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
