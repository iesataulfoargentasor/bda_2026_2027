#!/usr/bin/env python3
"""Reducer: suma noches por hotel (claves ya agrupadas)."""
import sys

actual, total = None, 0
for linea in sys.stdin:
    linea = linea.strip()
    if not linea:
        continue
    hotel, n = linea.split("\t", 1)
    try:
        n = int(n)
    except ValueError:
        continue
    if hotel != actual:
        if actual is not None:
            print(f"{actual}\t{total}")
        actual, total = hotel, n
    else:
        total += n
if actual is not None:
    print(f"{actual}\t{total}")
