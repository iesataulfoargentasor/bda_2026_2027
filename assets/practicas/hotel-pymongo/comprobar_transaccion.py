#!/usr/bin/env python3
"""Prueba éxito, falta de cupo y rollback en una base temporal propia.

Ejecutar junto a reservar_parking.py, con HOTEL_MONGO_URI del replica set.
Conserva la base temporal si falla; la elimina solo si todo se comprueba.
"""
import os
from uuid import uuid4
from pymongo import MongoClient, ReadPreference
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.write_concern import WriteConcern
from reservar_parking import reservar


def exigir(condicion, mensaje):
    if not condicion:
        raise ValueError(mensaje)


def comprobar(cliente):
    exigir(bool(cliente.admin.command("hello").get("setName")),
           "Esta prueba requiere un replica set")
    nombre = "hotel_tx_prueba_" + uuid4().hex
    print("Base temporal:", nombre)
    bd = cliente.get_database(nombre, write_concern=WriteConcern("majority", wtimeout=5000),
                              read_preference=ReadPreference.PRIMARY)
    bd.parking.insert_one({"_id": "Laredo", "libres": 1})
    bd.create_collection("reservas")
    reservar(cliente, "prueba-01", nombre)
    exigir(bd.parking.find_one({"_id": "Laredo"})["libres"] == 0, "No se descontó la plaza")
    exigir(bd.reservas.count_documents({}) == 1, "No hay una reserva")
    try:
        reservar(cliente, "prueba-02", nombre)
    except ValueError as exc:
        exigir(str(exc) == "No quedan plazas: no se crea la reserva", "Rechazo inesperado")
    else:
        raise ValueError("Se confirmó una reserva sin cupo")
    exigir(bd.parking.find_one({"_id": "Laredo"})["libres"] == 0, "Cambió el cupo tras el rechazo")
    exigir(bd.reservas.count_documents({}) == 1, "Cambió el recuento tras el rechazo")
    print("Correcto: éxito y rechazo sin cupo")
    # Solo esta base temporal: preparar un cupo para probar el fallo posterior.
    bd.parking.update_one({"_id": "Laredo"}, {"$set": {"libres": 1}})
    antes = list(bd.reservas.find({}).sort("_id", 1))
    try:
        reservar(cliente, "prueba-01", nombre)  # Ya existe: falla después del descuento.
    except DuplicateKeyError:
        pass
    else:
        raise ValueError("No se rechazó el identificador duplicado")
    exigir(bd.parking.find_one({"_id": "Laredo"})["libres"] == 1, "El aborto no conservó el cupo")
    exigir(list(bd.reservas.find({}).sort("_id", 1)) == antes, "El aborto cambió las reservas")
    print("Correcto: el aborto conserva una plaza y la reserva preexistente")
    cliente.drop_database(nombre)
    print("Base temporal retirada; hotel y hotel_tx no se han modificado")


def main():
    uri = os.environ.get("HOTEL_MONGO_URI")
    if not uri:
        raise SystemExit("Define HOTEL_MONGO_URI con la URI del replica set")
    try:
        with MongoClient(uri, serverSelectionTimeoutMS=5000) as cliente:
            comprobar(cliente)
    except (PyMongoError, ValueError) as exc:
        raise SystemExit(
            f"Prueba no completada ({type(exc).__name__}). "
            "Revisa el entorno y la base temporal mostrada, si llegó a crearse."
        ) from None


if __name__ == "__main__":
    main()
