---
title: 2.9 MongoDB y Python
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.9. MongoDB y Python

[PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/) es el conector oficial. Aquí **comprobáis** consultas y agregados sobre el hotel (criterios **b)** a escala de aplicación y **d)** al insertar documentos nuevos sin migrar).

```bash
pip install pymongo
```

URI del aula (local típico): `mongodb://localhost:27017`. En Atlas vendrá con usuario y `tls`. **No** subáis la URI con contraseña a Moodle en texto plano.

```python
from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017")
col = cliente["hotel"]["reservas"]

print(col.count_documents({}))
print(col.find_one({ "hotel": "Laredo" }))
```

`MongoClient` es un **pool**: no abras uno por petición en un bucle.

## Consultas y cursores

```python
filtro = { "canal": "web", "noches": { "$gte": 3 } }
proy = { "hotel": 1, "importe": 1, "_id": 0 }

for doc in col.find(filtro, proy).sort("importe", -1).limit(5):
    print(doc)
```

`skip` + `limit` pagina; en colecciones enormes mejor **rango** (`_id > ultimo`).

## Agregación (el “MapReduce casero” de Mongo)

```python
pipeline = [
    { "$match": { "canal": { "$in": ["web", "ota"] } } },
    { "$group": {
        "_id": "$hotel",
        "noches": { "$sum": "$noches" },
        "media": { "$avg": "$importe" },
    }},
    { "$sort": { "noches": -1 } },
]
for fila in col.aggregate(pipeline):
    print(fila)
```

Tres fases: filtrar, agrupar, ordenar. Es el mismo oficio que el job de [2.4](computacion-distribuida.md), **dentro** del motor documental.

`$lookup` une colecciones (un *join* suave). Úsalo con tiento; si lo necesitas siempre, revisa el [modelado](modelado.md).

## CRUD

```python
col.insert_one({ "hotel": "Noja", "canal": "recepcion", "noches": 2, "importe": 110 })
col.insert_many([
    { "hotel": "Potes", "canal": "web", "noches": 4, "importe": 240 },
    { "hotel": "Comillas", "canal": "ota", "noches": 1, "importe": 75 },
])

col.update_many({ "importe": { "$lt": 0 } }, { "$set": { "importe": 0 } })
col.delete_many({ "hotel": "prueba" })
```

Errores: captura `DuplicateKeyError` si chocas con un `_id` único. `write_concern` / `read_preference` en el cliente alinean con [2.8](replicas-shards.md).

## Transacciones

En un **replica set** (no en un `mongod` suelto de juguete, según versión) puedes agrupar “inserta cobro **y** marca reserva” con sesión y *callback*. En esta UT basta saber: **existen** para cuando dos colecciones deben ir a la una; el cobro de la caja sigue siendo territorio [ACID relacional](../ut1/almacenamiento.md) si el banco lo exige.

## Mini caso (sin Flask)

1. `mongoimport` del JSONL de reservas.
2. Script que imprime ocupación (suma de `noches`) por `hotel`.
3. Inserta una reserva de 2027 con un campo **nuevo** (`mascota: true`) y comprueba que los `find` viejos **no rompen**.

Eso es **d)** en Python. Un MVC o una API Flask son un extra si el profesor los pide; el RA2 no exige un framework web.

!!! success "Cerrar la UT2"
    HDFS **deposita** el lago y **tolera** discos muertos. YARN/MapReduce **demuestran** el cómputo partido. Mongo **guarda** el JSON inquieto. Réplicas y shards **prueban** fallos y **muestran** el crecimiento. El ecosistema (Hive, Spark…) son **módulos** que enchufas después.
