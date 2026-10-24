#!/usr/bin/env python3
"""Reserva una plaza y registra el pedido en una transacción de hotel_tx.

Requiere HOTEL_MONGO_URI para un replica set accesible (UT2, apartado 2.9).
Primera ejecución: confirma una reserva. Segunda: sin plazas, no inserta nada.
Para repetir desde cero, el docente debe reiniciar solo los datos de hotel_tx.
"""
import os

from bson import ObjectId
from pymongo import MongoClient, ReadPreference
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern


def reservar(cliente, identificador, nombre_bd="hotel_tx"):
    bd = cliente.get_database(nombre_bd)

    def operacion(sesion):
        resultado = bd.parking.update_one(
            {"_id": "Laredo", "libres": {"$gte": 1}},
            {"$inc": {"libres": -1}},
            session=sesion,
        )
        if resultado.modified_count != 1:
            raise ValueError("No quedan plazas: no se crea la reserva")
        bd.reservas.insert_one(
            {"_id": identificador, "hotel": "Laredo", "extras": ["parking"], "noches": 1},
            session=sesion,
        )

    with cliente.start_session() as sesion:
        sesion.with_transaction(
            operacion,
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority", wtimeout=5000),
            read_preference=ReadPreference.PRIMARY,
        )


def main():
    uri = os.environ.get("HOTEL_MONGO_URI")
    if not uri:
        raise SystemExit("Define HOTEL_MONGO_URI con la URI del replica set accesible")
    confirmada = False
    try:
        with MongoClient(uri, serverSelectionTimeoutMS=5000) as cliente:
            estado = cliente.admin.command("hello")
            if not estado.get("setName"):
                raise ValueError("Esta práctica requiere un replica set; revisa HOTEL_MONGO_URI")
            # Solo inicializa una vez: no repone plazas al repetir el programa.
            parking = cliente.hotel_tx.get_collection(
                "parking", write_concern=WriteConcern("majority", wtimeout=5000)
            )
            parking.update_one(
                {"_id": "Laredo"}, {"$setOnInsert": {"libres": 1}}, upsert=True
            )
            # Fuera del callback: el mismo id se conserva durante sus reintentos.
            identificador = ObjectId()
            print("Identificador de esta ejecución:", identificador)
            reservar(cliente, identificador)
            confirmada = True
            print("Reserva confirmada:", identificador)
            print("Plazas:", parking.find_one({"_id": "Laredo"}))
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    except PyMongoError as exc:
        if confirmada:
            raise SystemExit(
                f"Reserva confirmada; no se pudo consultar el estado final ({type(exc).__name__}). "
                "Comprueba el identificador mostrado antes de repetir la operación."
            ) from None
        raise SystemExit(
            f"Operación no confirmada ({type(exc).__name__}). "
            "Revisa conectividad, topología y estado antes de reintentar."
        ) from None


if __name__ == "__main__":
    main()
