#!/usr/bin/env python3
"""Parte de noches reservadas del grupo hotelero. URI por variable de entorno o localhost."""
import os

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError

URI = os.environ.get("HOTEL_MONGO_URI", "mongodb://localhost:27017")


def imprimir_parte(cliente):
    reservas = cliente["hotel"]["reservas"]
    print("colecciones:", cliente["hotel"].list_collection_names())
    print("reservas:", reservas.count_documents({}))
    print("una de Laredo:", reservas.find_one({"hotel": "Laredo"}))

    print("\nNoches por hotel")
    pipeline = [
        {"$group": {"_id": "$hotel", "noches": {"$sum": "$noches"}, "media": {"$avg": "$importe"}}},
        {"$sort": {"noches": DESCENDING}},
    ]
    for fila in reservas.aggregate(pipeline):
        print(f"  {fila['_id']}: {fila['noches']} noches, media {fila['media']:.1f} €")

    print("\nWeb, ≥3 noches (tope 5)")
    filtro = {"canal": "web", "noches": {"$gte": 3}}
    proy = {"hotel": 1, "importe": 1, "noches": 1, "_id": 0}
    for doc in reservas.find(filtro, proy).sort("importe", ASCENDING).limit(5):
        print(" ", doc)


def main():
    try:
        with MongoClient(URI, serverSelectionTimeoutMS=4000) as cliente:
            cliente.admin.command("ping")
            imprimir_parte(cliente)
    except PyMongoError as exc:
        raise SystemExit(
            f"No se pudo obtener el parte ({type(exc).__name__}). "
            "Comprueba servicio, red, base y permisos."
        ) from None


if __name__ == "__main__":
    main()
