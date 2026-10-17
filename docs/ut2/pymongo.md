---
title: 2.9 MongoDB y Python
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.9. MongoDB y Python

Gerencia puede obtener el parte de las ocho mediante un **script**, sin escribir consultas manualmente en `mongosh`. [PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/) es el conector oficial. Aquí comprobáis el criterio **b)** (el procesamiento lo lanza la *app*) y el **d)** (metéis `mascota` en 2027 y los `find` de 2026 **no** se rompen).

El *shell* del [2.6](mongodb.md) enseña el oficio. Python es el mismo gesto con otro teclado: filtro, proyección, cursor, *pipeline*, `WriteConcern`. Las reservas y opiniones son las del hotel, no un catálogo de cine ni el proyecto de otro ciclo.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install "pymongo>=4,<5"
```

En el aula usad **PyMongo 4.x** y anotad la versión instalada. La URI típica es `mongodb://localhost:27017`. Atlas trae usuario, `tls` y a menudo `mongodb+srv://`. **No** subáis la URI con contraseña a Moodle en claro.

## El primer cable

Importad una sola vez los JSONL en `hotel`: deben existir **15 reservas y 6 opiniones**. Las consultas de este bloque utilizan esos datos originales. `MongoClient` crea un cliente, el acceso a `cliente["hotel"]` obtiene una referencia a la base y `find_one` envía una consulta. No son tres formas equivalentes de conectar.

En programas completos, reutilizad el cliente y cerradlo al terminar, por ejemplo con `with MongoClient(...) as cliente:`. Para comprobar conectividad de manera explícita utilizad `cliente.admin.command("ping")`.

```python
from pymongo import MongoClient

cliente = MongoClient("mongodb://localhost:27017")
hotel = cliente.hotel          # o cliente["hotel"]
print(hotel.list_collection_names())

reservas = hotel.reservas      # o hotel["reservas"]
print(reservas.find_one({"hotel": "Laredo"}))
```

Si no habéis importado aún, desde la **raíz del repo** y con `mongoimport` instalado en el PC (el procedimiento y la comprobación de carga están en el [2.6](mongodb.md)):

```bash
mongoimport --host 127.0.0.1 --port 27017 --db hotel --collection reservas --file docs/assets/practicas/reservas_mongo.jsonl
mongoimport --host 127.0.0.1 --port 27017 --db hotel --collection opiniones --file docs/assets/practicas/hotel-mongo/opiniones.jsonl
```

Hay un script de aula que imprime el parte: [`parte_gerencia.py`](../assets/practicas/hotel-pymongo/parte_gerencia.py). Arrancad un `mongod` (el del [2.6](mongodb.md), no el *replica set* y el suelto a la vez: los dos quieren el **27017**).

```powershell
$env:HOTEL_MONGO_URI = "mongodb://localhost:27017"
python docs/assets/practicas/hotel-pymongo/parte_gerencia.py
```

## Una llave, no un enchufe por clic

Un cliente gestiona conexiones y descubre la topología. Crear uno por documento desperdicia ese trabajo. `connectTimeoutMS` limita el establecimiento de una conexión; `serverSelectionTimeoutMS` limita cuánto se busca un servidor adecuado. Ninguno equivale a cancelar automáticamente una escritura ya realizada.

Las opciones de reintento no hacen idempotente cualquier código de aplicación. Si el programa no sabe si se confirmó una operación, necesita un identificador de negocio para comprobarla y evitar duplicarla. Los errores mostrados al alumnado no deben imprimir una URI que pudiera contener contraseña.

`MongoClient` **no** es “abro el socket, pregunto, cierro”. Mantiene un ***pool*** que crece según la demanda, con un límite predeterminado de 100 conexiones por servidor; no abre 100 de golpe. Cada `find` toma una y la suelta. Abrir un cliente **dentro** del `for` de un Flask es el error clásico.

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

**Pereza:** `cliente.hotel` y `hotel.reservas` **no** crean nada en disco hasta el primer `insert`. Un typo (`cliente.htel`) no falla al instante: puede crear una base equivocada al escribir. Verificad el nombre antes de cargar datos.

## Preguntar sin vaciar el BSON

Construid primero el filtro como diccionario de Python. Las claves de operadores son cadenas (`"$gte"`); los booleanos son `True` y `False`, y el valor nulo es `None`. Copiar literalmente `true` del shell JavaScript produce un error en Python.

Una consulta vacía no demuestra fallo de conexión: puede no haber coincidencias. Contrastad `count_documents({})`, base y filtro. Al convertir un cursor completo en JSON o en una lista, cargáis sus resultados en memoria; el ejemplo siguiente limita la salida a diez documentos.

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

cursor = reservas.find({"hotel": "Laredo"}).limit(10)
print(dumps(cursor, indent=2, ensure_ascii=False))
```

`ObjectId` y fechas salen con `$oid` / `$date`. `json.dumps` de la biblioteca estándar **rompe** con esos tipos.

## El parte: agregación en el motor

Seguid la forma de los datos después de cada etapa. `$match` conserva reservas que cumplen el filtro; `$group` produce un documento por hotel; `$sort` ordena esos resúmenes. En `$sum: "$noches"`, el valor es una referencia al campo; en `$sum: 1`, se cuenta un documento.

`media` en el ejemplo es la **media del importe por reserva**, no el precio medio por noche. Este último exigiría dividir el importe total entre las noches totales, especificando qué reservas entran. Y la suma de noches no es un porcentaje de ocupación: faltan calendario y capacidad.

Aquí aprendemos a **dejar el trabajo en Mongo** (`aggregate`) y que Python solo reciba el resultado. Una agregación sobre un servidor independiente no demuestra computación distribuida; esa evidencia se obtiene con el experimento del [2.4](computacion-distribuida.md). Tres fases que gerencia pide cada mañana: filtrar, agrupar, ordenar.

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

En el `$lookup` anterior, cada reserva de Laredo recibe las opiniones de ese hotel. Con los datos originales salen **tres reservas**, cada una con **dos opiniones**. Sumar los tamaños de esos arrays daría seis asociaciones, no seis opiniones distintas. Para una fila por hotel, agrupad primero o consultad una colección de hoteles.

`$unwind` genera una fila por elemento del array. Si una reserva tiene dos extras, participa en dos filas: no suméis después su importe como si cada fila fuera una reserva diferente sin decidir cómo evitar la duplicación.

## El cursor: cortar, ordenar, saltar

Para comparar cursor y pipeline, consumid ambos sobre los mismos datos, con idéntico filtro, proyección y orden. En el fichero original Potes tiene importes 124, 490 y 280: los dos mayores son **490 y 280**. Si hay empates, añadid `_id` como desempate en ambos. La equivalencia no significa que cualquier cadena arbitraria de etapas produzca el mismo resultado.

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

Realizad las modificaciones sobre la base `hotel_escrituras`, preparada en el [2.6](mongodb.md). Antes de continuar, reasignad los manejadores:

```python
hotel = cliente["hotel_escrituras"]
reservas = hotel["reservas"]
```

Así las altas y cambios no alteran los 15 documentos originales del parte. En las respuestas de escritura distinguimos que el servidor haya confirmado la operación, que haya encontrado un documento y que realmente lo haya cambiado.

### Altas

Conservad `inserted_id` si otra colección necesita referenciar el documento. El identificador puede ser un `ObjectId` u otro tipo permitido: no lo convirtáis automáticamente a `ObjectId`. Si `find_one` devuelve `None`, comprobádlo antes de acceder a `["_id"]`.

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
    "reserva_id": id_reserva,  # conserva exactamente su valor y su tipo
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

El ejemplo marca un importe negativo para revisión y conserva su valor. Convertirlo automáticamente en cero alteraría la información sin justificar si era un error, una devolución u otro caso. Una modificación puede encontrar cero documentos: eso no siempre es un fallo técnico, pero debe interpretarse según la operación de negocio.

Segundo argumento: **operador** (`$set`, `$inc`, `$unset`…). `update_one` y `update_many` no admiten un documento ordinario como reemplazo: para sustituir el contenido se utiliza `replace_one`.

```python
r = reservas.update_many(
    {"importe": {"$lt": 0}},
    {"$set": {"aviso": "revisar importe negativo"}},
)
print(r.matched_count, r.modified_count)
```

`upsert=True`: si no hay match, **inserta**. `bypass_document_validation=True` se salta el validador del [2.7](modelado.md): solo con permiso y motivo (migración). Por defecto, `False`.

### A granel

`bulk_write` reduce viajes entre cliente y servidor; no convierte el lote en una transacción. Por defecto, un error puede detener las operaciones ordenadas siguientes, dejando las anteriores aplicadas. Comprobad el resultado y utilizad identificadores concretos si queréis afectar a una reserva determinada.

Varias operaciones en un *batch*:

```python
from pymongo import UpdateOne, DeleteOne

reservas.bulk_write([
    UpdateOne({"hotel": "Comillas", "canal": "web"}, {"$inc": {"noches": 1}}),
    DeleteOne({"hotel": "prueba"}),
])
```

## Las mismas promesas que el 2.8

Lectura: clases de `ReadPreference`. Escritura: `WriteConcern`. Se fijan en el cliente, en `get_database` / `get_collection` o mediante `with_options`, que devuelve un manejador nuevo con esas opciones para sus operaciones posteriores.

```python
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern

cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)  # URI interna del set, definida antes
print(cliente.read_preference)

informes = cliente.get_database("hotel", read_preference=ReadPreference.SECONDARY)
mostrador = informes.get_collection("reservas", read_preference=ReadPreference.PRIMARY)

ocupacion = mostrador.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
cobro = mostrador.with_options(write_concern=WriteConcern(w="majority", wtimeout=2500))
cobro.insert_one({"hotel": "Potes", "canal": "web", "noches": 1, "importe": 95})
```

Valores: `PRIMARY`, `PRIMARY_PREFERRED`, `SECONDARY`, `SECONDARY_PREFERRED`, `NEAREST` (los mismos nombres del [2.8](replicas-shards.md)). El informe de ocupación puede ir a Noja; el cobro, no.

### Ejecutar Python dentro de la red del replica set

Los nombres `rs-laredo`, `rs-potes` y `rs-noja` son internos de Docker. Para que el driver descubra los miembros sin configurar el DNS de Windows, mantened `hotel-rs` levantado y ejecutad desde la **raíz del repositorio**, en PowerShell:

```powershell
docker run --rm -it --network hotel-rs_default -v "${PWD}:/trabajo:ro" -w /trabajo python:3.12-slim bash
```

Este contenedor cliente necesita acceso a Internet para instalar PyMongo. En su Bash:

```bash
pip install "pymongo>=4,<5"
export HOTEL_MONGO_URI='mongodb://rs-laredo:27017,rs-potes:27017,rs-noja:27017/?replicaSet=hotelrs'
python docs/assets/practicas/hotel-pymongo/reservar_parking.py
```

La red se llama `hotel-rs_default` con el nombre de proyecto del Compose incluido. Si se ha cambiado el nombre del proyecto, adaptad la red. Usar `localhost:27017` dentro del contenedor cliente apuntaría al propio cliente, no a MongoDB.

## Dos papeles, un “sí” (transacciones)

Una actualización de un documento es atómica. Si una operación modifica documentos distintos, como el cupo de parking y la reserva, necesitamos una transacción explícita para confirmarlos juntos. **Un servidor standalone no admite transacciones multidocumento**; utilizamos el replica set preparado en el 2.8.

MongoDB ofrece una API explícita de inicio/commit/abort y una API de callback, `with_transaction`. Esta última puede reejecutar el callback o reintentar el commit ante determinados errores. Por tanto, dentro del callback no enviamos correos ni realizamos efectos externos que pudieran duplicarse.

El programa completo está en [reservar_parking.py](../assets/practicas/hotel-pymongo/reservar_parking.py). Usa una base independiente, `hotel_tx`, e inicializa **una plaza**, únicamente si aún no existe. Su núcleo es:

```python
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
```

`bd` e `identificador` se preparan fuera del callback. El programa lo ejecuta con lectura `snapshot`, escritura `majority` y preferencia `PRIMARY`. Todas las operaciones participantes llevan `session=sesion`.

La comprobación de `modified_count` es esencial: **no encontrar plazas no provoca automáticamente una excepción**. Sin esa comprobación, una transacción podría confirmar una reserva sin haber descontado cupo. Si la inserción falla después del descuento, el aborto también deshace ese descuento.

Prueba en una base `hotel_tx` nueva:

| Ejecución | Resultado esperado | Estado final |
| --- | --- | --- |
| Primera | Reserva confirmada | Una reserva y cero plazas |
| Segunda | Mensaje de falta de plazas | Sigue una reserva y cero plazas |
| Error de inserción dentro de una transacción | Aborto | Se conserva el cupo anterior |

No repongáis una plaza antes de la segunda ejecución: el objetivo es probar el rechazo. Para repetir el experimento desde cero, el docente reinicia solo los datos de `hotel_tx`. Un error de red o de confirmación requiere comprobar el estado antes de reintentar una operación de negocio.

!!! note "ODM"
    Un mapeo objeto-documento, como los basados en modelos de validación, puede simplificar una aplicación. En esta unidad usamos PyMongo para ver explícitamente filtros, sesiones y resultados. Un ODM no elimina la necesidad de comprender sus garantías.

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

`flask.g` vive **una petición**: crear allí un cliente nuevo por petición impediría reutilizar el pool entre peticiones. En esta aplicación guardamos un `MongoClient` en `app.extensions`, compartido por las rutas dentro del proceso. En un despliegue con varios procesos, cada uno crea su propio cliente.

```python
# conexion.py
import os
from flask import current_app
from pymongo import MongoClient

def iniciar(app):
    uri = os.environ.get("HOTEL_MONGO_URI", "mongodb://localhost:27017")
    app.extensions["mongo"] = MongoClient(uri, maxPoolSize=50, serverSelectionTimeoutMS=4000)

def hotel_db():
    return current_app.extensions["mongo"]["hotel"]
```

```python
# app.py
from flask import Flask, render_template
from pymongo import DESCENDING
import conexion

app = Flask(__name__)
conexion.iniciar(app)

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

La ruta conserva el nombre `/ocupacion`, pero muestra noches reservadas, no un porcentaje. La plantilla inicial permite visitar también `/`:

```html
<!-- templates/inicio.html -->
<h1>Parte de gerencia</h1>
<a href="{{ url_for('ocupacion') }}">Consultar noches reservadas por hotel</a>
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

Un script que suma noches por hotel practica procesamiento en el servidor; para demostrar el modelo distribuido de **b)** se añade la evidencia del 2.4. Un `insert_one` con `mascota` que no tumba los `find` viejos es **d)**. `WriteConcern` y `ReadPreference` en el cliente son el [2.8](replicas-shards.md) con otro idioma.

!!! success "Cerrar la UT2"
    HDFS **deposita** el lago y **tolera** discos muertos. YARN/MapReduce **demuestran** el cómputo partido. Mongo **guarda** el JSON inquieto. Réplicas y *shards* **prueban** fallos y **muestran** el crecimiento. PyMongo **enciende** eso desde Python. Hive, Spark y el resto son **módulos** que enchufáis después.

## Relación con el RA2

| Criterio | Aquí |
| --- | --- |
| **b)** | Procesamiento en el motor con `aggregate`; se complementa con la prueba distribuida del 2.4 |
| **d)** | Campo nuevo en un `insert`; `find` antiguos siguen |
| **c)** | `ReadPreference` / `WriteConcern` / transacción sobre `hotelrs` |

## Para practicar (Moodle manda)

1. **Parte.** Importad `reservas` y `opiniones`. Ejecutad `parte_gerencia.py` (o el vuestro). Entregad captura de `count_documents`, un `find` de Laredo y el `$group` por hotel.
2. **Esquema que crece.** Insertad una reserva de 2027 con `mascota: True`. Un `find({"mascota": True})` y otro `find({"hotel": "Laredo"})` que **siga** devolviendo las de 2026. Eso es **d)** en Python.
3. **Cursor frente a *pipeline*.** La misma pregunta (Potes, orden por importe, dos filas) de las dos formas. Una frase: cuándo usaríais cada una.
4. **Errores.** Forzad un `DuplicateKeyError` y un `ServerSelectionTimeoutError` (URI falsa). Capturad; no vale el *traceback* suelto.
5. **Promesas.** Sobre `hotelrs` (si el lab está levantado): un `insert_one` con `WriteConcern(w="majority", wtimeout=2500)` y un `find` con `SECONDARY`. Relacionadlo con el viernes de Laredo del [2.8](replicas-shards.md).
6. (Opcional) Ruta Flask `/ocupacion` con un cliente compartido por proceso y el *pool*. No hace falta login ni un MVC de otro proyecto.
7. (Opcional) Transacción `reservas` + `parking` en el *replica set*. Si el `mongod` es suelto, documentad **por qué** falla.

### Criterios de comprobación

En las consultas de lectura, contrastad los recuentos iniciales y los importes de Potes indicados arriba. En escrituras, mostrad el antes, el resultado de la operación y el después sobre `hotel_escrituras`. En la transacción, entregad tanto la primera ejecución correcta como el rechazo de la segunda: mostrar solo el camino de éxito deja sin probar la regla de negocio.

La aplicación Flask es opcional y utiliza `hotel` sin modificar. Probad `/` y `/ocupacion`, y comprobad que los totales coinciden con el script de gerencia. El servidor con `--debug` es para desarrollo local.

## Referencias

- [PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/)
- [Agregación](https://www.mongodb.com/docs/manual/aggregation/) y [transacciones](https://www.mongodb.com/docs/manual/core/transactions/)
- [Flask](https://flask.palletsprojects.com/) (solo el extra)
- [2.6 MongoDB](mongodb.md) · [2.7 Modelado](modelado.md) · [2.8 Réplicas](replicas-shards.md)
