#!/usr/bin/env python3
"""Parte de ocupación del grupo hotelero. URI por variable de entorno o localhost."""
import os

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import ServerSelectionTimeoutError

URI = os.environ.get("HOTEL_MONGO_URI", "mongodb://localhost:27017")


def conectar():
    cliente = MongoClient(URI, serverSelectionTimeoutMS=4000, wtimeout=2500)
    cliente.admin.command("ping")
    return cliente


def main():
    try:
        cliente = conectar()
    except ServerSelectionTimeoutError as exc:
        raise SystemExit(f"No hay mongod en {URI}: {exc}") from exc

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


if __name__ == "__main__":
    main()
