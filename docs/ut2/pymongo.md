---
title: 2.9 MongoDB y Python
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.9. MongoDB y Python

Recepción no abre `mongosh` a las ocho: abre un **script**. [PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/) es el conector oficial. Aquí comprobáis el criterio **b)** (el procesamiento lo lanza la *app*) y el **d)** (metéis `mascota` en 2027 y los `find` de 2026 **no** se rompen).

El *shell* del [2.6](mongodb.md) enseña el oficio. Python es el mismo gesto con otro teclado: filtro, proyección, cursor, *pipeline*, `WriteConcern`. Las reservas y opiniones son las del hotel, no un catálogo de cine ni el proyecto de otro ciclo.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install pymongo
```

En el aula usad **4.x** (la que instale `pip` ese día). La URI típica es `mongodb://localhost:27017`. Atlas trae usuario, `tls` y a menudo `mongodb+srv://`. **No** subáis la URI con contraseña a Moodle en claro.

## El primer cable

```python
from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017")
hotel = cliente.hotel          # o cliente["hotel"]
print(hotel.list_collection_names())

reservas = hotel.reservas      # o hotel["reservas"]
print(reservas.find_one({"hotel": "Laredo"}))
```

Si no habéis importado aún:

```bash
mongoimport --db hotel --collection reservas --file docs/assets/practicas/reservas_mongo.jsonl
mongoimport --db hotel --collection opiniones --file docs/assets/practicas/hotel-mongo/opiniones.jsonl
```

Hay un script de aula que imprime el parte: [`parte_gerencia.py`](../assets/practicas/hotel-pymongo/parte_gerencia.py). Arrancad un `mongod` (el del [2.6](mongodb.md), no el *replica set* y el suelto a la vez: los dos quieren el **27017**).

```powershell
$env:HOTEL_MONGO_URI = "mongodb://localhost:27017"
python docs/assets/practicas/hotel-pymongo/parte_gerencia.py
```

## Una llave, no un enchufe por clic

`MongoClient` **no** es “abro el socket, pregunto, cierro”. Arranca un ***pool*** (por defecto, del orden de **100** conexiones). Cada `find` toma una y la suelta. Abrir un cliente **dentro** del `for` de un Flask es el error clásico.

Podéis pasar la URI o trocearla. Opciones que en el hotel importan:

```python
cliente = MongoClient(
    "mongodb://localhost:27017",
    maxPoolSize=50,
    connectTimeoutMS=2000,
    serverSelectionTimeoutMS=4000,
    retryWrites=True,
    wtimeout=2500,
)
```

`wtimeout` evita que un cobro con `w: "majority"` se quede **colgado** si Potes no contesta ([2.8](replicas-shards.md)). Si no hay servidor, salta `ServerSelectionTimeoutError`: capturadlo; no dejéis un *traceback* crudo en recepción.

```python
print(cliente.list_database_names())
print(cliente.address)
```

Set `hotelrs` (varios hosts + nombre del conjunto):

```python
uri = "mongodb://rs-laredo:27017,rs-potes:27017,rs-noja:27017/?replicaSet=hotelrs"
```

En Atlas, `mongodb+srv://…` ya lista los miembros. `tls=True` va en la cadena. El *pool* ve los tres *hosts*; no hace falta “elegir el primario a mano”.

**Pereza:** `cliente.hotel` y `hotel.reservas` **no** crean nada en disco hasta el primer `insert`. Un typo (`cliente.htel`) no falla al instante: falla cuando escribís.

## Preguntar sin vaciar el BSON

`find` devuelve un **cursor**, no una lista. `count_documents` cuenta con el mismo filtro.

```python
filtro = {"canal": "web", "noches": {"$gte": 3}}
print(reservas.count_documents(filtro))

proy = {"hotel": 1, "importe": 1, "noches": 1, "_id": 0}
for doc in reservas.find(filtro, proy):
    print(doc)
```

Sin `"_id": 0` el identificador **sigue** saliendo. Los arrays se filtran como en el *shell*: `{"extras": "parking"}` encuentra el documento que **contiene** ese valor.

BSON no es JSON. Para volcar a un fichero o a una API:

```python
from bson.json_util import dumps

cursor = reservas.find({"hotel": "Laredo"})
print(dumps(cursor, indent=2, ensure_ascii=False))
```

`ObjectId` y fechas salen con `$oid` / `$date`. `json.dumps` de la biblioteca estándar **rompe** con esos tipos.

## El parte: agregación en el motor

El criterio **b)** aquí no es YARN: es **dejar el trabajo en Mongo** (`aggregate`) y que Python solo **imprima**. Tres fases que gerencia pide cada mañana: filtrar, agrupar, ordenar.

```python
from pymongo import DESCENDING

pipeline = [
    {"$match": {"canal": {"$in": ["web", "ota"]}}},
    {
        "$group": {
            "_id": "$hotel",
            "noches": {"$sum": "$noches"},
            "media": {"$avg": "$importe"},
        }
    },
    {"$sort": {"noches": DESCENDING}},
]
for fila in reservas.aggregate(pipeline):
    print(fila)
```

Extras (array) → una fila por valor, luego recuento:

```python
por_extra = [
    {"$unwind": "$extras"},
    {"$group": {"_id": "$extras", "reservas": {"$sum": 1}}},
    {"$sort": {"reservas": DESCENDING}},
]
```

`$lookup` pega opiniones al hotel. Nuestros JSONL se cruzan por **nombre**, no por `ObjectId` (el join “de cine” del temario de referencia usaba `movie_id`; aquí el campo natural es `hotel`):

```python
from bson.objectid import ObjectId

pipeline = [
    {"$match": {"hotel": "Laredo"}},
    {
        "$lookup": {
            "from": "opiniones",
            "localField": "hotel",
            "foreignField": "hotel",
            "as": "criticas",
        }
    },
]
for fila in reservas.aggregate(pipeline):
    print(fila["hotel"], "opiniones:", len(fila["criticas"]))
```

Si la opinión apuntara a `_id` de una reserva, el `localField` sería `_id` y el `foreignField` un `ObjectId` guardado. Si **cada** pantalla necesita `$lookup`, el [2.7](modelado.md) os está pidiendo embeber un trozo.

## El cursor: cortar, ordenar, saltar

Lo que en el *pipeline* es `$limit` / `$sort` / `$skip`, en el cursor son métodos **encadenados**. Mismo resultado; elegid uno y no mezcléis sin motivo.

```python
from pymongo import ASCENDING, DESCENDING

solo_dos = reservas.find(
    {"hotel": "Potes"},
    {"_id": 0, "canal": 1, "noches": 1, "importe": 1},
).sort("importe", DESCENDING).limit(2)

for doc in solo_dos:
    print(doc)
```

Equivalente:

```python
pipeline = [
    {"$match": {"hotel": "Potes"}},
    {"$project": {"_id": 0, "canal": 1, "noches": 1, "importe": 1}},
    {"$sort": {"importe": DESCENDING}},
    {"$limit": 2},
]
```

Dos criterios (noche y nombre): lista de tuplas.

```python
reservas.find({}).sort([("hotel", ASCENDING), ("importe", DESCENDING)])
```

Paginación de aula: `.sort("checkin", ASCENDING).skip(10).limit(10)`. En colecciones **enormes**, `skip` recorre lo saltado: mejor un rango (`"_id": {"$gt": ultimo}`).

## Escribir, borrar, enmendar

### Altas

`insert_one` → `InsertOneResult`: `acknowledged` (falso si `w=0`) e `inserted_id`.

```python
alta = reservas.insert_one({
    "hotel": "Noja",
    "canal": "recepcion",
    "noches": 2,
    "importe": 110,
    "mascota": True,   # d): el campo no existía en 2026
})
print(alta.acknowledged, alta.inserted_id)
```

`insert_many` → `InsertManyResult` (lista de ids). Una opinión que **señala** una reserva concreta:

```python
from bson.objectid import ObjectId

id_reserva = reservas.find_one({"hotel": "Laredo"})["_id"]
hotel["opiniones"].insert_one({
    "hotel": "Laredo",
    "reserva_id": ObjectId(id_reserva) if not isinstance(id_reserva, ObjectId) else id_reserva,
    "autor": "Mostrador",
    "cuerpo": "El huésped pidió cuna a última hora.",
})
```

`_id` o índice único ya ocupado → `DuplicateKeyError`. Informad; no tragéis el error.

```python
from pymongo.errors import DuplicateKeyError

try:
    reservas.insert_one({"_id": alta.inserted_id, "hotel": "Fantasma"})
except DuplicateKeyError:
    print("esa reserva ya está en el libro")
```

### Bajas

`delete_one` / `delete_many` → `deleted_count`. Vaciar con `delete_many({})` deja la colección; `reservas.drop()` la **quita** (índices incluidos). En el hotel, `drop` de `reservas` un viernes es noticia.

### Cambios

Segundo argumento: **operador** (`$set`, `$inc`, `$unset`…). Si pasáis un documento pelado, **sustituye** el entero.

```python
r = reservas.update_many(
    {"importe": {"$lt": 0}},
    {"$set": {"importe": 0, "aviso": "importe corregido"}},
)
print(r.matched_count, r.modified_count)
```

`upsert=True`: si no hay match, **inserta**. `bypass_document_validation=True` se salta el validador del [2.7](modelado.md): solo con permiso y motivo (migración). Por defecto, `False`.

### A granel

Varias operaciones en un *batch*:

```python
from pymongo import UpdateOne, DeleteOne

reservas.bulk_write([
    UpdateOne({"hotel": "Comillas", "canal": "web"}, {"$inc": {"noches": 1}}),
    DeleteOne({"hotel": "prueba"}),
])
```

## Las mismas promesas que el 2.8

Lectura: clases de `ReadPreference`. Escritura: `WriteConcern`. Se fijan en el cliente, en `get_database` / `get_collection` o en `with_options` para **una** operación.

```python
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern

cliente = MongoClient("mongodb://localhost:27017", replicaSet="hotelrs")
print(cliente.read_preference)

informes = cliente.get_database("hotel", read_preference=ReadPreference.SECONDARY)
mostrador = informes.get_collection("reservas", read_preference=ReadPreference.PRIMARY)

ocupacion = mostrador.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
cobro = mostrador.with_options(write_concern=WriteConcern(w="majority", wtimeout=2500))
cobro.insert_one({"hotel": "Potes", "canal": "web", "noches": 1, "importe": 95})
```

Valores: `PRIMARY`, `PRIMARY_PREFERRED`, `SECONDARY`, `SECONDARY_PREFERRED`, `NEAREST` (los mismos nombres del [2.8](replicas-shards.md)). El informe de ocupación puede ir a Noja; el cobro, no.

## Dos papeles, un “sí” (transacciones)

Un `update` **de un** documento ya es atómico: por eso el [2.7](modelado.md) embebe el cobro cuando cabe. Si el cobro vive en `cobros` y la reserva en `reservas`, hace falta una **sesión** y, en la práctica, un **replica set** (un `mongod` suelto de juguete, según versión, **no** abre transacción).

Mongo ofrece dos APIs. La **Core** (`start_transaction` / `commit_transaction`) os deja el reintento. La **Callback** (`with_transaction`) inicia, ejecuta, hace *commit* o aborta y **reintenta** el *commit*. Es la que usaréis.

Historia de aula: entra un pedido de parking y **a la vez** baja el cupo.

```python
from pymongo import MongoClient, ReadPreference
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

URI = "mongodb://localhost:27017/?replicaSet=hotelrs"
cliente = MongoClient(URI)
majority = WriteConcern("majority", wtimeout=2500)
bd = cliente.get_database("hotel", write_concern=majority)

def callback(sesion):
    reservas = sesion.client.hotel.reservas
    plazas = sesion.client.hotel.parking
    reservas.insert_one(
        {"hotel": "Laredo", "canal": "web", "extras": ["parking"], "noches": 1},
        session=sesion,
    )
    plazas.update_one(
        {"hotel": "Laredo", "libres": {"$gte": 1}},
        {"$inc": {"libres": -1}},
        session=sesion,
    )

with cliente.start_session() as sesion:
    sesion.with_transaction(
        callback,
        read_concern=ReadConcern("local"),
        write_concern=majority,
        read_preference=ReadPreference.PRIMARY,
    )
```

Cada operación **lleva** `session=sesion`. Si no hay plaza, el `update` no toca nada: decidid en el *callback* si abortáis. El banco, si exige ACID de libro mayor, sigue siendo territorio [relacional](../ut1/almacenamiento.md).

!!! note "ODM"
    Un mapeo objeto-documento (Beanie + Pydantic, etc.) es un atajo de *app*. En esta UT el RA2 se demuestra con **PyMongo**. No hace falta un *framework* encima para el criterio **b)**.

## Extra: una URL para gerencia (Flask)

El RA2 **no** pide un MVC. Si el profesor quiere ver el dato en el navegador, Flask basta. Distinto del “Hola / Adiós / listado de usuarios” de otros apuntes: aquí la ruta útil es la **ocupación**.

```bash
pip install pymongo flask
```

```
mostrador/
  app.py
  conexion.py
  templates/
    inicio.html
    ocupacion.html
```

`flask.g` vive **una petición**. Guardad ahí el cliente (el *pool*), no creéis uno por ruta.

```python
# conexion.py
import os
from flask import g
from pymongo import MongoClient

def hotel_db():
    db = getattr(g, "_hotel", None)
    if db is None:
        uri = os.environ.get("HOTEL_MONGO_URI", "mongodb://localhost:27017")
        db = g._hotel = MongoClient(uri, maxPoolSize=50, wtimeout=2500)["hotel"]
    return db
```

```python
# app.py
from flask import Flask, render_template
from pymongo import DESCENDING
import conexion

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/ocupacion")
def ocupacion():
    col = conexion.hotel_db()["reservas"]
    filas = list(col.aggregate([
        {"$group": {"_id": "$hotel", "noches": {"$sum": "$noches"}}},
        {"$sort": {"noches": DESCENDING}},
    ]))
    return render_template("ocupacion.html", filas=filas)
```

```html
<!-- templates/ocupacion.html -->
<h1>Noches por sede</h1>
<ul>
{% for f in filas %}
  <li>{{ f._id }}: {{ f.noches }}</li>
{% endfor %}
</ul>
```

```powershell
cd mostrador
flask --app app run --debug
```

`http://127.0.0.1:5000/ocupacion`. Jinja: `{{ variable }}` y `{% for %}`. Eso es el *bridge* a una *app*; el oficio de Big Data ya lo hizo `aggregate`.

## Cómo se cierra el apartado (y la UT2)

Un script que suma noches por hotel es **b)**. Un `insert_one` con `mascota` que no tumba los `find` viejos es **d)**. `WriteConcern` y `ReadPreference` en el cliente son el [2.8](replicas-shards.md) con otro idioma.

!!! success "Cerrar la UT2"
    HDFS **deposita** el lago y **tolera** discos muertos. YARN/MapReduce **demuestran** el cómputo partido. Mongo **guarda** el JSON inquieto. Réplicas y *shards* **prueban** fallos y **muestran** el crecimiento. PyMongo **enciende** eso desde Python. Hive, Spark y el resto son **módulos** que enchufáis después.

## Relación con el RA2

| Criterio | Aquí |
| --- | --- |
| **b)** | `aggregate`, cursores, *bulk*; el trabajo pesado **dentro** del motor |
| **d)** | Campo nuevo en un `insert`; `find` antiguos siguen |
| **c)** | `ReadPreference` / `WriteConcern` / transacción sobre `hotelrs` |

## Para practicar (Moodle manda)

1. **Parte.** Importad `reservas` y `opiniones`. Ejecutad `parte_gerencia.py` (o el vuestro). Entregad captura de `count_documents`, un `find` de Laredo y el `$group` por hotel.
2. **Esquema que crece.** Insertad una reserva de 2027 con `mascota: true`. Un `find({"mascota": true})` y otro `find({"hotel": "Laredo"})` que **siga** devolviendo las de 2026. Eso es **d)** en Python.
3. **Cursor frente a *pipeline*.** La misma pregunta (Potes, orden por importe, dos filas) de las dos formas. Una frase: cuándo usaríais cada una.
4. **Errores.** Forzad un `DuplicateKeyError` y un `ServerSelectionTimeoutError` (URI falsa). Capturad; no vale el *traceback* suelto.
5. **Promesas.** Sobre `hotelrs` (si el lab está levantado): un `insert_one` con `WriteConcern(w="majority", wtimeout=2500)` y un `find` con `SECONDARY`. Relacionadlo con el viernes de Laredo del [2.8](replicas-shards.md).
6. (Opcional) Ruta Flask `/ocupacion` con `g` y el *pool*. No hace falta login ni un MVC de otro proyecto.
7. (Opcional) Transacción `reservas` + `parking` en el *replica set*. Si el `mongod` es suelto, documentad **por qué** falla.

## Referencias

- [PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/)
- [Agregación](https://www.mongodb.com/docs/manual/aggregation/) y [transacciones](https://www.mongodb.com/docs/manual/core/transactions/)
- [Flask](https://flask.palletsprojects.com/) (solo el extra)
- [2.6 MongoDB](mongodb.md) · [2.7 Modelado](modelado.md) · [2.8 Réplicas](replicas-shards.md)
