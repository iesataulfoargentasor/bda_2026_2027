#!/usr/bin/env python3
"""CSV de cinco columnas -> hotel\tnoches; un registro por línea física.

Contrato: id_reserva,hotel,canal,noches,importe. Rechaza datos inválidos:
descartarlos silenciosamente produciría totales aparentemente correctos.
"""
import csv
from decimal import Decimal, InvalidOperation
import sys

cabecera = ["id_reserva", "hotel", "canal", "noches", "importe"]
for numero, linea in enumerate(sys.stdin, 1):
    if not linea.strip():
        continue
    try:
        partes = next(csv.reader([linea.lstrip("\ufeff")], strict=True))
        if partes == cabecera:
            continue
        if len(partes) != 5:
            raise ValueError("se requieren las cinco columnas del CSV de UT2")
        identificador, hotel, canal, noches_texto, importe = partes
        int(identificador)
        noches = int(noches_texto)
        precio = Decimal(importe)
        if not hotel.strip() or "\t" in hotel or not canal.strip():
            raise ValueError("hotel/canal vacío o tabulador en la clave")
        if noches < 1 or not precio.is_finite() or precio < 0:
            raise ValueError("noches o importe fuera del contrato")
    except (ValueError, csv.Error, InvalidOperation) as exc:
        print(f"Registro {numero} del fragmento: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"{hotel}\t{noches}")
