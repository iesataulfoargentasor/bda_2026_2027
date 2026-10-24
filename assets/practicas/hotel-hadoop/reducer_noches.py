#!/usr/bin/env python3
"""Reducer: suma noches por hotel (claves ya agrupadas)."""
import sys

actual, total = None, 0
for linea in sys.stdin:
    # Conservamos la clave tal como la emitió el mapper.
    linea = linea.rstrip("\r\n")
    if not linea:
        continue
    try:
        hotel, n = linea.split("\t", 1)
        n = int(n)
        if not hotel or n < 1:
            raise ValueError("clave vacía o noches no positivas")
    except ValueError as exc:
        print(f"Par inválido recibido por el reducer: {exc}", file=sys.stderr)
        sys.exit(1)
    if hotel != actual:
        if actual is not None:
            print(f"{actual}\t{total}")
        actual, total = hotel, n
    else:
        total += n
if actual is not None:
    print(f"{actual}\t{total}")
