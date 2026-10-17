---
title: 2.7 Modelado documental
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.7. Modelado documental

Tanto en SQL como en MongoDB empezamos por los datos, las operaciones y las reglas de negocio. En un modelo documental tiene especial importancia **qué información se lee y actualiza junta**. El criterio **d)** del RA2 no es “tirar JSON al cubo”. Es: **guardáis lo que hay hoy** y **dejáis hueco** para el campo de abril, sin tumbar el hotel una noche y sin reescribir 40 000 reservas.

Un documento es el sitio donde vive **lo que se lee junto**. Una escritura sobre un documento es atómica. Si una operación modifica reserva y cobro en dos documentos, un único `update` no los convierte en una unidad atómica: necesitáis una transacción explícita en el servidor, iniciada desde una sesión del cliente. El atajo mental “3FN + `$lookup` en cada pantalla” suele ser señal de que seguís modelando como PostgreSQL.

El código se lee mejor —y el `find` corre antes— cuando aceptáis **cierta redundancia**. Duplicar el nombre del hotel en la reserva no es suciedad: es **no hacer un join** cada vez que recepción abre la ficha.

## Empieza por las preguntas, no por las entidades

Antes de Compass, escribid **qué hace** cada rol. Tres ejemplos del grupo:

| Quién | Qué abre | Qué necesita ver *ya* |
| --- | --- | --- |
| Recepción | Ficha de una reserva | Hotel, noches, huéspedes, cobro |
| Gerencia | Ocupación de Laredo | Conteos, no el DNI de cada huésped |
| Mantenimiento | Incidencias de la 214 | Historial largo (años), no la ficha de reserva |

Luego medid, aunque sea a groso modo:

- ¿Más **lecturas** o más **escrituras**?
- ¿Cuántas veces por minuto? ¿Qué latencia aguanta el mostrador?
- ¿Qué campos entran en el filtro (`hotel`, `checkin`, `comarca`)?
- ¿Hay algo que **cambia** (teléfono del hotel) y algo que **debe quedar congelado** (precio ya cobrado)?

Un equipo pequeño, una sola *app* y siempre las mismas consultas: **simple**. Embebéd lo que quepa. Un equipo grande, muchas *apps* y picos de escritura: mirad **tamaño**, **ops/s** y **qué operación no puede fallar**. Optimizar código es más barato que destensar un esquema ya enrevesado: **empezad simple**.

### Carga de aula: no es el sensor de un MOOC

Imaginad 12 hoteles, 800 habitaciones y un sensor de puerta/temperatura por habitación. Cada minuto llega una medida. Gerencia, cada hora, quiere un resumen. Ciencia de datos, de vez en cuando, el minuto a minuto de un invierno.

| Actor | Gestos | Ritmo (orden) | Lectura o escritura | Nota de modelado |
| --- | --- | --- | --- | --- |
| Sensor 214 | `hab`, `ts`, `temp_c`, `puerta` | ~800/min en el grupo | Escritura | Un documento **por minuto** hincha índices; un **cubo por hora** agrupa |
| Reloj de gerencia | Agregar la hora | 1/hora | Escritura | Valor **ya sumado** (patrón calculado) |
| Analista | Tendencia de un mes | Pocas, *scan* | Lectura | Puede ir a un secundario ([2.8](replicas-shards.md)) |

Conclusión distinta a “un JSON por clic”: **agrupáis escrituras** y **precalculáis** lo que gerencia pide siempre. El detalle de *buckets* está más abajo.

## Solo hay dos gestos: meter dentro o señalar fuera

Decidid con cuatro preguntas: ¿se lee junto?, ¿cambia junto?, ¿crece de forma acotada?, ¿necesita una actualización atómica? Embeber favorece la lectura conjunta y la atomicidad de un documento. Referenciar evita repetir entidades compartidas y permite que cada una tenga su propio ciclo de vida.

Duplicar un nombre puede representar una **instantánea histórica** o una copia del nombre actual. En el primer caso no debemos actualizarlo si cambia el hotel; en el segundo necesitamos una estrategia para mantenerlo sincronizado. La duplicación solo está bien definida cuando explicitamos esa diferencia.

**Meter dentro (embeber):** el cobro viaja *con* la reserva. Un `find`, un `update`. Atómico. Tope: **16 MiB** por documento. `bsonSize` en el *shell* os dice cuánto ocupa el que tenéis abierto:

```javascript
bsonSize(db.reservas.findOne({ hotel: "Laredo" }))
```

Fotos de habitación: la ruta o un `id` de objeto; los bytes gordos a **GridFS** o a [HDFS](hdfs.md), no al BSON.

**Señalar fuera (referencia):** `id_hotel` en la reserva. Segunda lectura o `$lookup`. Bien cuando el hotel **cambia** el teléfono y no queréis tocar 40 000 copias.

Referencia **a mano** (lo habitual):

```javascript
const idLaredo = ObjectId()
db.hoteles.insertOne({
  _id: idLaredo,
  nombre: "Laredo",
  telefono: "942 60 00 00",
  comarca: "Trasmiera",
})
db.reservas.insertOne({
  hotel_id: idLaredo,
  canal: "web",
  noches: 3,
  importe: 186.5,
})
```

```javascript
db.reservas.aggregate([
  {
    $lookup: {
      from: "hoteles",
      localField: "hotel_id",
      foreignField: "_id",
      as: "hotel",
    },
  },
])
```

`$lookup` lo usaréis en agregaciones ([2.9](pymongo.md)). Si **cada** pantalla lo necesita, el modelo pide **duplicar un trozo** (nombre + comarca), no un join eterno.

En textos viejos salen **DBRef** (`$ref`, `$id`, `$db`). Mongo **desaconseja** usarlas. Quedaos con el `_id` y el nombre de colección en la *app*.

## Cardinalidad: el hotel en cuatro tamaños

No memoricéis “1:N = array”. Preguntad **cuántos** y **si se leen siempre juntos**.

### Uno a uno (ficha y dirección de envío)

La cardinalidad 1:1 no obliga a embeber. Si los datos de llegada son pequeños y aparecen en la ficha de reserva, resulta cómodo. Si un documento médico u otra información con acceso separado tuviera un ciclo de vida distinto, la referencia podría ser más adecuada. El criterio es la operación, no solo el dibujo de la relación.

La reserva y el *check-in* breve (matrícula del coche, hora de llegada) se leen **siempre** a la vez → **dentro**.

```json
{
  "hotel": "Potes",
  "noches": 2,
  "llegada": { "hora": "16:00", "matricula": "1234-ABC" }
}
```

Separadlos si: uno se consulta **casi nunca**, uno es **enorme**, o uno se **reescribe** diez veces más que el otro. Si tenéis que cambiar **los dos a la vez**, volved a embeber: si no, pagáis transacción.

### Uno a pocos (huéspedes)

Escribid el límite esperado: por ejemplo, cuatro huéspedes en una reserva familiar. Ese límite hace previsible el tamaño. Si el mismo huésped necesita un perfil compartido entre muchas reservas, la ficha histórica puede guardar sus datos de estancia y una referencia opcional al perfil, sin copiar todo su historial.

Una reserva, 1–4 personas. Van **en un array dentro**. Misma lectura, mismo `update`.

```json
{
  "hotel": "Santander",
  "huespedes": [
    { "nombre": "Ana", "tipo": "adulto" },
    { "nombre": "Leo", "tipo": "nino" }
  ]
}
```

Cuidado con el techo de 16 MiB si alguien embebe **PDFs**.

### Uno a muchos (hotel → reservas)

La consulta «reservas del hotel durante abril» se resuelve filtrando la colección de reservas. Un índice que empiece por `hotel_id` y continúe por la fecha puede ayudar. Evitamos cargar un documento de hotel creciente cada vez que entra una reserva y podemos paginar los resultados.

Un hotel, decenas de miles de reservas. El `_id` del hotel vive **en el lado de las muchas**. No metáis un array de 40 000 `ObjectId` en `hoteles`.

```json
{ "_id": "...", "nombre": "Laredo", "telefono": "942…" }
```

```json
{ "hotel_id": "...", "canal": "web", "noches": 3, "importe": 186.5 }
```

**Precio ya cobrado:** ese número se **congela** en la reserva. Si mañana Laredo pone la doble a 200 €, el cobro de abril **no** se mueve. Es el mismo gesto que embeber el precio en un pedido: el catálogo cambia; el ticket, no.

**Nombre del hotel en la ficha:** si recepción lo pide **siempre**, copiad `nombre` + `comarca` en la reserva (*referencia extendida*). El teléfono que **sí** cambia se queda en `hoteles`.

### Uno a tropecientos (habitación → logs de puerta)

Cada evento debe identificar inequívocamente habitación **y hotel**: la habitación 214 puede existir en varias sedes. Además se registra el instante y el tipo de evento. Para consultar un periodo, el índice debe seguir esa combinación; guardar eventos en otra colección sin diseñar el acceso solo desplaza el problema.

Millones de líneas. La habitación **no** guarda el array. Cada evento apunta a la habitación (muchos → uno). Invertís la flecha para no reventar el BSON.

```json
{ "hab": "214", "ts": "2026-04-12T22:03:00Z", "evento": "apertura" }
```

### Varios a varios (habitaciones ↔ servicios)

Una colección de asociaciones es válida también en MongoDB. Resulta útil cuando la relación tiene atributos propios, como vigencia, precio contratado o disponibilidad. No implica necesariamente tres viajes a la base: una agregación puede reunir resultados. Comparad frecuencia de lectura y coste de mantener referencias duplicadas antes de elegir.

Spa, parking, cuna: una habitación tiene pocos servicios; un servicio (parking) toca muchas habitaciones. Tres caminos, **ninguno** es “la tabla puente de SQL” como primera opción:

1. Colección puente `hab_id` + `servicio_id`: tres lecturas. Solo si el puente **tiene vida propia** (fecha, precio extra).
2. Array de ids **en un lado** (el *pequeño*). Suele bastar. Array **en los dos** (*two-way*): coherencia a mano, fácil de romper.
3. Embeber el servicio entero en la habitación: solo si el servicio **casi no cambia** y N es **chico**. Si el spa cambia de horario, no queréis 800 copias.

Regla de pulgar: si un lado es 3 y el otro 500 000, el 3 **cabe dentro** del 500 000. Si ambos son 3 y 5, podéis **cruzar** arrays de ids.

!!! warning "Arrays que no paran de crecer"
    No hay un umbral universal de elementos. Importan el tamaño, el crecimiento, la frecuencia de actualización y qué parte se lee. Si el array crece sin límite, separadlo o divididlo en grupos acotados antes de acercaros al máximo del documento.

### Árboles (comarca → municipio → hotel)

Guardar ancestros permite buscar descendientes con una condición sencilla, pero mover un hotel o una rama exige actualizar esas rutas. Una referencia al padre simplifica los cambios, aunque recorrer varios niveles necesita más trabajo. Justificad qué operación es frecuente en vuestro caso.

Hijos en un array, o **ancestros** (`["Cantabria", "Trasmiera", "Laredo"]`) para preguntar “todo lo de Trasmiera” sin *join* recursivo. [Árboles en Mongo](https://www.mongodb.com/docs/manual/applications/data-models-tree-structures/). No traduzcáis el organigrama relacional *tal cual*.

## Un recetario (no un catecismo)

Mongo University parte los patrones en representación / acceso / agrupación. Aquí los agrupo por **el problema que os salta en recepción**. No hace falta recitar los veinte nombres; sí reconocer el gesto.

### El campo se multiplica (`precio_es`, `precio_uk`…)

Este es el **patrón de atributos**. Por ejemplo, `tarifas: [{canal: "web", precio: 90, moneda: "EUR"}]`. Para exigir canal web y precio menor que 100 en la misma tarifa, usad `$elemMatch`. Un índice sobre los campos del array puede ayudar, pero aumenta el coste de escritura.

En vez de una columna por país, un **array de objetos** (`sitio`, `importe`, `moneda`). Añadir Andorra es **otro elemento**, no otra clave. Se indexa y se ordena mejor.

En el hotel: tarifas por **canal** (`web`, `ota`, `recepcion`), no `tarifa_web`, `tarifa_ota`.

### Ayer el JSON no es el de hoy

El **versionado de esquema** exige lectores compatibles: si `v` falta, tratadlo como la versión antigua definida por el equipo. Primero desplegad un lector que entienda ambas versiones, después empezad a escribir la nueva y, si procede, migrad por lotes. Cambiar solo la etiqueta `v` sin transformar el contenido no es una migración correcta.

Campo `v: 2` (o `esquema`). Los documentos viejos siguen; la *app* sabe cómo leer. Evitáis la parada de “migrar toda la colección a las 03:00”. Eso **es** el criterio **d)**.

### El mismo tipo de cosa, con rarezas

El **patrón polimórfico** conserva campos comunes y un discriminador de tipo. Por ejemplo, una reserva OTA añade localizador del proveedor; una de recepción añade puesto. La validación puede aplicar reglas diferentes según el tipo. Si las operaciones y el ciclo de vida son totalmente distintos, revisad si conviene separar colecciones.

`tipo: "web" | "ota"` y un subdocumento `detalle` distinto. **Una** colección `reservas`, no tres. Consultas unificadas.

### La ficha pesa y la lista no

El **patrón de subconjunto** mantiene cerca la parte más utilizada. Antes de duplicar datos, probad una proyección: evita transferir campos innecesarios. Si aun así el volumen del documento y el conjunto de trabajo perjudican el acceso, separar contenido extenso puede ayudar. Las dos representaciones deben tener una regla de actualización.

Colección *gorda* (hotel con todos los textos legales) y una **flaca** (nombre, comarca, plazas) para el listado. Relación 1:1. Menos bytes por la red.

### No hace falta el número exacto *ahora*

Distinguid **agrupación de escrituras** y **aproximación estadística**. Acumular 100 clics y escribir el total puede ser exacto si no se pierde el acumulador; actualizar con probabilidad del 1 % y sumar 100 produce una estimación con variación. Ninguno debe aplicarse sin más a una cantidad que no puede perderse, como plazas disponibles.

Visitas a la web del hotel: el cliente **acumula** 100 clics y escribe **una** vez (o un aleatorio que dispara ~1 %). Menos escrituras; el contador **no** es de caja.

### El join os persigue

La **referencia extendida** conserva el identificador del hotel y unos pocos atributos copiados. Definid si esos atributos son históricos o deben actualizarse. Una caché o una proyección pueden ser alternativas: no hace falta duplicar toda la entidad para ahorrar una consulta.

Duplicad en la reserva lo que **siempre** pintáis (nombre del hotel). Dejad fuera lo que **cambia** (teléfono). Redundancia **consciente**.

### El informe es siempre la misma suma

El **patrón calculado** intercambia trabajo de lectura por trabajo de actualización. Puede recalcularse cada noche o mantenerse con eventos. En el primer caso hay retraso conocido; en el segundo debemos gestionar reintentos, anulaciones y fallos parciales. Conviene poder reconstruir el resumen desde los datos originales.

Una colección de resúmenes puede guardar `noches_totales` por hotel y periodo. Gerencia lee un resultado ya calculado. Debéis mantenerlo también al modificar o cancelar una reserva y evitar contar dos veces un evento reintentado. Para una ocupación diaria real hacen falta fechas y habitaciones disponibles; sumar noches reservadas no produce por sí solo un porcentaje de ocupación.

### El sensor no para (cubo)

El **patrón bucket** agrupa un número o periodo acotado de medidas. A una medida por minuto, una hora aporta hasta 60 valores por sensor. Guardad hotel, habitación, inicio de hora, suma y número de medidas; la media es `suma / n`, no se divide siempre por 60 si faltan lecturas. Definid qué ocurre con datos tardíos y evitad que un bucket crezca indefinidamente. Las colecciones de series temporales son una alternativa específica del motor.

Un documento **por hora** (o por día) con `medidas: [ … ]` y `suma` / `n`. Menos documentos, índices más flacos, fácil de **purgar** el mes viejo. Encaja con la carga de la 214.

### Uno de cada mil se sale (atípico)

El **patrón atípico** conserva el camino habitual sencillo y mueve el exceso a otra colección. La reserva debe indicar que existe continuación y cómo recuperarla. Comprobad tanto una reserva normal como una excepcional: optimizar el caso frecuente no permite perder extras del caso poco frecuente.

El 99 % de reservas tiene ≤ 6 extras. Una agencia deja 200. No hinchéis el 99 %: flag `rara: true` y el resto en `reservas_extras`. La *app* hace el segundo `find` **solo** en ese caso.

Otros nombres que veréis: **árbol** (ancestros), **preasignación** (estructura vacía de antemano; hoy Mongo gestiona mejor la RAM, menos urgente).

### Lo que no queréis hacer

Evaluad los patrones con la consulta que intentan mejorar. Cread unos datos pequeños, ejecutad la lectura y la actualización y estimad cómo crecerían en un año. No se trata de aplicar todos los patrones: cada uno introduce un coste que debe compensar el problema que resuelve.

| Mal hábito | Qué duele | Salida |
| --- | --- | --- |
| Array sin techo | Lecturas lentas, 16 MiB | Otra colección o páginas |
| Documento-baúl | Traéis 200 KB para pintar 3 campos | Colección flaca / subconjunto |
| Cien colecciones vacías | Catálogo sucio | Menos colecciones, `tipo` |
| Índice que nadie usa | Escrituras lentas | Revisar y **tirar** |
| Partir lo que se abre junto | `$lookup` en cada clic | Embeber |
| Sin versión de esquema | Migraciones a ciegas | Campo `v` |

## Un validador no es un `CREATE TABLE`

El esquema **sigue siendo dinámico**. El validador pone **barandillas**: que `noches` sea entero ≥ 1, que exista `hotel`. Si prohibís **cualquier** campo nuevo, chocáis con **d)**.

Al crear:

```javascript
db.createCollection("reservas_validacion", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      title: "Reserva del grupo",
      required: ["hotel", "noches", "importe"],
      properties: {
        hotel: { bsonType: "string" },
        canal: {
          enum: ["web", "ota", "recepcion"],
          description: "origen de la reserva",
        },
        noches: { bsonType: "int", minimum: 1, maximum: 60 },
        importe: { bsonType: ["double", "int", "long", "decimal"], minimum: 0 },
        huespedes: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["nombre"],
            properties: {
              nombre: { bsonType: "string" },
              tipo: { bsonType: "string" },
            },
          },
        },
      },
    },
  },
})
```

Podéis **combinar** `$jsonSchema` con `$expr` (p. ej. `importe` ≥ un mínimo por noche).

`validationLevel` y `validationAction` deciden qué pasa con documentos **viejos** y si el fallo **rechaza** o solo **avisa**. En Compass: pestaña *Validation*.

Colección **ya** existente:

```javascript
db.runCommand({
  collMod: "reservas_validacion",
  validationLevel: "strict",
  validationAction: "error",
})
```

En Atlas el usuario de prácticas a veces **no** puede `collMod` (hace falta rol de admin).

Ver el validador:

```javascript
db.getCollectionInfos({ name: "reservas_validacion" })[0].options.validator
db.runCommand({ listCollections: 1, filter: { name: "reservas_validacion" } })
```

Un `insertOne` que rompe el esquema devuelve `Document failed validation` y **qué** regla falló. Leedlo; no es un “error misterioso”.

### Probar el contrato, no solo crearlo

La colección `reservas_validacion` es independiente de los datos de consulta del 2.6. En el ejemplo `noches` debe ser entero; `importe` admite varios tipos numéricos. Para importes monetarios de producción, acordad una representación exacta, como céntimos enteros o `Decimal128`; los decimales binarios del fichero de aula simplifican el ejercicio.

```javascript
db.reservas_validacion.insertOne({hotel: "Laredo", noches: Int32(2), importe: 124})
// Debe rechazarse: noches no cumple el tipo entero.
db.reservas_validacion.insertOne({hotel: "Laredo", noches: "dos", importe: 124})
// Debe admitirse: el contrato permite campos adicionales.
db.reservas_validacion.insertOne({hotel: "Potes", noches: Int32(1), importe: 90, mascota: true})
```

`strict` aplica la validación a inserciones y actualizaciones; `error` rechaza operaciones inválidas. Cambiar las reglas no repara automáticamente los documentos anteriores. Para migrar una colección existente, inspeccionad los datos, preparad lectores compatibles y comprobad qué escrituras aceptará el nuevo validador.

## Compass como pizarra (no como examen)

Compass permite explorar el esquema inferido de una muestra; las opciones de diagramación dependen de la versión. Útil para **enseñar** el modelo. El RA2 se aguanta si justificáis **por qué** embebeis el huésped y **por qué** no el log de la puerta.

## Cómo se cierra el apartado

Da igual la carga y los patrones: el modelo **sigue a las historias de usuario**. Si no podéis decir “recepción abre *esto* y por eso el cobro va *aquí*”, el dibujo es decoración.

!!! success "d) en voz alta"
    “Guardo la reserva de 2024. En 2026 añado `mascota` solo a las nuevas. El teléfono del hotel no está copiado 40 000 veces. El precio cobrado sí está congelado dentro. El sensor de la 214 va por horas, no un JSON por minuto.”

## Relación con el RA2

| Criterio | Aquí |
| --- | --- |
| **d)** | Esquema que **crece**; `v`; validador que no ahoga |
| **a)** | Un `find` que responde a la ficha **sin** ocho tablas |
| **e)** | Cubos y colecciones nuevas cuando el array **ya no cabe** |

## Para practicar (Moodle manda)

1. **De un ER de hotel a documentos.** Entidades típicas: hotel, habitación, reserva, huésped, cobro, servicio (spa/parking), incidencia. La *app* muestra (a) ficha de reserva, (b) ficha de hotel con teléfono, (c) listado de incidencias de una habitación. Entregad: un JSON de ejemplo **por** colección, `insertOne`/`insertMany`, por qué embebeis o referenciáis (explicaciones fuera del JSON, que no admite comentarios), validador de `reservas` y de `hoteles`. Si Compass lo pide el profesor: captura o `.mdm`.
2. **Tarifas.** Partís de `tarifa_web`, `tarifa_ota`, `tarifa_recepcion`. Pasadlo a array de `{ canal, precio, moneda }`. Un `update` que añada `agencias`.
3. **Versión de esquema.** Las reservas viejas tienen `telefono_hotel` plano. Las nuevas, `hotel: { id, nombre }`. Campo `v`. Un `updateMany` que marque las viejas con `v: 1` y las que ya tengan objeto con `v: 2`.
4. **Cubo.** Medidas de temperatura de la 214 (un JSON por minuto, 2 horas). Rediseñad **un documento por hora** con `medidas` y `temp_media`. Explicad qué patrón es y qué ganáis al purgar.
5. **Atípico.** El 99 % tiene ≤ 5 extras. Diseñad `rara` + colección auxiliar. No hace falta implementar la *app*.
6. (Opcional) Tres patrones que **ya** usáis en `reservas` + `opiniones` del [2.6](mongodb.md) (array de huéspedes, comentarios, etiquetas). Nombradlos con vuestras palabras.

### Criterios para revisar la entrega

Cada colección debe incluir un ejemplo válido, una consulta que justifique su existencia y una explicación del crecimiento esperado. Para referencias, comprobad tipos e identificadores; para duplicaciones, explicad cómo se mantienen o por qué son históricas; para validadores, adjuntad un caso aceptado y otro rechazado.

Los ejercicios que cambian `hotel` de cadena a objeto se realizan en una colección **independiente**, por ejemplo `reservas_versionadas`. No modifiquéis la colección usada por el 2.6 y el 2.9: sus consultas presuponen `hotel` como cadena. En los buckets, usad 120 medidas conocidas y verificad que las dos horas conservan las 120, incluidas las que lleguen fuera de orden.

## Referencias

- Curso *M320 Data Modeling* (MongoDB University): la **idea** de carga → relaciones → patrones; los ejemplos de esta página son del hotel.
- “6 Rules of Thumb for MongoDB Schema Design” (blog de Mongo)
- [Schema validation](https://www.mongodb.com/docs/manual/core/schema-validation/)
- [2.6 MongoDB](mongodb.md) (oficios del *shell*) · [2.8](replicas-shards.md) (dónde viven las copias) · [2.9](pymongo.md) (`$lookup` en Python)
