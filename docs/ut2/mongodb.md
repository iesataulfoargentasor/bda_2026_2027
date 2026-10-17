---
title: 2.6 MongoDB
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.6. MongoDB

[MongoDB](https://www.mongodb.com/) es la NoSQL **documental** del aula. Los documentos se basan en JSON; por dentro el motor guarda **BSON**. El nombre viene de *humongous*: gigantesco.

Destaca porque:

- **Esquema dinámico:** dos documentos de `reservas` **no** tienen por qué traer las mismas claves (criterio **d)**).
- Los *joins* (`$lookup`) existen; desde **5.1** incluso entre colecciones *shardeadas*. No es el gesto del día a día: lo que se usa junto se **embebe** ([2.7](modelado.md)).
- Una inserción o un `update` de **un** documento es atómico. Una transacción **entre varios documentos** la ejecuta el servidor en una topología compatible; la aplicación la solicita mediante una sesión del driver. En un RDBMS serían varias filas y un `COMMIT`.

Analogía: base ≈ esquema SQL, colección ≈ tabla, documento ≈ fila… **pero** el esquema puede ser flexible o incorporar validadores explícitos. El criterio **a)** aquí: depositáis el JSON del motor de reservas **tal cual** y preguntáis sin montar ocho tablas.

## Conceptos

| Pieza | Oficio | Analogía SQL (con trampa) |
| --- | --- | --- |
| **Instancia** (`mongod`) | Un proceso; 0 o más bases | El servidor |
| **Base de datos** | Contenedor de alto nivel | La base / el esquema |
| **Colección** | Conjunto de documentos. Crece con ellos. Las ***capped*** tienen tamaño fijo: lo nuevo **pisa** lo viejo | Tabla |
| **Documento** | Un objeto BSON | Fila |
| **Campo** | Par clave/valor. Sin esquema obligatorio | Columna |

Una instancia puede tener varias bases; cada base, varias colecciones; cada colección, documentos. Mongo **indexa** (como SQL) para no escanear todo. `find()` devuelve un **cursor** que permite recorrer resultados; `findOne()` devuelve un documento o `null`, y los métodos de recuento devuelven un número.

```mermaid
flowchart TB
  I[mongod :27017] --> H[hotel]
  I --> admin[admin / local]
  H --> R[reservas]
  H --> O[opiniones]
  R --> D1[doc Laredo]
  R --> D2[doc Potes]
```

### BSON

BSON conserva información de tipos: una fecha no es simplemente una cadena con aspecto de fecha. Eso permite comparaciones y operaciones adecuadas. La codificación binaria **no garantiza** que ocupe menos que el JSON equivalente. Para intercambiar tipos como fechas e identificadores en texto utilizamos Extended JSON (`$date`, `$oid`).

Para fechas de la aplicación utilizamos `new Date()` o `ISODate()`. El tipo BSON `Timestamp` tiene un uso interno, por ejemplo en replicación; no es el sustituto habitual de una fecha de creación.

En `mongosh` escribís objetos JavaScript; un texto JSON estricto exige comillas en las claves y no admite constructores como `ObjectId()`. Mongo serializa los documentos como **BSON** (*Binary JSON*): [especificación](https://bsonspec.org/). Es un **superset** de JSON:

- binario;
- tipos que JSON no tiene: `ObjectId`, `Date`, `BinData`, `Timestamp`…

[Tipos BSON](https://www.mongodb.com/docs/manual/reference/bson-types/). Ejemplo de aula (no lo peguéis en [jsonlint.com](https://jsonlint.com/): ese sitio valida **JSON**, no BSON; `ISODate` y `ObjectId` fallarán):

```javascript
const reserva = {
  hotel: "Laredo",
  canal: "web",
  noches: 3,
  importe: 186.5,
  checkin: ISODate("2026-04-12"),
  extras: ["parking", "cuna"],
  cobro: { medio: "tarjeta", ok: true },
  creada: new Date(),
};
```

Restricciones:

- Un documento **no pasa de 16 MiB**.
- `_id` está **reservado** a la clave primaria.
- Desde Mongo **5.0** un campo *puede* empezar por `$` o llevar `.`; **evitadlo**: rompe consultas y *drivers*.

Además Mongo:

- **no garantiza** el orden de los campos al devolver;
- es **sensible al tipo** (`18` ≠ `"18"`);
- es **sensible a mayúsculas** (`hotel` ≠ `Hotel`).

Estos tres documentos son **distintos**:

```javascript
{ edad: "18" }
{ edad: 18 }
{ Edad: 18 }
```

Mezclar tipos en el mismo campo es un **antipatrón**: las comparaciones no mezclan cadena y número.

## Puesta en marcha

Tres productos:

| Producto | Oficio |
| --- | --- |
| **Atlas** | Servicio gestionado en la nube; comprobad los límites del plan elegido |
| **Community** | Gratis *on-premise* (Windows, macOS, Linux) |
| **Enterprise** | Pago: soporte, seguridad y monitorización extra |

El demonio escucha en **27017**. Si abrís `http://localhost:27017` en el navegador veréis un aviso: ese puerto es el del **driver**, no una web. La UI es **Compass** o Atlas.

Hoy es más cómodo **Docker** o **Atlas** que instalar el servicio a mano. En clase: host y puerto del **profesor**. No copies URI ni contraseñas de otro ciclo.

### Docker

Anotad `db.version()` al conectar. El ejemplo fija la versión principal `mongo:7` y conserva datos en un volumen. Si el contenedor ya existe, usad `docker start hotel-mongo`; no hace falta volver a crearlo. Este servidor independiente sirve para consultas, pero **no** para transacciones multidocumento: esas se prueban con el replica set del 2.8.

```text
docker run -p 127.0.0.1:27017:27017 --name hotel-mongo -v hotel_mongo_data:/data/db -d mongo:7
```

!!! warning "Procesadores sin AVX"
    En plataformas x86-64, las versiones modernas requieren AVX. Si el equipo no es compatible, utilizad el servidor de aula o Atlas que indique el docente; no cambiéis automáticamente a una versión antigua sin soporte.

Cargar el hotel. Los comandos se lanzan **desde la raíz del repositorio** (la carpeta donde está `docs`).

La disponibilidad de `mongoimport` depende de la imagen instalada; podéis comprobarla con `docker exec hotel-mongo mongoimport --version`. Para que los comandos siguientes se ejecuten desde el PC, instalad las [Database Tools](https://www.mongodb.com/try/download/database-tools) en el PC y apuntáis al puerto que publicó el `docker run`:

```text
mongoimport --host 127.0.0.1 --port 27017 --db hotel --collection reservas --file docs/assets/practicas/reservas_mongo.jsonl
mongoimport --host 127.0.0.1 --port 27017 --db hotel --collection opiniones --file docs/assets/practicas/hotel-mongo/opiniones.jsonl
```

No usamos el *sample dataset* de Atlas (`sample_mflix`, `sample_training`). El caso es el **grupo hotelero**.

### Comprobar la carga antes de practicar

La entrada original tiene **15 reservas** y **6 opiniones**. Importad una sola vez en colecciones vacías: como el JSONL no fija `_id`, repetir la importación añade duplicados. Si los recuentos no coinciden, revisad la base y las cargas previas antes de continuar.

```javascript
use hotel
db.reservas.countDocuments({})
db.opiniones.countDocuments({})
db.reservas.countDocuments({hotel: "Laredo"}) // 3
db.reservas.countDocuments({canal: "web"})   // 6
```

Los ejemplos de inserción de «Hola MongoDB» son demostraciones: hacedlos en una colección de prueba o después de comprobar las consultas originales. Para empezar de nuevo, conservad primero el trabajo que queráis entregar y recargad únicamente las colecciones de práctica. No añadimos `--drop` por defecto para evitar eliminar datos al repetir un comando.

### Atlas (si el profesor lo pide)

Registro → clúster → usuario de base → red. En el mapa de AWS, **París es `eu-west-3`** y España es `eu-south-2`. Si la consola muestra `eu-west-1`, eso es **Irlanda**. **No** dejéis `0.0.0.0/0` en un proyecto con datos reales; en aula, solo si el profesor lo autoriza.

La URI de Atlas suele utilizar `mongodb+srv://`, que consulta registros DNS y activa TLS por defecto. La seguridad también depende de credenciales, permisos y configuración de red:

```text
mongodb+srv://USUARIO:CLAVE@cluster0.xxxxx.mongodb.net/hotel
```

El *Load Sample Dataset* de Atlas es opcional y **ajeno** a estas prácticas. Si Moodle pide captura del *dashboard*, usad **vuestra** cuenta.

### mongosh

Tras `mongod` (Docker o Atlas), el cliente es **`mongosh`** (antes se llamaba `mongo`). Habla **JavaScript**. Flecha arriba = comando anterior.

```text
docker exec -it hotel-mongo mongosh hotel
```

Sin argumentos entra en `test` de `localhost`. `use hotel` cambia (y **crea** la base al **insertar** el primer documento; `use` solo no basta).

```text
show dbs
```

Veréis `admin`, `config`, `local` y, tras importar, `hotel`.

Shell solo (sin el servidor), para un Atlas remoto: [descarga del shell](https://www.mongodb.com/try/download/shell).

```text
mongosh "mongodb+srv://USUARIO:CLAVE@cluster0.xxxxx.mongodb.net/hotel"
```

### Database Tools

[Herramientas](https://www.mongodb.com/try/download/database-tools): JSON ↔ colección y copias **binarias**.

```text
mongoimport -d hotel -c reservas --host 127.0.0.1 --port 27017 --file docs/assets/practicas/reservas_mongo.jsonl
mongoexport -d hotel -c reservas -o reservas_export.json

mongoimport --type csv -d hotel -c ocupacion_lab --headerline --file ocupacion.csv

mongodump -d hotel -o backup_hotel
mongorestore -d hotel backup_hotel/hotel
```

`mongoimport` / `export` = JSON (o CSV). **Backup serio:** `mongodump` (BSON) + `mongorestore`. `bsondump fichero.bson > fichero.json` pasa binario a texto.

!!! question "Si exportáis una colección"
    Suele aparecer una carpeta con **`.bson`** (datos) y **`.metadata.json`** (índices, opciones). Eso es un *dump*, no un CSV.

Monitorización: `mongostat`, `mongotop`. En Atlas van en el panel. *Drivers* oficiales para casi todos los lenguajes; Python es el [2.9](pymongo.md).

### Compass y VS Code

**Compass:** explorar, esquema, agregados, índices, consultas. Las funciones disponibles dependen de la versión instalada. Pegáis la URI y listo. Abajo hay un **mongosh** embebido.

**MongoDB for VS Code:** la misma URI y un *playground* (guion al estilo *shell*).

El RA2 se demuestra en **`mongosh`**, no solo en capturas bonitas.

## Hola MongoDB

Patrón de casi todo: `db.nombreColeccion.operacion()`.

```javascript
use hotel
db.reservas.insertOne({
  hotel: "Laredo",
  canal: "web",
  noches: 3,
  importe: 186.5,
  extras: ["parking"],
})
```

Respuesta: `acknowledged: true` y `insertedId: ObjectId("…")`.

```javascript
db.reservas.findOne({ hotel: "Laredo" })
```

| Comando | Oficio |
| --- | --- |
| `show dbs` | Bases |
| `show collections` | Colecciones de la base actual |
| `db` | Nombre de la base activa |
| `db.dropDatabase()` | **Borra** la base actual |
| `db.help()` | Ayuda |
| `db.version()` | Versión del servidor |

El esquema **aparece** al insertar. Podéis insertar otra reserva **sin** `extras` y Mongo no se queja. Más adelante, un `validator` ([2.7](modelado.md)) puede exigir reglas y rechazar documentos que las incumplan.

### JavaScript en el shell

```javascript
load("semilla_hotel.js")
```

Este ejemplo presupone que habéis guardado vuestro código en `semilla_hotel.js`; no es un fichero incluido en el repositorio. La ruta se resuelve donde se ejecuta `mongosh`: si está dentro de Docker, copiad primero el archivo al contenedor. Para los datos iniciales de esta unidad utilizad los JSONL enlazados, sin necesidad de ese script.

```text
mongosh hotel semilla_hotel.js
```

Bucle (crea documentos de prueba; luego `drop`):

```javascript
for (let i = 0; i < 10; i++) {
  db.reservas_lab.insertOne({ hotel: "Laredo", canal: "web", noches: i + 1 });
}
```

## ObjectId

El identificador distingue documentos; no es el número de reserva ni garantiza un orden cronológico exacto entre clientes. Los ejemplos que usan `getTimestamp()` presuponen que `_id` es un `ObjectId`; si insertáis un entero como identificador, ese método no existe para ese valor. Una referencia debe conservar el mismo valor **y tipo** que el identificador referenciado.

`_id` es único **en la colección** (clave primaria). Si no lo ponéis, el ***driver*** (no el servidor) fabrica un **ObjectId** de 12 bytes:

- 4 bytes: *timestamp*;
- 5 bytes: aleatorio por máquina y proceso;
- 3 bytes: contador.

No asumas un orden global perfecto: dos portátiles con reloj distinto **desordenan**. Sí podéis sacar la fecha de creación:

```javascript
db.reservas.findOne()._id
db.reservas.findOne()._id.getTimestamp()
```

El `_id` no se modifica una vez guardado. En una colección sin particionar, su índice único evita duplicados dentro de la colección. En sharding, la garantía global de índices únicos depende de la clave de partición; no deduzcáis unicidad global solo por el nombre del campo.

Si lo ponéis vosotros, Mongo **no** añade ObjectId. Puede ser número, cadena u **otro documento** (cuidado: más lío al consultar):

```javascript
db.reservas.insertOne({ _id: 18442, hotel: "Laredo", noches: 3 })
db.hoteles.insertOne({
  _id: { cadena: "Trasmiera", codigo: "LAR" },
  nombre: "Laredo",
})
```

`edad: 14` es entero; `edad: "14"` es texto. No los mezcléis.

## Recuperar datos

```javascript
db.reservas.find()
db.reservas.findOne()
```

`find()` devuelve un **cursor**, que se consume por lotes y puede caducar según los límites de cursor y sesión. El *shell* muestra **20** y espera `it` para seguir. `findOne()` = un documento (o `null`).

Los ejemplos de abajo asumen [reservas_mongo.jsonl](../assets/practicas/reservas_mongo.jsonl) y [opiniones.jsonl](../assets/practicas/hotel-mongo/opiniones.jsonl) ya importados (`use hotel`).

### Criterios (Y implícita)

Traducid primero la pregunta: «reservas web de Laredo con tres o más noches» combina tres condiciones sobre el mismo documento. La consulta selecciona documentos, no columnas. Un resultado vacío puede significar que no hay coincidencias, que habéis elegido otra base o que un campo tiene un tipo diferente; comprobad esas posibilidades antes de cambiar operadores.

`$ne` y `$nin` pueden incluir documentos en los que el campo está ausente. Si necesitáis «canal informado y distinto de web», combinad `$exists: true` y `$ne: "web"`. Igualmente, `{campo: null}` puede coincidir con valor nulo o campo ausente; usad `$exists` para distinguirlos.

Varios campos en el mismo objeto = **AND**:

```javascript
db.reservas.find({ hotel: "Laredo", canal: "web" })
```

!!! tip "El orden escrito no fija el plan"
    La selectividad ayuda a diseñar índices, pero poner una condición primero en el objeto no obliga al motor a ejecutarla antes. Comparad planes con `explain("executionStats")`: documentos examinados, claves examinadas y documentos devueltos.

| Comparación | Operador |
| --- | --- |
| `<` | `$lt` |
| `≤` | `$lte` |
| `>` | `$gt` |
| `≥` | `$gte` |

Sintaxis: `{ campo: { operador: valor } }`. Varios operadores en el **mismo** campo:

```javascript
db.reservas.find({ noches: { $lt: 3 } })
db.reservas.find({ noches: { $gte: 2, $lte: 4 } })
db.reservas.find({ canal: { $ne: "web" } })
db.reservas.find({ noches: { $lt: 2 }, canal: { $ne: "ota" } })
```

Sin una collation específica se utiliza comparación binaria de cadenas. `Laredo` y `laredo` no son iguales; una collation puede cambiar reglas lingüísticas y sensibilidad a mayúsculas.

**`$exists`:** el documento **tiene** (o no) el campo. Encaja con el esquema flexible: unas reservas tienen `extras`, otras no.

```javascript
db.reservas.find({ extras: { $exists: true } })
```

**`$not`:** niega otro operador. **`$mod`:** resto de división.

```javascript
db.reservas.find({ noches: { $not: { $mod: [2, 0] } } })  // noches impares
```

**`$regex`** (o `/…/`):

```javascript
db.reservas.find({ hotel: /lar/i })
db.reservas.find({ hotel: { $regex: /lar/i } })
```

Caro sin índice. Búsquedas de texto serias: índice `$text` *on-prem* o **Atlas Search** en la nube.

**`$expr`:** comparar **dos campos del mismo** documento (agregación dentro del `find`). El `$` delante del nombre es **el valor** del campo:

```javascript
// reservas cuyo importe es al menos 80 € por noche
db.reservas.find({
  $expr: { $gte: ["$importe", { $multiply: ["$noches", 80] }] },
})
```

**`$type`:**

```javascript
db.reservas.find({ hotel: { $type: "string" } })
```

**`$where`:** JavaScript arbitrario. **No** usa índices. Evitadlo si hay operador.

### Proyección

El primer argumento de `find` responde **qué documentos**; el segundo, **qué campos devolver**. La proyección reduce el contenido transferido y facilita leer la respuesta, pero no modifica los documentos almacenados. Excluir `_id` es la excepción habitual que permite combinar inclusión de campos con una exclusión.

Segundo argumento: qué campos ver (`1` / `true`) u ocultar (`0` / `false`). `_id` sale **siempre** salvo que lo apaguéis.

```javascript
db.reservas.find({ hotel: "Laredo" }, { canal: 1, importe: 1 })
db.reservas.find({ hotel: "Laredo" }, { canal: 1, importe: 1, _id: 0 })
```

!!! warning "No mezcléis 1 y 0"
    O listáis los que **sí**, o los que **no**. La única mezcla legal es **ocultar `_id`** junto a un listado en `1`.

### `$and`, `$or`, `$nor`, `$in`

```javascript
db.reservas.find({ $or: [{ hotel: "Laredo" }, { hotel: "Noja" }] })
db.reservas.find({ $or: [{ noches: { $lte: 1 } }, { noches: { $gte: 6 } }] })
```

`$and` explícito es raro: dos claves en el mismo objeto ya es AND.

```javascript
db.reservas.find({ hotel: "Laredo", canal: "web" })
db.reservas.find({ $and: [{ hotel: "Laredo" }, { canal: "web" }] })
```

!!! tip "OR une alternativas"
    Un documento se devuelve si cumple al menos una rama. Cambiar su orden no garantiza una mejora. Importan las condiciones y los índices que el planificador pueda utilizar; comprobad el plan de ejecución.

**`$nor`:** no cumple **ninguna** de las condiciones.

```javascript
db.reservas.find({
  noches: { $lte: 2 },
  $nor: [{ canal: "ota" }, { hotel: "Reinosa" }],
})
```

**`$in` / `$nin`:**

```javascript
db.reservas.find({ hotel: { $in: ["Laredo", "Noja", "Comillas"] } })
db.reservas.find({ canal: { $nin: ["ota"] } })
```

### Subdocumentos (notación punto)

La notación `"cobro.ok"` accede a una propiedad dentro de un objeto. Comparar un subdocumento completo puede exigir una coincidencia más estricta, incluido su contenido y orden de campos. Para preguntar por una propiedad concreta, preferid la ruta con punto. En arrays, además hay que decidir si las condiciones deben cumplirlas elementos distintos o **el mismo elemento**.

Da igual el nivel. El orden de los campos **dentro** del subdocumento no importa.

```javascript
db.reservas.find({ "cobro.medio": "tarjeta" })
db.opiniones.find({ titulo: "Vistas al mar", "comentarios.autor": "Luis Sainz" })
```

### Arrays

Ejemplo: un comentario de Ana tiene `email: "a@ejemplo.es"` y otro de Luis tiene `email: "l@ejemplo.es"`. Filtrar por autor Ana y correo de Luis con dos rutas independientes puede encontrar el documento: cada condición la cumple un elemento. Con `$elemMatch`, ambas deben cumplirse en **un mismo comentario**, así que no coincidiría.

No confundáis `$elemMatch` en el **filtro** con su uso en la **proyección**: el primero selecciona documentos; el segundo devuelve solamente el **primer elemento coincidente** del array. Para devolver todos los comentarios que cumplen una condición, se necesita una expresión de agregación como `$filter`.

Un array de **escalares** se consulta como un campo: `{ extras: "parking" }` = “contiene parking”.

| Operador | Oficio |
| --- | --- |
| `$all` | Contiene **todos** esos valores (puede haber más; el orden no importa) |
| `$in` | Contiene **alguno** |
| `$nin` | No contiene ninguno de la lista |
| `$elemMatch` | Un **elemento** (documento) cumple **varios** criterios a la vez |
| `$size` | Longitud **exacta** |
| `$slice` | En la **proyección**: recorta el array |

```javascript
db.opiniones.find({ etiquetas: { $all: ["playa", "parking"] } })
db.opiniones.find({ etiquetas: { $in: ["playa", "nieve"] } })
db.opiniones.find({
  comentarios: { $elemMatch: { autor: "Luis Sainz", email: "luis@ejemplo.es" } },
})
```

Si solo filtráis **un** campo del subdocumento del array, basta la notación punto: `"comentarios.autor": "Luis Sainz"`. `$elemMatch` es obligatorio cuando **dos** condiciones deben cumplirse **en el mismo** comentario.

Proyectar **solo** esos comentarios:

```javascript
db.opiniones.find(
  { comentarios: { $elemMatch: { autor: "Luis Sainz" } } },
  { comentarios: { $elemMatch: { autor: "Luis Sainz" } }, titulo: 1 }
)
```

```javascript
db.opiniones.find({ comentarios: { $size: 0 } })
db.opiniones.find({ titulo: "Centro y ruido" }, { comentarios: { $slice: 2 }, etiquetas: { $slice: 3 } })
```

### Fechas

El JSONL utiliza Extended JSON para que `checkin` se importe como fecha BSON. Una cadena `"2026-04-12"` no es el mismo tipo. Para un periodo utilizad inicio incluido y final excluido: abril es `>= 2026-04-01T00:00:00Z` y `< 2026-05-01T00:00:00Z` si el periodo se define en UTC. Para un día civil de Cantabria, convertid sus límites teniendo en cuenta la zona horaria.

Guardad **`Date` / `ISODate`**, no `"12/04/2026"` en texto, si vais a filtrar rangos. El JSONL de reservas usa Extended JSON (`$date`) para que `mongoimport` cree fechas de verdad.

```javascript
const fechas = {
  hoy: new Date(),
  checkin: ISODate("2026-04-12"),
  ahora: new Date(),
};
```

```javascript
db.reservas.find({ hotel: "Laredo" }, { checkin: 1 }).sort({ checkin: 1 }).limit(3)
db.reservas.find({
  checkin: {
    $gte: ISODate("2026-04-01"),
    $lt: ISODate("2026-05-01"),
  },
})
```

En agregación (y a veces en proyección moderna) `$dateToString` formatea. El detalle de *pipelines* está en el [2.9](pymongo.md); aquí basta saber que **existe**.

### `distinct`

`distinct("hotel")` devuelve valores diferentes de ese campo, no el número de reservas por hotel. Si hay tres reservas de Laredo, el nombre aparece una vez. Para obtener totales o sumas necesitaremos `$group`, desarrollado en [2.9](pymongo.md).

Valores distintos de un campo (como un `SELECT DISTINCT`):

```javascript
db.reservas.distinct("canal")
db.reservas.distinct("canal", { comarca: "Trasmiera" })
```

### Cursores

El cursor evita traer todos los resultados de golpe. Configurad filtro, proyección y orden antes de recorrerlo. Sin un orden explícito, «los dos primeros» no es una selección de negocio estable. Para paginar con empates, añadid `_id` como segundo criterio, por ejemplo `sort({importe: -1, _id: 1})`.

Guardáis el cursor y lo recorréis. `limit` / `sort` / `skip` se ejecutan en el **servidor**. `hasNext` / `next` en el **cliente**.

| Método | Oficio | Dónde |
| --- | --- | --- |
| `hasNext()` | ¿Queda algo? | Cliente |
| `next()` | Siguiente documento | Cliente |
| `limit(n)` | Como mucho *n* | Servidor |
| `sort({ campo: 1 })` | `1` asc, `-1` desc | Servidor |
| `skip(n)` | Saltar *n* | Servidor |

La consulta **no corre** hasta el primer `next` / `hasNext`. Por eso `sort` y `limit` van **antes** de recorrer.

```javascript
const c = db.reservas.find({ comarca: "Trasmiera" })
c.hasNext()
c.next()
```

```javascript
db.reservas.find().sort({ importe: -1 }).limit(3)
db.reservas.find({ canal: "web" }).sort({ importe: -1 }).limit(3)
db.reservas.find({ canal: "web" }).sort({ importe: -1 }).skip(4).limit(5)
```

`skip` grande es caro: para paginar en serio, *range* sobre `_id` o un índice, no `skip(10_000)`.

### Contar

```javascript
db.reservas.countDocuments({ hotel: "Laredo" })
db.reservas.countDocuments({ hotel: "Laredo", noches: { $gte: 3 } })
```

`count()` en colección y en cursor está **deprecated** (4.0+). Aún lo veréis: `find(…).count()`.

Estimación basada en metadatos de toda la colección: `estimatedDocumentCount()` **no acepta un filtro de consulta**. Para un subconjunto utilizad `countDocuments(filtro)`:

```javascript
db.reservas.estimatedDocumentCount()
```

## Insertar y modificar

Para mantener reproducibles las consultas, terminad primero el bloque de lectura sobre las colecciones originales. Después copiad los datos a una base independiente y realizad **todo el bloque de escrituras y borrados** allí:

```javascript
use hotel
db.reservas.aggregate([{ $out: { db: "hotel_escrituras", coll: "reservas" } }])
db.opiniones.aggregate([{ $out: { db: "hotel_escrituras", coll: "opiniones" } }])
use hotel_escrituras
```

`$out` reemplaza la colección de destino si existía: usad únicamente esta base de ejercicios. Los ejemplos siguientes mantienen el nombre `reservas`, pero la base activa ya es `hotel_escrituras`. Verificadla con `db.getName()`.

`insertMany` = array de documentos.

```javascript
db.reservas.insertMany([
  { hotel: "Laredo", canal: "web", noches: 1, importe: 72 },
  { hotel: "Potes", canal: "ota", noches: 2, importe: 120 },
])
```

`updateOne` / `updateMany`: (1) filtro (2) operadores. **Obligatorio** usar operadores (`$set`…); un documento suelto ya **no** es “reemplazo silencioso” (eso es `replaceOne`).

```javascript
db.reservas.updateOne(
  { hotel: "Laredo", canal: "web" },
  { $set: { canal: "ota", notas: "pasada a OTA" }, $inc: { noches: 1 } }
)
```

Respuesta: `matchedCount`, `modifiedCount`, `upsertedCount`. `updateOne` toca **el primero** que encaja.

Si el filtro no encuentra nada, **no pasa nada**. **Upsert** = si no está, **inserta**:

```javascript
db.reservas.updateOne(
  { hotel: "Islares", canal: "web" },
  { $set: { noches: 2, importe: 110, comarca: "Trasmiera" } },
  { upsert: true }
)
```

| Operador | Oficio |
| --- | --- |
| `$set` | Pone / crea el campo |
| `$unset` | **Quita** el campo (no es un `delete` del documento) |
| `$inc` | Suma (negativo resta) |
| `$mul` | Multiplica |
| `$min` / `$max` | Deja el menor / mayor |
| `$currentDate` | Fecha/hora de ahora |
| `$rename` | Renombra un campo |

```javascript
db.reservas.updateOne({ hotel: "Islares" }, { $unset: { notas: "" } })
db.reservas.updateMany({ comarca: "Trasmiera" }, { $inc: { importe: 1 } })
db.reservas.updateMany({ hotel: "Laredo" }, { $rename: { notas: "observaciones" } })
```

[Operadores de update](https://www.mongodb.com/docs/manual/reference/operator/update/).

### `replaceOne`

Reemplazar significa aportar el nuevo contenido completo, conservando el identificador según las reglas de la operación. Un campo omitido desaparece. Para cambiar solo una propiedad, utilizad `$set`: evita borrar accidentalmente huéspedes, fechas o extras que no habéis incluido en el documento de sustitución.

Sustituye **todo** el documento (salvo `_id`) por el que pasáis. Los campos que no listéis **desaparecen**.

```javascript
db.reservas.replaceOne(
  { hotel: "Islares" },
  { hotel: "Islares", canal: "web", noches: 2, importe: 110 }
)
```

### Concurrencia

Leer `noches`, sumar uno en la aplicación y escribir el resultado puede perder un incremento si dos clientes leen el mismo valor inicial. `$inc` expresa el cambio relativo dentro de la operación atómica. Para descontar una plaza, el filtro debe exigir además `libres: {$gte: 1}` y hay que comprobar si realmente se modificó el documento.

Un `updateMany` **no** es una transacción ACID de toda la colección (salvo que se incluya en una transacción explícita sobre una topología compatible; una sesión por sí sola no basta). Cada **documento** sí es atómico: no queda a medias. Entre documento y documento puede haber una pausa.

`findOneAndUpdate` (el `findAndModify` moderno) busca y cambia **atómico** y puede devolver el documento **ya** cambiado:

```javascript
db.reservas.findOneAndUpdate(
  { hotel: "Laredo", canal: "web" },
  { $inc: { noches: 1 } },
  { returnDocument: "after" }
)
```

Útil para **contadores** (habitaciones libres) sin que dos recepciones pisen el mismo número.

### Arrays: `$push`, `$pull`, `$`

`$push` añade incluso si el valor ya existe; `$addToSet` evita añadir un valor idéntico, pero no ordena ni elimina duplicados previos. El operador posicional `$` depende del elemento que identificó el filtro. Antes de actualizar, ejecutad un `find` con ese filtro para comprobar qué reserva y qué array estáis seleccionando.

| Operador | Oficio |
| --- | --- |
| `$push` | Añade (duplica si ya estaba) |
| `$push` + `$each` | Añade varios |
| `$addToSet` | Añade **sin** duplicar |
| `$pull` | Quita los que coinciden |
| `$pullAll` | Quita una lista |
| `$pop` | `-1` el primero, `1` el último |

```javascript
db.reservas.updateMany({ hotel: "Laredo" }, { $push: { extras: "spa" } })
db.reservas.updateMany(
  { hotel: "Laredo" },
  { $push: { extras: { $each: ["wifi", "parking"] } } }
)
db.reservas.updateMany({ hotel: "Laredo" }, { $addToSet: { extras: "parking" } })
db.reservas.updateMany({ hotel: "Laredo" }, { $pull: { extras: "spa" } })
db.reservas.updateMany({ hotel: "Laredo" }, { $pop: { extras: 1 } })
```

**`$` posicional:** el elemento del array que **encajó** en el filtro.

```javascript
db.reservas.updateOne(
  { hotel: "Santander", "huespedes.nombre": "Ana" },
  { $set: { "huespedes.$.tipo": "adulto_vip" } }
)
```

`$[]` = todos los elementos. `$[iden]` + `arrayFilters` = los que cumplen una condición. [Update de arrays](https://www.mongodb.com/docs/manual/reference/operator/update-array/).

## Borrar

Primero ejecutad `find(filtro)` y `countDocuments(filtro)` en la base de escrituras para comprobar el alcance. Después contrastad `deletedCount` con lo esperado. El resultado de una eliminación es un recuento, no una copia de los documentos borrados.

```javascript
db.reservas.deleteOne({ hotel: "Islares" })
db.reservas.deleteMany({ hotel: "prueba" })
```

Sin filtro, `deleteMany({})` vacía la colección **documento a documento**. `deleteOne({})` borra **uno**. Las **referencias** en otras colecciones **siguen**: las limpiáis vosotros (no hay `ON DELETE CASCADE`).

Quitar un **campo** = `$unset`, no `delete`.

Vaciar y **tirar índices**: `db.reservas.drop()`. Borrar la base: `use hotel` y `db.dropDatabase()`.

## Relación con el RA2

| Criterio | En este apartado |
| --- | --- |
| **a)** | JSON anidado **depositado** y **consultado** sin ocho tablas |
| **d)** | Documentos con distintas claves; `$exists`; campos nuevos con `$set` |

El rendimiento depende de consultas, índices y recursos. Para agregados grandes sobre ficheros podemos evaluar [HDFS y un motor distribuido](computacion-distribuida.md), sin convertir un tamaño concreto en una frontera universal entre productos. Réplicas y *shards*: [2.8](replicas-shards.md). Python: [2.9](pymongo.md).

!!! success "En voz alta"
    “Mongo guarda BSON. El `_id` lo fabrica el driver. `find` es un cursor. Actualizo con `$set`, no pisando el documento a ciegas. El array se toca con `$push` y `$`.”

## Para practicar (Moodle manda la nota)

Importad `reservas` y `opiniones`. Copiad comando y resultado (o captura).

1. **Puesta en marcha.** Docker `hotel-mongo` o Atlas del aula. Compass conectado. `show dbs` / `show collections`.
2. **Consultas sobre `reservas`:**
    1. Todos; el primero (`findOne`).
    2. Hotel `Laredo`; cuántos hay.
    3. Laredo **y** canal `web`.
    4. Laredo **y no** canal `web`.
    5. `noches` menor que 3; `importe` entre 100 y 200.
    6. Hotel en `["Laredo","Noja","Comillas"]`.
    7. Tienen campo `extras`; no tienen `huespedes`.
    8. `distinct` de `canal` en Trasmiera.
    9. Las 5 de más `importe` (documento entero).
    10. `$nor`: ni `ota` ni `Reinosa`, y `noches ≤ 2`.
    11. `$expr`: `importe` ≥ `noches * 80`.
    12. Proyección: solo `hotel` e `importe`, sin `_id`.
    13. Cursor: `web`, orden `importe` desc, documentos del 5 al 8 (`skip`/`limit`).
3. **`opiniones`:**
    1. Etiqueta `playa`; `playa` **y** `parking` (`$all`); `playa` **o** `nieve` (`$in`).
    2. Sin etiqueta `spa` (`$nin` o `$not`).
    3. Exactamente **un** comentario (`$size`); al menos un comentario (`comentarios.0` `$exists` o `$not` `$size: 0`).
    4. Algún comentario de `Luis Sainz`; proyectar el **primer** comentario coincidente (`$elemMatch`); explicad por qué no devuelve todos.
    5. `cuerpo` que contenga `wifi` (`$regex`); título + `$slice` de 2 comentarios y 3 etiquetas.
4. **Escrituras** (colección `reservas` o una `reservas_lab` que luego `drop`):
    1. Insertar Islares (Trasmiera, 2 noches).
    2. `$set` de `importe` a 1 000 000; `$inc` de +1 € a toda Trasmiera.
    3. Añadir `provincia: "Cantabria"`; `$rename` a `comunidad`.
    4. `$set` de `extras: []` y luego `$addToSet` `"parking"`; `$` para cambiar un extra.
    5. `$unset` de un campo; `deleteOne` de Islares.

### Cómo comprobar las respuestas

Entregad pregunta en lenguaje natural, filtro, proyección y resultado. En arrays, incluid un contraejemplo que distinga «el mismo elemento» de «elementos distintos». En fechas, explicad límites y zona horaria. En escrituras, anotad recuento de coincidencias y modificaciones: `matchedCount: 1` y `modifiedCount: 0` puede significar que el valor ya era el solicitado.

Las actividades de escritura se hacen sobre `hotel_escrituras`; las del [parte en Python](pymongo.md) parten otra vez de `hotel` sin modificar. Así una práctica no altera silenciosamente los resultados de la siguiente.

## Referencias

- [Manual de MongoDB](https://www.mongodb.com/docs/manual/)
- [mongosh](https://www.mongodb.com/docs/mongodb-shell/)
- [2.5 Familias](nosql.md) · [2.7 Modelado](modelado.md) · [2.8 Réplicas](replicas-shards.md) · [2.9 PyMongo](pymongo.md)
