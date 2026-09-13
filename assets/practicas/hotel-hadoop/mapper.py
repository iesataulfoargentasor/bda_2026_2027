#!/usr/bin/env python3
"""Mapper de aula: una palabra -> 1. Limpia puntuación y unifica mayúsculas."""
import string
import sys

tabla = str.maketrans("", "", string.punctuation)

for linea in sys.stdin:
    linea = linea.strip()
    if not linea:
        continue
    for palabra in linea.translate(tabla).lower().split():
        if palabra:
            print(f"{palabra}\t1")
