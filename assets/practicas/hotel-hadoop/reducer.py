#!/usr/bin/env python3
"""Reducer de aula: Hadoop ya agrupa claves consecutivas. No uses un dict global."""
import sys

actual, total = None, 0
for linea in sys.stdin:
    linea = linea.strip()
    if not linea:
        continue
    palabra, n = linea.split("\t", 1)
    try:
        n = int(n)
    except ValueError:
        continue
    if palabra != actual:
        if actual is not None:
            print(f"{actual}\t{total}")
        actual, total = palabra, n
    else:
        total += n
if actual is not None:
    print(f"{actual}\t{total}")
