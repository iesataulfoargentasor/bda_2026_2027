---
title: 2.9 MongoDB y Python
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.9. MongoDB y Python

En los apartados anteriores hemos aprendido a consultar MongoDB, modelar documentos y comprobar qué sucede cuando falla un miembro del conjunto. Ahora gerencia necesita repetir el parte sin escribir cada consulta a mano. **PyMongo permite ejecutar esas operaciones desde un programa Python**: el programa prepara la petición y MongoDB la resuelve según su configuración.

Continuamos con las reservas y opiniones del grupo hotelero. Como en la UT1, comprobaremos el resultado: que un programa termine no demuestra que haya leído la base correcta ni aplicado la regla de negocio.

!!! info "Ruta de estudio"
    **Esencial:** preparar la conexión, consultar sin alterar los originales, interpretar el cursor y las agregaciones, y comprobar las escrituras en una base de ejercicios.

    **Práctica guiada:** obtener el parte de gerencia y comparar los resultados con 2.6. Después, trasladar las preferencias y confirmaciones de 2.8 a Python.

    **Ampliación:** transacción de reserva de parking sobre el replica set y una página local con Flask. Se indican por separado sus requisitos. Las entregas evaluables se concretan en Moodle.

[PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/) es el driver oficial. Usaremos Python 3.12, **PyMongo 4.x** y MongoDB 7, en coherencia con el laboratorio. Desde la raíz del repositorio, cread el entorno de Python; si ya existe, reutilizadlo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "pymongo>=4,<5"
```

En PowerShell, activadlo con `.\.venv\Scripts\Activate.ps1`. Si la política del equipo impide activar, ejecutad `.\.venv\Scripts\python.exe` en lugar de `python`, también para `-m pip`; no hace falta cambiar la política del sistema. Anotad `python --version` y `python -m pip show pymongo`. El paquete `bson` viene incluido en PyMongo: no instaléis otro paquete independiente con ese nombre.

La URI típica es `mongodb://localhost:27017`. Atlas trae usuario, `tls` y a menudo `mongodb+srv://`. **No** subáis la URI con contraseña a Moodle en claro.

## El primer cable

Primero detened el laboratorio de 2.8 que ocupe el puerto 27017 y arrancad el servidor independiente de [2.6](mongodb.md). **Los volúmenes del servidor independiente y del replica set son diferentes**: cambiar la URI no copia los datos.

| Recorrido | Conexión y base | Qué se conserva |
| --- | --- | --- |
| Lecturas y parte | Servidor de 2.6, `hotel` | 15 reservas, 6 opiniones y 46 noches originales |
| Escrituras | Mismo servidor, `hotel_escrituras` | Copia de ejercicios, modificable |
| Preferencias y confirmaciones | Replica set de 2.8, `hotel_python_lab` | Documentos identificados de prueba |
| Transacción — ampliación | Replica set de 2.8, `hotel_tx` | Cupo y reservas propios del experimento |
| Flask — ampliación | Servidor de 2.6, `hotel` | Lectura de los originales |

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

Hasta el bloque de escrituras, los fragmentos reutilizan `cliente`, `hotel` y `reservas` de esta sesión Python. Cerrad `cliente.close()` al finalizar ese recorrido. No concatenéis todos los fragmentos como si fueran un único programa; los scripts descargables sí son programas completos.

Si no habéis importado aún, desde la **raíz del repo** y con `mongoimport` instalado en el PC (el procedimiento y la comprobación de carga están en el [2.6](mongodb.md)):

```bash
mongoimport --host 127.0.0.1 --port 27017 --db hotel --collection reservas --file docs/assets/practicas/reservas_mongo.jsonl
mongoimport --host 127.0.0.1 --port 27017 --db hotel --collection opiniones --file docs/assets/practicas/hotel-mongo/opiniones.jsonl
```

Comprobad los recuentos antes de importar: repetir la carga puede duplicar documentos, porque los archivos no incluyen `_id`. Si no trabajáis con el repositorio completo, descargad [reservas_mongo.jsonl](../assets/practicas/reservas_mongo.jsonl) y [opiniones.jsonl](../assets/practicas/hotel-mongo/opiniones.jsonl) y adaptad solo la ruta de `--file`. El procedimiento alternativo dentro del contenedor está en 2.6.

Hay un script de aula que imprime el parte: [`parte_gerencia.py`](../assets/practicas/hotel-pymongo/parte_gerencia.py). Arrancad un `mongod` (el del [2.6](mongodb.md), no el *replica set* y el suelto a la vez: los dos quieren el **27017**).

```powershell
$env:HOTEL_MONGO_URI = "mongodb://localhost:27017"
python docs/assets/practicas/hotel-pymongo/parte_gerencia.py
```

El script verifica 15 reservas, 6 opiniones, fechas BSON y 46 noches antes de presentar el parte. Estos controles detectan problemas habituales, pero no certifican por sí solos que todos los campos coincidan con el archivo original. La media impresa es **importe por reserva**, no precio por noche ni cobro realizado.

| Hotel | Noches originales |
| --- | ---: |
| Comillas | 4 |
| Laredo | 11 |
| Noja | 4 |
| Potes | 13 |
| Reinosa | 6 |
| Santander | 8 |
| **Total** | **46** |

## Una llave, no un enchufe por clic

Un cliente gestiona conexiones y descubre la topología. Crear uno por documento desperdicia ese trabajo. `connectTimeoutMS` limita el establecimiento de una conexión; `serverSelectionTimeoutMS` limita cuánto se busca un servidor adecuado. Ninguno equivale a cancelar automáticamente una escritura ya realizada.

Las opciones de reintento no hacen idempotente cualquier código de aplicación. Si el programa no sabe si se confirmó una operación, necesita un identificador de negocio para comprobarla y evitar duplicarla. Los errores mostrados al alumnado no deben imprimir una URI que pudiera contener contraseña.

`MongoClient` **no** es “abro el socket, pregunto, cierro”. Mantiene un ***pool*** que crece según la demanda, con un límite predeterminado de 100 conexiones por servidor; no abre 100 de golpe. Las operaciones utilizan el pool; al recorrer un cursor puede haber varias peticiones al servidor, no una conexión nueva por documento. Abrir un cliente **dentro** del `for` de un Flask es el error clásico.

El siguiente fragmento muestra una configuración alternativa. Si vais a sustituir el cliente anterior, cerradlo con `cliente.close()` y obtened de nuevo los manejadores de base y colección desde el nuevo cliente antes de continuar. No reutilicéis los manejadores vinculados al cliente cerrado:

```python
cliente = MongoClient(
    "mongodb://localhost:27017",
    maxPoolSize=50,
    connectTimeoutMS=2000,
    serverSelectionTimeoutMS=4000,
    retryWrites=True,
    wtimeoutMS=2500,
)
hotel = cliente["hotel"]
reservas = hotel["reservas"]
```

La opción `wtimeoutMS` del cliente (llamada `wtimeout` en `WriteConcern`) limita la espera de confirmación cuando la escritura necesita las confirmaciones indicadas. **No limita toda la operación ni deshace lo ya aplicado**. En un conjunto de tres miembros, la ausencia de uno no impide necesariamente obtener mayoría: importan los miembros disponibles y su estado. El ejemplo anterior no fija `w`; para pedir mayoría de forma explícita se usa `WriteConcern(w="majority", wtimeout=2500)`, como veremos después. Si no hay servidor, salta `ServerSelectionTimeoutError`: capturadlo; no dejéis un *traceback* crudo en recepción.

```python
print(cliente.list_database_names())
print(cliente.address)
```

Set `hotelrs` (varios hosts + nombre del conjunto). **Esta URI solo sirve desde un entorno que resuelva y alcance esos nombres Docker**, como el contenedor cliente explicado más abajo; no la ejecutéis directamente en Windows sin adaptar la red:

```python
uri = "mongodb://rs-laredo:27017,rs-potes:27017,rs-noja:27017/?replicaSet=hotelrs"
```

En Atlas, una URI `mongodb+srv://…` permite descubrir servidores mediante DNS y activa TLS por defecto. Usad la URI que proporciona el servicio, con credenciales fuera del código. En un replica set accesible, el driver descubre los miembros y selecciona el primario; `directConnection=true` fija un servidor y no sustituye esa conexión con descubrimiento.

**Referencias:** `cliente.hotel` y `hotel.reservas` no crean por sí solos la base ni la colección. Una escritura o una creación explícita sí puede crearlas. Un typo (`cliente.htel`) no falla al instante: puede crear una base equivocada al escribir. Verificad el nombre antes de cargar datos.

## Preguntar sin vaciar el BSON

Construid primero el filtro como diccionario de Python. Las claves de operadores son cadenas (`"$gte"`); los booleanos son `True` y `False`, y el valor nulo es `None`. Copiar literalmente `true` del shell JavaScript produce un error en Python.

Una consulta vacía no demuestra fallo de conexión: puede no haber coincidencias. Contrastad `count_documents({})`, base y filtro. Al convertir un cursor completo en JSON o en una lista, cargáis sus resultados en memoria; el ejemplo de exportación limita la salida a diez documentos. La primera consulta usa el pequeño conjunto de aula; con datos grandes conviene filtrar, proyectar y recorrer los resultados sin materializarlos completos.

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

`dumps` produce Extended JSON, con representaciones como `$oid` y `$date`; no convierte el resultado en JSON ordinario independiente de los tipos BSON. `json.dumps` de la biblioteca estándar **rompe** con esos tipos.

## El parte: agregación en el motor

Seguid la forma de los datos después de cada etapa. `$match` conserva reservas que cumplen el filtro; `$group` produce un documento por hotel; `$sort` ordena esos resúmenes. En `$sum: "$noches"`, el valor es una referencia al campo; en `$sum: 1`, se cuenta un documento.

`media` en el ejemplo es la **media del importe por reserva**, no el precio medio por noche. Este último exigiría dividir el importe total entre las noches totales, especificando qué reservas entran. Y la suma de noches no es un porcentaje de ocupación: faltan calendario y capacidad.

Aquí aprendemos a **dejar el trabajo en Mongo** (`aggregate`) y que Python solo reciba el resultado. Una agregación sobre un servidor independiente no demuestra computación distribuida; esa evidencia se obtiene con el experimento del [2.4](computacion-distribuida.md). Tres fases que gerencia pide cada mañana: filtrar, agrupar, ordenar.

```python
from pymongo import ASCENDING, DESCENDING

pipeline = [
    {"$match": {"canal": {"$in": ["web", "ota"]}}},
    {
        "$group": {
            "_id": "$hotel",
            "noches": {"$sum": "$noches"},
            "media": {"$avg": "$importe"},
        }
    },
    {"$sort": {"noches": DESCENDING, "_id": ASCENDING}},
]
for fila in reservas.aggregate(pipeline):
    print(fila)
```

El parte descargable suma **todos los canales**; este pipeline filtra `web` y `ota`, por lo que no debe exigirse el mismo total. Comparad únicamente consultas con el mismo alcance.

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

Si la opinión apuntara a `_id` de una reserva, el `localField` sería `_id` y el `foreignField` un `ObjectId` guardado. Si muchas pantallas necesitan `$lookup`, revisad con [2.7](modelado.md) la frecuencia de lectura, las actualizaciones y el crecimiento del documento. Embeber puede ayudar, pero no es una obligación: una relación compartida o creciente puede justificar referencias.

En el `$lookup` anterior, cada reserva de Laredo recibe las opiniones de ese hotel. Con los datos originales salen **tres reservas**, cada una con **dos opiniones**. Sumar los tamaños de esos arrays daría seis asociaciones, no seis opiniones distintas. Para una fila por hotel, agrupad primero o consultad una colección de hoteles.

`$unwind` genera una fila por elemento del array. Si una reserva tiene dos extras, participa en dos filas: no suméis después su importe como si cada fila fuera una reserva diferente sin decidir cómo evitar la duplicación.

## El cursor: cortar, ordenar, saltar

Para comparar cursor y pipeline, consumid ambos sobre los mismos datos, con idéntico filtro, proyección y orden. En el fichero original Potes tiene importes 124, 490 y 280: los dos mayores son **490 y 280**. Si hay empates, añadid `_id` como desempate en ambos. La equivalencia no significa que cualquier cadena arbitraria de etapas produzca el mismo resultado.

El cursor permite encadenar `sort`, `skip` y `limit`. Un pipeline puede expresar la misma consulta mediante etapas, pero su orden importa: limitar antes de ordenar no equivale a ordenar todos los resultados y escoger los primeros.

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

Dos criterios (nombre del hotel y después importe): lista de tuplas.

```python
reservas.find({}).sort([("hotel", ASCENDING), ("importe", DESCENDING)])
```

Paginación de aula: `.sort([("checkin", ASCENDING), ("_id", ASCENDING)]).skip(10).limit(10)`. El desempate permite un orden definido. Con desplazamientos grandes, `skip` puede resultar costoso: estudiad paginación por rango e índices. El rango debe corresponder al orden: `_id > ultimo` sirve para avanzar por `_id`, pero no sustituye sin más a paginar por `checkin`. Si los datos cambian entre peticiones, un orden estable no equivale a una instantánea común.

## Escribir, borrar, enmendar

Realizad las modificaciones sobre la base `hotel_escrituras`, preparada en el [2.6](mongodb.md). Si aún no la habéis preparado, copiad las dos colecciones con el procedimiento `$out` de el bloque de escrituras de 2.6; hacerlo otra vez reemplaza los ejercicios anteriores. Antes de continuar, reasignad los manejadores y verificad el destino:

```python
hotel = cliente["hotel_escrituras"]
reservas = hotel["reservas"]
print(reservas.full_name)  # hotel_escrituras.reservas
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

reserva = reservas.find_one({"hotel": "Laredo"}, sort=[("_id", 1)])
if reserva is None:
    raise ValueError("Falta Laredo: revisa la copia de hotel_escrituras")
id_reserva = reserva["_id"]
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

`delete_one` / `delete_many` → `deleted_count`. Vaciar con `delete_many({})` deja la colección; `reservas.drop()` la **quita** (índices incluidos). Para practicar, borrad únicamente el documento que acabáis de insertar, usando su `_id`; conservad las operaciones de vaciado como comparación conceptual.

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

# Ejecutar solo desde la red Docker indicada en el siguiente bloque.
# Se cierra este cliente al salir del bloque; no reemplaza el cliente de lectura.
with MongoClient(uri, serverSelectionTimeoutMS=5000) as cliente_rs:
    cliente_rs.admin.command("ping")
    bd_lab = cliente_rs.get_database("hotel_python_lab")
    mostrador = bd_lab.get_collection("reservas", read_preference=ReadPreference.PRIMARY)
    informes = mostrador.with_options(read_preference=ReadPreference.SECONDARY)
    escritura = mostrador.with_options(
        write_concern=WriteConcern(w="majority", wtimeout=2500)
    )
    resultado = escritura.update_one(
        {"_id": "python-confirmacion-01"},
        {"$set": {"hotel": "Potes", "noches": 1, "importe": 95}},
        upsert=True,
    )
    print("Confirmada:", resultado.acknowledged)
    print("Lectura secundaria:", informes.find_one({"_id": "python-confirmacion-01"}))
```

Repetir esta escritura mantiene el mismo documento de laboratorio. No convierte cualquier proceso de negocio en idempotente. La lectura secundaria puede devolver `None` si el miembro seleccionado todavía no ha aplicado la escritura: **mayoría no significa que todos estén al día**. Contrastad después desde el primario y repetid la lectura para observar la propagación.

Valores: `PRIMARY`, `PRIMARY_PREFERRED`, `SECONDARY`, `SECONDARY_PREFERRED` y `NEAREST`. La preferencia selecciona lecturas; no dirige escrituras al secundario. Un informe que admite retraso puede usar secundarios. Para fijar qué datos son visibles existe además `ReadConcern`, y `WriteConcern` indica cómo se confirma una escritura. Son decisiones distintas, como en [2.8](replicas-shards.md).

### Ejecutar Python dentro de la red del replica set

Los nombres `rs-laredo`, `rs-potes` y `rs-noja` son internos de Docker. Para que el driver descubra los miembros sin configurar el DNS de Windows, mantened `hotel-rs` levantado y ejecutad desde la **raíz del repositorio**, en PowerShell:

```powershell
docker run --rm -it --network hotel-rs_default -v "${PWD}:/trabajo:ro" -w /trabajo python:3.12-slim bash
```

Este contenedor cliente necesita acceso a Internet para instalar PyMongo. En su Bash:

```bash
python -m pip install "pymongo>=4,<5"
export HOTEL_MONGO_URI='mongodb://rs-laredo:27017,rs-potes:27017,rs-noja:27017/?replicaSet=hotelrs'
python docs/assets/practicas/hotel-pymongo/reservar_parking.py
```

La red se llama `hotel-rs_default` con el nombre de proyecto del Compose incluido. Si se ha cambiado el nombre del proyecto, adaptad la red. Usar `localhost:27017` dentro del contenedor cliente apuntaría al propio cliente, no a MongoDB.

## Dos papeles, un “sí” (transacciones)

Una actualización de un documento es atómica. Si la regla exige confirmar juntos cambios en documentos distintos, como descontar el cupo de parking y crear la reserva, utilizamos una transacción explícita. Otras operaciones pueden aceptar pasos independientes; hay que decidir la garantía antes de elegir el mecanismo. **Un servidor standalone no admite transacciones multidocumento**; utilizamos el replica set preparado en el 2.8.

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

`bd` e `identificador` se preparan fuera del callback. El programa lo ejecuta con lectura `snapshot`, escritura `majority` y preferencia `PRIMARY`. Todas las operaciones participantes llevan `session=sesion`. El identificador se muestra antes de intentar la reserva y se conserva durante los reintentos del callback; volver a arrancar el programa genera otro. Ante un resultado incierto, consultad el identificador anterior antes de repetir: no es una solución completa de idempotencia entre ejecuciones.

La comprobación de `modified_count` es esencial: **no encontrar plazas no provoca automáticamente una excepción**. Sin esa comprobación, una transacción podría confirmar una reserva sin haber descontado cupo. Si la inserción falla después del descuento, el aborto también deshace ese descuento.

Prueba en una base `hotel_tx` nueva:

| Ejecución | Resultado esperado | Estado final |
| --- | --- | --- |
| Primera | Reserva confirmada | Una reserva y cero plazas |
| Segunda | Mensaje de falta de plazas | Sigue una reserva y cero plazas |
| Error de inserción dentro de una transacción | Aborto | Se conserva el cupo anterior |

No repongáis una plaza antes de la segunda ejecución: el objetivo es probar el rechazo. Para repetir el experimento desde cero, el docente reinicia solo los datos de `hotel_tx`. Un error de red o de confirmación requiere comprobar el estado antes de reintentar una operación de negocio.

### Comprobar también el aborto

La tercera fila de la tabla necesita una prueba diferente: sin plazas, el callback se detiene antes de insertar. Para provocar un error **después** del descuento sin cambiar `hotel_tx`, descargad también [comprobar_transaccion.py](../assets/practicas/hotel-pymongo/comprobar_transaccion.py) junto a `reservar_parking.py` y ejecutadlo desde la misma conexión al set:

```bash
python docs/assets/practicas/hotel-pymongo/comprobar_transaccion.py
```

Crea una base temporal propia con nombre `hotel_tx_prueba_...`, que muestra al iniciar. Comprueba tres casos: reserva correcta, rechazo sin cupo y una inserción con `_id` duplicado después del descuento. En este último debe mantenerse **una plaza y una reserva preexistente**, sin el segundo documento. El comprobador elimina únicamente su base temporal si pasan todas las comprobaciones; si falla, la conserva para investigar. No reinicia el trabajo anterior.

La transacción controla documentos de MongoDB; no confirma un cargo bancario ni envía un correo de forma atómica. Ese tipo de efecto externo requiere un diseño adicional.

!!! note "ODM"
    Un mapeo objeto-documento, como los basados en modelos de validación, puede simplificar una aplicación. En esta unidad usamos PyMongo para ver explícitamente filtros, sesiones y resultados. Un ODM no elimina la necesidad de comprender sus garantías.

## Extra: una URL para gerencia (Flask)

Volved a la conexión del servidor de 2.6 que contiene `hotel` original, deteniendo antes el set si ambos necesitan 27017. En PowerShell: `$env:HOTEL_MONGO_URI = "mongodb://localhost:27017"`. Comprobad de nuevo el parte antes de arrancar Flask. Los ficheros siguientes son una aplicación aparte; no se pegan al final de los ejemplos de transacciones.

El RA2 **no** pide un MVC. Si el profesor quiere ver el dato en el navegador, Flask basta. Distinto del “Hola / Adiós / listado de usuarios” de otros apuntes: aquí la ruta muestra **noches reservadas por hotel**.

```bash
python -m pip install "pymongo>=4,<5" flask
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
from pymongo import ASCENDING, DESCENDING
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
        {"$sort": {"noches": DESCENDING, "_id": ASCENDING}},
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

`http://127.0.0.1:5000/ocupacion`. Jinja usa `{{ variable }}` para mostrar valores y `{% for %}` para recorrer filas. MongoDB calcula el resumen y Flask lo presenta; esta separación no demuestra por sí sola distribución ni rendimiento con grandes volúmenes.

## Cómo se cierra el apartado (y la UT2)

Un script que suma noches practica procesamiento en MongoDB. Para comprobar el modelo distribuido del criterio **b)** se mantiene la evidencia de 2.4. Añadir `mascota` permite ensayar evolución del documento, pero el criterio **d)** también requiere explicar qué datos se conservan, sus límites y cómo se reutilizan.

!!! success "Cerrar la UT2"
    HDFS permite almacenar bloques y recuperarlos según la configuración; MapReduce y YARN permiten ejecutar y observar tareas distribuidas. MongoDB aporta otro modelo de almacenamiento y consulta. Las réplicas y particiones responden a necesidades diferentes, con recursos y fallos concretos. PyMongo conecta ese sistema con una aplicación que consulta, modifica y comprueba resultados. Ninguna de estas herramientas elimina por sí sola los límites de capacidad ni todos los fallos.

## Relación con el RA2

| Criterio | Evidencia y alcance |
| --- | --- |
| **b)** | Pipeline enviado desde Python y resultado contrastado; se complementa con la prueba distribuida de 2.4, no la sustituye. |
| **d)** | Conservación de los originales, incorporación controlada de un campo y consultas compatibles. No demuestra capacidad ilimitada ni compatibilidad de cualquier aplicación. |
| **c)** | Opciones del cliente y resultados de transacciones; la prueba de tolerancia a una caída se documenta en 2.8. Atomicidad y alta disponibilidad son garantías distintas. |

## Actividades

Conservad **objetivo, URI sin credenciales, base, código, resultado esperado, resultado observado e interpretación**. Las actividades 1–7 forman el recorrido básico; 8–10 requieren las condiciones indicadas. Las entregas evaluables se concretan en Moodle.

1. **Preparar y comprobar.** Registrad versiones, ejecutad `ping` y el parte. Contrastad 15 reservas, 6 opiniones, 46 noches y el reparto por hotel. Explicad por qué una base vacía accesible no equivale a una conexión fallida.
2. **Traducir una pregunta.** Buscad reservas web de al menos tres noches, mostrando hotel, importe y noches sin `_id`. Comparad el recuento y el cursor con la consulta equivalente de 2.6. Explicad cuándo se ejecuta la consulta y por qué no conviene convertir un resultado enorme en una lista.
3. **Cursor y pipeline.** Obtened los dos mayores importes de Potes de ambas formas: 490 y 280. Usad el mismo filtro, proyección y orden. Si introducís empates en una copia, aplicad el mismo desempate antes de retirar `_id` de la proyección.
4. **Agregaciones con sentido.** Contrastad el parte de todos los canales con el pipeline filtrado a web y ota. Después explicad por qué las tres reservas de Laredo con dos opiniones cada una no representan seis opiniones distintas y por qué `$unwind` puede duplicar importes si se suman sin ajustar.
5. **Esquema y conservación.** En `hotel_escrituras`, insertad la reserva con `mascota=True`, guardad su id y comprobad la consulta antigua de Laredo. Mostrad que `hotel` mantiene sus recuentos. Justificad por qué añadir un campo no prueba que cualquier aplicación sea compatible.
6. **Escribir y verificar.** Actualizad una reserva identificada con `$set`; repetid el mismo valor y comparad `matched_count` y `modified_count`. Borrad solo el alta de la actividad 5 mediante su id. Mostrad antes y después; no vaciéis la colección.
7. **Errores comprensibles.** Provocad una clave duplicada en la copia y un fallo de selección con `MongoClient("mongodb://127.0.0.1:1", serverSelectionTimeoutMS=1000)` seguido de `ping`. Capturad `DuplicateKeyError` y `ServerSelectionTimeoutError`, sin credenciales ni traceback. Explicad por qué construir el cliente no basta para observar el segundo error.
8. **Confirmar y leer — con replica set.** Ejecutad el ejemplo de `hotel_python_lab` desde su red. Diferenciad confirmación mayoritaria y lectura secundaria. Si se observa retraso, registradlo; si no, no afirméis que es imposible. Recuperad la evidencia de caída de 2.8 para distinguir configuración de prueba de tolerancia.
9. **Parking — ampliación.** Ejecutad dos veces `reservar_parking.py` sobre una base `hotel_tx` inicialmente nueva. Contrastad éxito y rechazo por falta de cupo. Ejecutad el comprobador independiente para demostrar el aborto después del descuento. Indicad qué parte del estado se conserva en cada caso.
10. **Página de gerencia — ampliación.** Construid Flask, visitad `/` y `/ocupacion` y contrastad los seis hoteles y las 46 noches. Explicad dónde se calcula y dónde se representa. Una página correcta no demuestra rendimiento con millones de documentos.

### Orientaciones para comprobar las respuestas

??? note "Revisar después de intentarlo"
    **1–3.** `ping` comprueba acceso al servidor; los recuentos comprueban el conjunto usado. `find` devuelve un cursor y su recorrido obtiene documentos por lotes. Los dos importes mayores de Potes son 490 y 280; un pipeline debe ordenar antes de limitar.

    **4–5.** El parte completo suma 46 noches; el filtro web y ota deja 30. Las opiniones pertenecen al hotel y se repiten en el resultado de cada reserva. Un nuevo campo puede coexistir con documentos antiguos, pero hay que revisar validadores, lectores y valores ausentes.

    **6–7.** Una coincidencia con cero modificaciones puede significar que el valor ya era el solicitado. Una clave repetida debe rechazarse. Una conexión mal dirigida solo se comprueba al pedir una operación; no imprimáis una URI con contraseña para diagnosticarla.

    **8–10.** Mayoría no significa aplicación en todos los secundarios. Una transacción mantiene unidos el descuento y la inserción, y un fallo debe conservar el estado anterior. Flask presenta noches, no un porcentaje de ocupación. Las pruebas locales no demuestran resistencia a perder el ordenador.

## Autoevaluación del 2.9

Diez preguntas (A–D, **una** correcta). No puntúan en Moodle. **Comprobar respuesta** muestra el resultado y explica el motivo. Revisad el apartado enlazado antes de repetir.

<div class="dwec-quiz" data-dwec-quiz data-src="../../assets/quizzes/ut2-2-9.json"></div>

Al terminar, cerrad los clientes de Python y detened Flask. Salid del contenedor cliente con `exit` si lo utilizasteis; al haberse iniciado con `--rm`, se retira al salir, pero eso no detiene los servidores MongoDB. Desde la terminal del PC, elegid la parada que corresponda:

- **Servidor independiente de 2.6 (`hotel-mongo`), utilizado para consultas, parte y Flask:** ejecutad `docker stop hotel-mongo`. Se creó con `docker run`, por lo que no se detiene con Compose.
- **Conjunto de réplicas de 2.8 (`hotel-rs`):** ejecutad `docker compose stop` desde `docs/assets/practicas/hotel-rs`, donde está su `compose.yaml`.

Ambas paradas conservan los volúmenes y sus datos. No uséis `down -v` para alternar entornos.

## Referencias

- [PyMongo](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/)
- [Agregación](https://www.mongodb.com/docs/manual/aggregation/) y [transacciones](https://www.mongodb.com/docs/manual/core/transactions/)
- [Flask](https://flask.palletsprojects.com/) (solo el extra)
- [2.6 MongoDB](mongodb.md) · [2.7 Modelado](modelado.md) · [2.8 Réplicas](replicas-shards.md)
