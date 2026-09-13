---
title: 2.7 Modelado documental
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.7. Modelado documental

En SQL dibujáis tablas y *después* las pantallas se adaptan. En Mongo es al revés: **las pantallas mandan**. El criterio **d)** del RA2 no es “tirar JSON al cubo”. Es: **guardáis lo que hay hoy** y **dejáis hueco** para el campo de abril, sin tumbar el hotel una noche y sin reescribir 40 000 reservas.

Un documento es el sitio donde vive **lo que se lee junto**. ACID, en Mongo, es **por documento**. Si partís la reserva y el cobro en dos colecciones, o los tocáis **en el mismo** `update` o montáis una transacción en el *driver*. El atajo mental “3FN + `$lookup` en cada pantalla” suele ser señal de que seguís modelando como PostgreSQL.

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

**Meter dentro (embeber):** el cobro viaja *con* la reserva. Un `find`, un `update`. Atómico. Tope: **16 MB** por documento. `bsonSize` en el *shell* os dice cuánto ocupa el que tenéis abierto:

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

Cuidado con el techo de 16 MB si alguien embebe **PDFs**.

### Uno a muchos (hotel → reservas)

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

Millones de líneas. La habitación **no** guarda el array. Cada evento apunta a la habitación (muchos → uno). Invertís la flecha para no reventar el BSON.

```json
{ "hab": "214", "ts": "2026-04-12T22:03:00Z", "evento": "apertura" }
```

### Varios a varios (habitaciones ↔ servicios)

Spa, parking, cuna: una habitación tiene pocos servicios; un servicio (parking) toca muchas habitaciones. Tres caminos, **ninguno** es “la tabla puente de SQL” como primera opción:

1. Colección puente `hab_id` + `servicio_id`: tres lecturas. Solo si el puente **tiene vida propia** (fecha, precio extra).
2. Array de ids **en un lado** (el *pequeño*). Suele bastar. Array **en los dos** (*two-way*): coherencia a mano, fácil de romper.
3. Embeber el servicio entero en la habitación: solo si el servicio **casi no cambia** y N es **chico**. Si el spa cambia de horario, no queréis 800 copias.

Regla de pulgar: si un lado es 3 y el otro 500 000, el 3 **cabe dentro** del 500 000. Si ambos son 3 y 5, podéis **cruzar** arrays de ids.

!!! warning "Arrays que no paran de crecer"
    Cientos de hijos embebidos: mal. Miles de ids en un array: mal. Cardinalidad alta = **otra colección**, no un `[]` eterno.

### Árboles (comarca → municipio → hotel)

Hijos en un array, o **ancestros** (`["Cantabria", "Trasmiera", "Laredo"]`) para preguntar “todo lo de Trasmiera” sin *join* recursivo. [Árboles en Mongo](https://www.mongodb.com/docs/manual/applications/data-models-tree-structures/). No traduzcáis el organigrama relacional *tal cual*.

## Un recetario (no un catecismo)

Mongo University parte los patrones en representación / acceso / agrupación. Aquí los agrupo por **el problema que os salta en recepción**. No hace falta recitar los veinte nombres; sí reconocer el gesto.

### El campo se multiplica (`precio_es`, `precio_uk`…)

En vez de una columna por país, un **array de objetos** (`sitio`, `importe`, `moneda`). Añadir Andorra es **otro elemento**, no otra clave. Se indexa y se ordena mejor.

En el hotel: tarifas por **canal** (`web`, `ota`, `recepcion`), no `tarifa_web`, `tarifa_ota`.

### Ayer el JSON no es el de hoy

Campo `v: 2` (o `esquema`). Los documentos viejos siguen; la *app* sabe cómo leer. Evitáis la parada de “migrar toda la colección a las 03:00”. Eso **es** el criterio **d)**.

### El mismo tipo de cosa, con rarezas

`tipo: "web" | "ota"` y un subdocumento `detalle` distinto. **Una** colección `reservas`, no tres. Consultas unificadas.

### La ficha pesa y la lista no

Colección *gorda* (hotel con todos los textos legales) y una **flaca** (nombre, comarca, plazas) para el listado. Relación 1:1. Menos bytes por la red.

### No hace falta el número exacto *ahora*

Visitas a la web del hotel: el cliente **acumula** 100 clics y escribe **una** vez (o un aleatorio que dispara ~1 %). Menos escrituras; el contador **no** es de caja.

### El join os persigue

Duplicad en la reserva lo que **siempre** pintáis (nombre del hotel). Dejad fuera lo que **cambia** (teléfono). Redundancia **consciente**.

### El informe es siempre la misma suma

Colección `ocupacion_diaria` con `noches_totales` que **actualizáis al escribir** una reserva. Gerencia lee un documento, no agrega 8 000.

### El sensor no para (cubo)

Un documento **por hora** (o por día) con `medidas: [ … ]` y `suma` / `n`. Menos documentos, índices más flacos, fácil de **purgar** el mes viejo. Encaja con la carga de la 214.

### Uno de cada mil se sale (atípico)

El 99 % de reservas tiene ≤ 6 extras. Una agencia deja 200. No hinchéis el 99 %: flag `rara: true` y el resto en `reservas_extras`. La *app* hace el segundo `find` **solo** en ese caso.

Otros nombres que veréis: **árbol** (ancestros), **preasignación** (estructura vacía de antemano; hoy Mongo gestiona mejor la RAM, menos urgente).

### Lo que no queréis hacer

| Mal hábito | Qué duele | Salida |
| --- | --- | --- |
| Array sin techo | Lecturas lentas, 16 MB | Otra colección o páginas |
| Documento-baúl | Traéis 200 KB para pintar 3 campos | Colección flaca / subconjunto |
| Cien colecciones vacías | Catálogo sucio | Menos colecciones, `tipo` |
| Índice que nadie usa | Escrituras lentas | Revisar y **tirar** |
| Partir lo que se abre junto | `$lookup` en cada clic | Embeber |
| Sin versión de esquema | Migraciones a ciegas | Campo `v` |

## Un validador no es un `CREATE TABLE`

El esquema **sigue siendo dinámico**. El validador pone **barandillas**: que `noches` sea entero ≥ 1, que exista `hotel`. Si prohibís **cualquier** campo nuevo, chocáis con **d)**.

Al crear:

```javascript
db.createCollection("reservas", {
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
        importe: { bsonType: "double", minimum: 0 },
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
  collMod: "reservas",
  validator: { $jsonSchema: { /* … */ } },
})
```

En Atlas el usuario de prácticas a veces **no** puede `collMod` (hace falta rol de admin).

Ver el validador:

```javascript
db.getCollectionInfos({ name: "reservas" })[0].options.validator
db.runCommand({ listCollections: 1, filter: { name: "reservas" } })
```

Un `insertOne` que rompe el esquema devuelve `Document failed validation` y **qué** regla falló. Leedlo; no es un “error misterioso”.

## Compass como pizarra (no como examen)

Desde 2025 Compass **infiere** un esquema a partir de una muestra y deja dibujar colecciones, tipos e índices. Útil para **enseñar** el modelo. El RA2 se aguanta si justificáis **por qué** embebeis el huésped y **por qué** no el log de la puerta.

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

1. **De un ER de hotel a documentos.** Entidades típicas: hotel, habitación, reserva, huésped, cobro, servicio (spa/parking), incidencia. La *app* muestra (a) ficha de reserva, (b) ficha de hotel con teléfono, (c) listado de incidencias de una habitación. Entregad: un JSON de ejemplo **por** colección, `insertOne`/`insertMany`, por qué embebeis o referenciáis (comentarios en el JSON), validador de `reservas` y de `hoteles`. Si Compass lo pide el profesor: captura o `.mdm`.
2. **Tarifas.** Partís de `tarifa_web`, `tarifa_ota`, `tarifa_recepcion`. Pasadlo a array de `{ canal, precio, moneda }`. Un `update` que añada `agencias`.
3. **Versión de esquema.** Las reservas viejas tienen `telefono_hotel` plano. Las nuevas, `hotel: { id, nombre }`. Campo `v`. Un `updateMany` que marque las viejas con `v: 1` y las que ya tengan objeto con `v: 2`.
4. **Cubo.** Medidas de temperatura de la 214 (un JSON por minuto, 2 horas). Rediseñad **un documento por hora** con `medidas` y `temp_media`. Explicad qué patrón es y qué ganáis al purgar.
5. **Atípico.** El 99 % tiene ≤ 5 extras. Diseñad `rara` + colección auxiliar. No hace falta implementar la *app*.
6. (Opcional) Tres patrones que **ya** usáis en `reservas` + `opiniones` del [2.6](mongodb.md) (array de huéspedes, comentarios, etiquetas). Nombradlos con vuestras palabras.

## Referencias

- Curso *M320 Data Modeling* (MongoDB University): la **idea** de carga → relaciones → patrones; los ejemplos de esta página son del hotel.
- “6 Rules of Thumb for MongoDB Schema Design” (blog de Mongo)
- [Schema validation](https://www.mongodb.com/docs/manual/core/schema-validation/)
- [2.6 MongoDB](mongodb.md) (oficios del *shell*) · [2.8](replicas-shards.md) (dónde viven las copias) · [2.9](pymongo.md) (`$lookup` en Python)
