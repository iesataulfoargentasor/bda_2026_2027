---
title: 2.6 MongoDB
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.6. MongoDB

!!! info "Ruta de estudio"
    **Esencial:** documentos y tipos BSON; carga comprobada; filtros, proyecciones, arrays, fechas y recuentos; escrituras con resultado verificado.

    **Recorrido guiado:** conservar `hotel` para consultar, usar `hotel_demo` para ejemplos y `hotel_escrituras` para modificar. Primero expresad la pregunta; después escribid la consulta y contrastad su resultado.

    **Ampliación:** Atlas, copias y restauración, operadores menos frecuentes y análisis de índices. Las entregas evaluables se concretan en Moodle.

En [2.5](nosql.md) elegimos un modelo según las consultas y las garantías. Ahora lo aplicamos: recepción busca una reserva, consulta sus extras y modifica información concreta. Conservamos la idea de la UT1: **una operación terminada no basta; hay que comprobar qué datos ha leído o cambiado**.

Trabajaremos con **15 reservas y 6 opiniones**, diferentes de las 20 reservas de Hadoop. Las noches e importes de estos documentos describen reservas, no ocupación real ni cobros confirmados. El fichero no incorpora un identificador de negocio; los ejemplos usarán el `_id` de MongoDB o identificadores explícitos de laboratorio.

[MongoDB](https://www.mongodb.com/) es la NoSQL **documental** del aula. Los documentos se basan en JSON; por dentro el motor guarda **BSON**. El nombre viene de *humongous*: gigantesco.

Destaca porque:

- **Esquema dinámico:** dos documentos de `reservas` **no** tienen por qué traer las mismas claves (criterio **d)**).
- Permite relacionar documentos mediante `$lookup`. Embeber datos que se consultan juntos puede ayudar, pero las referencias también son válidas: se decide según crecimiento, actualizaciones y restricciones ([2.7](modelado.md)).
- Una inserción o un `update` de **un** documento es atómico. Una transacción **entre varios documentos** la ejecuta el servidor en una topología compatible; la aplicación la solicita mediante una sesión del driver. En un RDBMS serían varias filas y un `COMMIT`.

Analogía: base ≈ esquema SQL, colección ≈ tabla, documento ≈ fila… **pero** el esquema puede ser flexible o incorporar validadores explícitos. El criterio **a)** aquí: organizáis y consultáis documentos anidados, comprobando tipos, significado y validación; poder cargar un JSON no garantiza que sus datos sean correctos.

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
- Los nombres con `$` inicial o `.` tienen restricciones y requieren tratamiento especial. En esta práctica usamos nombres sencillos y reservamos el punto para acceder a campos anidados.

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

Mantener tipos coherentes facilita las consultas. Los tipos numéricos tienen reglas de comparación entre sí, pero la cadena `"18"` no equivale al número `18`. Para importes de producción habría que acordar precisión y redondeo, por ejemplo Decimal128 o unidades monetarias enteras; aquí conservamos los números del conjunto didáctico.

## Puesta en marcha

Tres productos:

| Producto | Oficio |
| --- | --- |
| **Atlas** | Servicio gestionado en la nube; comprobad los límites del plan elegido |
| **Community** | Gratis *on-premise* (Windows, macOS, Linux) |
| **Enterprise** | Pago: soporte, seguridad y monitorización extra |

El demonio escucha en **27017**. Si abrís `http://localhost:27017` en el navegador veréis un aviso: ese puerto es el del **driver**, no una web. La UI es **Compass** o Atlas.

Seguid el entorno indicado por el profesor. La ruta principal de esta página es Docker local; Atlas es una alternativa. Los comandos con `127.0.0.1` no conectan al servidor de otro equipo ni a Atlas: en esos casos hay que utilizar la conexión asignada. Cada alumno necesita una base propia si el servidor es compartido.

| Dónde se ejecuta | Qué se escribe |
| --- | --- |
| Terminal del PC (PowerShell o Bash) | `docker`, `mongoimport`, `mongosh`, comandos de copia |
| Dentro de `mongosh` | `use hotel`, `db.reservas.find(...)` |
| Fichero JavaScript ejecutado por mongosh | JavaScript; para elegir base, `db.getSiblingDB("hotel")` |

Las Database Tools y `mongosh` son herramientas distintas del servidor. Comprobad qué está instalado antes de copiar un comando.

### Docker

Antes de arrancar, comprobad `docker info`. Si no conecta, iniciad Docker Desktop y esperad a que el motor esté listo. Revisad con `docker ps -a` si ya existe `hotel-mongo`. Si el laboratorio de réplicas de 2.8 ocupa el puerto 27017, detened ese laboratorio siguiendo sus instrucciones; no pueden compartir el mismo puerto del PC.


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

Comprobad el mensaje final de cada importación: deben haberse importado **15** y **6** documentos, respectivamente, sin errores. En PowerShell, `$LASTEXITCODE` debe ser 0 inmediatamente después del comando; en Bash, comprobad `$?`.

Si no habéis descargado el repositorio completo, descargad [reservas_mongo.jsonl](../assets/practicas/reservas_mongo.jsonl) y [opiniones.jsonl](../assets/practicas/hotel-mongo/opiniones.jsonl) en una carpeta. Abrid allí la terminal y sustituid las rutas de `--file` por los nombres de los archivos. Son JSONL: un documento por línea, por eso no añadimos `--jsonArray`.

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

Los ejemplos de «Hola MongoDB» y ObjectId se realizan en `hotel_demo`, no en `hotel`. Para empezar de nuevo, conservad primero el trabajo que queráis entregar y recargad únicamente las colecciones de práctica. No añadimos `--drop` por defecto para evitar eliminar datos al repetir un comando.

Verificad también los tipos y algunas propiedades del conjunto:

```javascript
db.reservas.countDocuments({checkin: {$type: "date"}}) // 15
db.reservas.countDocuments({extras: {$exists: true}})  // 6
db.reservas.countDocuments({huespedes: {$exists: false}}) // 13
```

Los recuentos detectan cargas repetidas, pero no todos los cambios en el contenido. Más abajo hay resultados de referencia y un comprobador de consultas. Si una importación queda incompleta, no la repitáis sobre lo ya cargado: guardad el trabajo, revisad el error y preparad colecciones vacías de práctica antes de recargar.

### Atlas (si el profesor lo pide)

Cread el despliegue autorizado, un usuario de base con los permisos necesarios y el acceso de red para vuestro equipo. Elegid la región y el plan indicados; comprobad sus límites. Guardad las credenciales fuera del repositorio y de las capturas. Utilizad la URI del proyecto y evitad abrir el acceso a cualquier dirección.

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
mongosh "mongodb+srv://cluster0.xxxxx.mongodb.net/hotel" --username USUARIO
```

### Database Tools

[Herramientas](https://www.mongodb.com/try/download/database-tools): JSON ↔ colección y copias **binarias**.

No ejecutéis esta sección como si fuera otra carga inicial. La importación ya se ha realizado; los comandos siguientes son una **ampliación** sobre el servidor local, desde la terminal del PC:

```text
mongoexport --host 127.0.0.1 --port 27017 -d hotel -c reservas -o reservas_export.jsonl
mongodump --host 127.0.0.1 --port 27017 -d hotel -o backup_hotel
mongorestore --host 127.0.0.1 --port 27017 --nsInclude="hotel.*" --nsFrom="hotel.*" --nsTo="hotel_restauracion.*" backup_hotel
```

La restauración se dirige a una **base de prueba vacía**, `hotel_restauracion`, para no mezclarla con los originales. Si ya existe, conservad el trabajo y elegid otro destino. Comprobad después documentos e índices, no solo que el comando termine.

`mongoexport` genera Extended JSON (o CSV según opciones), pero no conserva por sí solo toda la configuración e índices. `mongodump` produce BSON y metadatos; `mongorestore` permite reconstruirlos. Una copia requiere además planificar la consistencia durante escrituras, compatibilidad, conservación y pruebas de recuperación. No basta con tener un archivo.

También se puede importar CSV con `--type csv --headerline`, definiendo los tipos necesarios. `ocupacion.csv` **no forma parte de los materiales de este apartado**; no hace falta buscarlo para completar la práctica. `bsondump fichero.bson` permite inspeccionar un BSON de un dump como texto.

!!! question "¿Exportación o dump?"
    Un `.jsonl` exportado y una carpeta con `.bson` y `.metadata.json` no son equivalentes. Explicad qué información conserva cada uno y cómo verificaríais la restauración.

Monitorización: `mongostat`, `mongotop`. En Atlas van en el panel. *Drivers* oficiales para casi todos los lenguajes; Python es el [2.9](pymongo.md).

### Compass y VS Code

**Compass:** explorar, esquema, agregados, índices, consultas. Las funciones disponibles dependen de la versión instalada. Pegáis la URI y listo. Abajo hay un **mongosh** embebido.

**MongoDB for VS Code:** la misma URI y un *playground* (guion al estilo *shell*).

Trabajaremos con `mongosh` para guardar comandos reproducibles. Una captura de Compass también puede aportar evidencia si explica el filtro y el resultado; la herramienta utilizada no sustituye a esa comprobación.

## Hola MongoDB

Patrón de casi todo: `db.nombreColeccion.operacion()`.

```javascript
use hotel_demo
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

Si no hay un validador que lo impida, podéis insertar otra reserva **sin** `extras`. Eso no significa que MongoDB deduzca automáticamente el contrato de la aplicación. Más adelante, un `validator` ([2.7](modelado.md)) puede exigir reglas y rechazar documentos que las incumplan.

### JavaScript en el shell

```javascript
load("semilla_hotel.js")
```

Este ejemplo presupone que habéis guardado vuestro código en `semilla_hotel.js`; no es un fichero incluido en el repositorio. La ruta se resuelve donde se ejecuta `mongosh`: si está dentro de Docker, copiad primero el archivo al contenedor. Para los datos iniciales de esta unidad utilizad los JSONL enlazados, sin necesidad de ese script.

```text
mongosh hotel_demo semilla_hotel.js
```

Bucle en `hotel_demo` (crea diez documentos; repetirlo añade otros diez):

```javascript
for (let i = 0; i < 10; i++) {
  db.reservas_lab.insertOne({ hotel: "Laredo", canal: "web", noches: i + 1 });
}
```

## ObjectId

El identificador distingue documentos; no es el número de reserva ni garantiza un orden cronológico exacto entre clientes. Los ejemplos que usan `getTimestamp()` presuponen que `_id` es un `ObjectId`; si insertáis un entero como identificador, ese método no existe para ese valor. Una referencia debe conservar el mismo valor **y tipo** que el identificador referenciado.

En la colección sin particionar del laboratorio, `_id` identifica de forma única cada documento. Si se omite, normalmente el driver o `mongosh` genera un **ObjectId**; el servidor también puede generarlo si recibe una inserción sin ese campo. Contiene 12 bytes:

- 4 bytes: *timestamp*;
- 5 bytes: valor aleatorio por proceso;
- 3 bytes: contador.

No asumas un orden global perfecto: dos portátiles con reloj distinto **desordenan**. Podéis extraer la marca temporal de generación del identificador, que no demuestra cuándo se guardó en el servidor ni cuándo ocurrió la reserva:

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

`edad: 14` es numérico y `edad: "14"` es texto. Para fijar un tipo BSON concreto, utilizad los constructores y validadores adecuados.

Los `_id` explícitos del ejemplo solo se insertan una vez. Repetirlos en la misma colección provoca un error de clave duplicada; no significa que se haya actualizado el documento.

## Recuperar datos

Volvemos a los originales, sin ejecutar inserciones aquí:

```javascript
use hotel
db.getName() // hotel
```


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

Un índice no acelera por igual todas las expresiones regulares. El patrón sin anclar y sin distinguir mayúsculas de este ejemplo puede requerir recorrer muchos datos. Para otras necesidades de búsqueda, estudiad índices de texto o las herramientas de búsqueda del despliegue. Comprobad el plan, no solo el tiempo con quince documentos.

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

**`$where` — referencia, no necesario en la práctica:** evalúa JavaScript en el servidor y esa expresión no aprovecha índices. Preferid operadores de consulta o `$expr`. Su disponibilidad y recomendaciones dependen de la versión; desde MongoDB 8.0 el JavaScript del servidor está obsoleto.

### Proyección

El primer argumento de `find` responde **qué documentos**; el segundo, **qué campos devolver**. La proyección reduce el contenido transferido y facilita leer la respuesta, pero no modifica los documentos almacenados. Excluir `_id` es la excepción habitual que permite combinar inclusión de campos con una exclusión.

Segundo argumento: qué campos ver (`1` / `true`) u ocultar (`0` / `false`). `_id` sale **siempre** salvo que lo apaguéis.

```javascript
db.reservas.find({ hotel: "Laredo" }, { canal: 1, importe: 1 })
db.reservas.find({ hotel: "Laredo" }, { canal: 1, importe: 1, _id: 0 })
```

!!! warning "No mezcléis 1 y 0"
    En las proyecciones básicas de esta práctica, elegid inclusión o exclusión. Podéis excluir `_id` mientras incluís otros campos. No mezcléis, por ejemplo, `hotel: 1` y `importe: 0`.

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

Al consultar una **ruta con punto**, no necesitamos reproducir el objeto completo ni su orden de campos. Eso no equivale a comparar el subdocumento entero por igualdad.

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

Si solo filtráis **un** campo del subdocumento del array, basta la notación punto: `"comentarios.autor": "Luis Sainz"`. Para exigir que esas condiciones se cumplan en el mismo comentario utilizamos `$elemMatch`.

Proyectar el **primer comentario coincidente de cada documento**:

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

El cursor se ejecuta cuando se solicitan resultados, por ejemplo al iterarlo o mostrarlo en el shell. `hasNext()` y `next()` pueden solicitar nuevos lotes al servidor; no significan que todo esté ya en el cliente. Definid `sort` y `limit` antes de consumirlo.

```javascript
const c = db.reservas.find({ comarca: "Trasmiera" })
c.hasNext()
c.next()
```

```javascript
db.reservas.find().sort({ importe: -1, _id: 1 }).limit(3)
db.reservas.find({ canal: "web" }).sort({ importe: -1, _id: 1 }).limit(3)
db.reservas.find({ canal: "web" }).sort({ importe: -1, _id: 1 }).skip(4).limit(5)
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

`updateOne` / `updateMany`: (1) filtro y (2) actualización. Aquí usamos operadores como `$set` y `$inc`; también existen pipelines de actualización con etapas admitidas. Para sustituir un documento completo utilizamos `replaceOne`.

```javascript
const elegida = db.reservas.findOne({hotel: "Laredo", canal: "web"})
if (!elegida) throw new Error("No se encontró la reserva de ejemplo")
printjson(elegida) // revisadla antes de modificar
db.reservas.updateOne(
  { _id: elegida._id },
  { $set: { canal: "ota", notas: "pasada a OTA" }, $inc: { noches: 1 } }
)
```

Revisad `matchedCount`, `modifiedCount` y, si corresponde, `upsertedCount`/`upsertedId`. `updateOne` cambia un documento coincidente; un filtro amplio no identifica una reserva de negocio. Tras revisar `elegida`, el filtro por `_id` hace explícito cuál cambia. `matchedCount: 1` con `modifiedCount: 0` puede indicar que el valor solicitado ya estaba guardado.

Si el filtro no encuentra documentos y no se solicita upsert, no se modifica nada: hay que revisar el recuento, no interpretar la ausencia de excepción como éxito de negocio. **Upsert** = si no está, **inserta**:

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

El ejemplo incrementa noches; no confirma disponibilidad comercial. Un contador de plazas necesita además la condición de disponibilidad en el filtro, como se explica arriba, y comprobar el resultado. La réplica y la transacción multidocumento se estudian después.

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

`drop()` elimina la colección y sus índices; `dropDatabase()` elimina la base activa. Son operaciones distintas de borrar documentos. No las ejecutéis en `hotel`: conservamos sus originales para 2.9. Para terminar la sesión local basta con `docker stop hotel-mongo` desde la terminal del PC; el volumen conserva los datos.

## Relación con el RA2

| Criterio | En este apartado |
| --- | --- |
| **a)** | Cargar documentos, comprobar tipos y consultar según una necesidad concreta |
| **d)** | Documentos con distintas claves; `$exists`; campos nuevos con `$set` |

El rendimiento depende de consultas, índices y recursos. Para agregados grandes sobre ficheros podemos evaluar [HDFS y un motor distribuido](computacion-distribuida.md), sin convertir un tamaño concreto en una frontera universal entre productos. Réplicas y *shards*: [2.8](replicas-shards.md). Python: [2.9](pymongo.md).

!!! success "En voz alta"
    “MongoDB conserva documentos BSON. Primero comprobamos base y datos. El filtro selecciona documentos y la proyección selecciona campos. Identificamos qué modificamos y contrastamos el resultado. Esquema flexible no significa ausencia de reglas.”

## Actividades

Seguid este orden y conservad **pregunta, base activa, comando, resultado e interpretación**. Las actividades 1–3 usan `hotel` original; la 4 usa una copia nueva en `hotel_escrituras`. Las condiciones de entrega se concretan en Moodle. No es necesario contratar Atlas ni utilizar una interfaz gráfica para resolverlas.

1. **Puesta en marcha.** Docker `hotel-mongo` o conexión asignada por el profesor. Registrad versión y base activa; comprobad 15 reservas, 6 opiniones y 15 fechas BSON. Explicad dónde se ejecutan `mongoimport` y `db.reservas.find()`. Compass es opcional.
2. **Consultas sobre `reservas`:**
    1. Todos; el primero (`findOne`).
    2. Hotel `Laredo`; cuántos hay.
    3. Laredo **y** canal `web`.
    4. Laredo **y no** canal `web`.
    5. `noches` menor que 3; `importe` entre 100 y 200, ambos incluidos.
    6. Hotel en `["Laredo","Noja","Comillas"]`.
    7. Tienen campo `extras`; no tienen `huespedes`.
    8. `distinct` de `canal` en Trasmiera.
    9. Las 5 de más `importe` (documento entero), con `_id` como desempate.
    10. `$nor`: ni `ota` ni `Reinosa`, y `noches ≤ 2`.
    11. `$expr`: `importe` ≥ `noches * 80`.
    12. Proyección: solo `hotel` e `importe`, sin `_id`.
    13. Cursor: `web`, orden `importe` descendente y `_id` ascendente, puestos del 5 al 8: `skip(4).limit(4)`. Explicad por qué pueden salir menos de cuatro.
3. **`opiniones`:**
    1. Etiqueta `playa`; `playa` **y** `parking` (`$all`); `playa` **o** `nieve` (`$in`).
    2. Sin etiqueta `spa` (`$nin` o `$not`).
    3. Exactamente **un** comentario (`$size`); al menos un comentario (`"comentarios.0": {$exists: true}`). Explicad por qué negar `$size: 0` también puede incluir documentos sin el campo en otros conjuntos.
    4. Algún comentario de `Luis Sainz`; proyectar el **primer** comentario coincidente (`$elemMatch`); explicad por qué no devuelve todos.
    5. `cuerpo` que contenga `wifi` (`$regex`); título + `$slice` de 2 comentarios y 3 etiquetas.
4. **Escrituras identificadas.** Guardad primero el trabajo previo que necesitéis. Preparad una copia limpia mediante el bloque `$out` de «Insertar y modificar» y verificad `db.getName()`: debe ser `hotel_escrituras`. No ejecutéis antes las demostraciones de escritura sobre esa copia. Realizad esta secuencia una sola vez:
    1. Insertad `{_id: "UT26-ISLARES", hotel: "Islares", canal: "web", comarca: "Trasmiera", noches: 2, importe: 110}`. Debe haber 16 reservas.
    2. Sobre ese `_id`, fijad `importe` en 1000000. Después sumad 1 al importe de **todas** las reservas de Trasmiera. Preved cuántas coinciden antes de ejecutarlo.
    3. Solo en `UT26-ISLARES`, añadid `provincia: "Cantabria"` y renombrad ese campo a `comunidad`.
    4. En ese documento, fijad `extras: []`; añadid `parking` dos veces con `$addToSet` y comprobad que queda una sola vez. Cambiadlo a `parking_cubierto` con el operador posicional `$`, filtrando por `_id` **y** `extras: "parking"`.
    5. Quitad `comunidad` con `$unset` y eliminad la reserva con `deleteOne({_id: "UT26-ISLARES"})`. Verificad `deletedCount` y el recuento final. Explicad por qué volver a 15 documentos no restaura los importes originales de la copia.
5. **Nulo, ausente y vacío.** En `hotel_demo`, cread tres documentos en una colección nueva: uno sin `extras`, otro con `extras: null` y otro con `extras: []`. Predecid y comprobad `{extras: null}`, `$exists: false` y `$size: 0`. Relacionadlo con la validación del esquema.
6. **El mismo comentario.** En los datos originales, buscad una opinión que contenga autor `Ana Ruiz` y correo `luis@ejemplo.es` usando dos rutas independientes. Repetid con `$elemMatch`. Comparad los resultados y explicad por qué las condiciones pueden pertenecer a personas distintas.
7. **Fechas y significado.** Consultad entradas de abril de 2026 con límites UTC, inicio incluido y fin excluido. Comprobad el tipo y explicad qué habría que cambiar si el periodo se definiera como días civiles de Cantabria. No sustituyáis la fecha BSON por una cadena para que coincida.
8. **Actualización sin cambio y reemplazo.** En una colección nueva de `hotel_demo`, insertad un documento con `canal` y `extras`. Asignad con `$set` el canal que ya tiene y contrastad coincidencias y modificaciones. Después usad `replaceOne` sin incluir `extras`: comprobad qué desaparece y qué ocurre con `_id`.
9. **Índices — ampliación.** En `hotel_escrituras`, observad `explain("executionStats")` antes y después de crear un índice para una consulta. Comparad documentos y claves examinados. Con quince registros, un tiempo de 0 ms no demuestra que el índice mejore cualquier carga; el optimizador puede elegir un recorrido de colección.
10. **Recuperación — ampliación.** Realizad el dump y la restauración en una base vacía diferente siguiendo «Database Tools». Contrastad contenido e índices. Explicad por qué la copia no prueba por sí sola alta disponibilidad ni computación distribuida.

### Resultados de referencia de las consultas

Se aplican a los archivos originales, sin las demostraciones ni escrituras. Los importes son los de las reservas del fichero.

| Consulta | Resultado esperado |
| --- | --- |
| Laredo; Laredo web; Laredo no web | 3; 1; 2 documentos |
| Noches menores que 3; importe entre 100 y 200 inclusive | 7; 6 documentos |
| Hotel Laredo, Noja o Comillas | 7 documentos |
| Tienen extras; no tienen huéspedes | 6; 13 documentos |
| Canales de Trasmiera | `ota`, `recepcion`, `web`, sin depender del orden |
| Cinco importes mayores | Potes 490; Santander 410; Laredo 372; Potes 280; Reinosa 260 |
| NOR de la actividad 2.10; comparación de la 2.11 | 3; 2 documentos |
| Reservas web en los puestos 5–8 | Reinosa 140 y Comillas 89,9: solo hay seis reservas web |
| Opiniones: playa; playa y parking; playa o nieve; sin spa | 3; 1; 4; 5 documentos |
| Exactamente un comentario; al menos uno; comentario de Luis | 3; 5; 2 documentos |
| `wifi` en el cuerpo principal | «Spa y wifi». El texto de comentarios es otro campo |
| Reservas con checkin en abril UTC | 3 documentos |

Podéis descargar [comprobar_consultas.js](../assets/practicas/hotel-mongo/comprobar_consultas.js). Realiza **30 comprobaciones de solo lectura** sobre la base de la conexión. No modifica datos ni certifica que todo el contenido sea idéntico al original; sirve para detectar errores frecuentes de carga y de resultados.

Si utilizáis Docker, desde la raíz del repositorio en la **terminal del PC**:

```text
docker cp docs/assets/practicas/hotel-mongo/comprobar_consultas.js hotel-mongo:/tmp/comprobar_consultas.js
docker exec hotel-mongo mongosh hotel --quiet --file /tmp/comprobar_consultas.js
```

Si tenéis `mongosh` en el PC:

```text
mongosh "mongodb://127.0.0.1:27017/hotel" --quiet --file docs/assets/practicas/hotel-mongo/comprobar_consultas.js
```

Para un servidor compartido o Atlas, utilizad la conexión y base asignadas, sin publicar credenciales. Si descargasteis el script suelto, ajustad su ruta. El resultado esperado es `Pruebas: 30; fallos: 0`. Ante un error, revisad base activa, tipos y cargas anteriores; no modifiquéis la referencia para ocultarlo.

??? success "Orientaciones para revisar las actividades"
    **1–3.** Contrastad filtros y recuentos con la tabla. La proyección no elimina campos almacenados. `$elemMatch` en proyección devuelve el primer elemento coincidente, no todos.

    **4.** Tras la inserción hay 16 reservas. El incremento de Trasmiera coincide con 6 documentos; Islares termina con importe 1000001. `$addToSet` repetido conserva un único parking. El filtro posicional identifica ese valor en la reserva indicada. El borrado final elimina uno y quedan 15, pero cinco reservas originales de Trasmiera siguen con un euro más en la copia. `hotel` permanece intacta.

    **5–6.** `{extras: null}` encuentra el nulo y el ausente; `$exists: false`, solo el ausente; `$size: 0`, el array vacío. Con Ana y el correo de Luis, las rutas independientes encuentran «Centro y ruido»; `$elemMatch` no encuentra ninguna porque no existe ese mismo comentario.

    **7–8.** Abril UTC devuelve tres reservas. Los límites civiles se convierten según `Europe/Madrid`. Asignar el mismo valor puede dar una coincidencia y cero modificaciones; reemplazar elimina los campos omitidos y conserva el `_id` existente si no se cambia.

    **9–10.** Documentad el plan observado y los límites del conjunto pequeño. Una restauración necesita comprobarse en su destino; no demuestra la elección de primario ni tolerancia a caídas del laboratorio 2.8.

### Cómo comprobar las respuestas

Entregad pregunta en lenguaje natural, filtro, proyección y resultado. En arrays, incluid un contraejemplo que distinga «el mismo elemento» de «elementos distintos». En fechas, explicad límites y zona horaria. En escrituras, anotad recuento de coincidencias y modificaciones: `matchedCount: 1` y `modifiedCount: 0` puede significar que el valor ya era el solicitado.

Las actividades de escritura se hacen sobre `hotel_escrituras`; las del [parte en Python](pymongo.md) parten otra vez de `hotel` sin modificar. Así una práctica no altera silenciosamente los resultados de la siguiente.

## Autoevaluación del 2.6

Diez preguntas (A–D, **una** correcta). No puntúan en Moodle. **Comprobar respuesta** muestra el resultado y explica el motivo. Revisad el apartado enlazado antes de repetir.

<div class="dwec-quiz" data-dwec-quiz data-src="../../assets/quizzes/ut2-2-6.json"></div>

En [2.7](modelado.md) decidiremos qué datos conviene agrupar y qué reglas validar. Aquí hemos practicado operaciones sobre una instancia; no hemos demostrado por ello reparto entre máquinas ni tolerancia a fallos. Esas pruebas corresponden a los apartados específicos de la unidad.

## Referencias

- [Manual de MongoDB](https://www.mongodb.com/docs/manual/)
- [mongosh](https://www.mongodb.com/docs/mongodb-shell/)
- [2.5 Familias](nosql.md) · [2.7 Modelado](modelado.md) · [2.8 Réplicas](replicas-shards.md) · [2.9 PyMongo](pymongo.md)

- [mongoimport y Extended JSON](https://www.mongodb.com/docs/database-tools/mongoimport/).
- [Actualización de un documento](https://www.mongodb.com/docs/manual/reference/method/db.collection.updateOne/).
- [Condiciones sobre el mismo elemento de un array](https://www.mongodb.com/docs/manual/reference/operator/query/elemMatch/).
