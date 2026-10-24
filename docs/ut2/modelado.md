---
title: 2.7 Modelado documental
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.7. Modelado documental

!!! info "Ruta de estudio"
    **Esencial:** decidir qué embeber y qué referenciar, limitar el crecimiento y definir reglas de validación y evolución del esquema.

    **Práctica guiada:** usar `hotel_modelado` para comprobar referencias, atributos, versiones, agrupación de medidas y un validador. No se modifican los originales de 2.6 y 2.9.

    **Ampliación:** diseñar el caso completo, probar datos tardíos y estudiar otros patrones. Las condiciones de entrega se concretan en Moodle.

En [2.6](mongodb.md) aprendimos a consultar y cambiar documentos. Ahora decidimos **cómo organizarlos para las operaciones del hotel**. Una reserva puede guardar huéspedes dentro, referenciar el hotel y conservar una copia del nombre o precio acordado. Cada decisión tiene consecuencias cuando leemos, actualizamos o conservamos el histórico.

Tanto en SQL como en MongoDB partimos de datos, consultas y reglas de negocio. Una escritura en un documento es atómica; modificar varios documentos como una unidad requiere una transacción explícita en una topología compatible. El servidor independiente de 2.6 permite esta práctica, pero no transacciones multidocumento.

El criterio **d)** del RA2 implica conservar información que pueda utilizarse después. Eso requiere metadatos, lectores y reglas de evolución; un esquema flexible no garantiza cambios sin migración ni interrupción. La capacidad disponible también tiene límites.

Embeber y duplicar algunos atributos puede evitar lecturas adicionales, pero no garantiza una consulta más rápida. Referenciar y usar `$lookup` también son decisiones válidas. **Medimos el tamaño, la frecuencia de acceso y el coste de mantener la coherencia**, en lugar de trasladar o rechazar automáticamente un modelo relacional.

## Empieza por las preguntas, no por las entidades

Antes de Compass, escribid **qué hace** cada rol. Tres ejemplos del grupo:

| Quién | Qué abre | Qué necesita ver *ya* |
| --- | --- | --- |
| Recepción | Ficha de una reserva | Hotel, noches, huéspedes, cobro |
| Gerencia | Resumen de reservas de Laredo | Noches e importes de reservas; la ocupación real exige además fechas, habitaciones y disponibilidad |
| Mantenimiento | Incidencias de la 214 | Historial largo (años), no la ficha de reserva |

Luego medid, aunque sea a groso modo:

- ¿Más **lecturas** o más **escrituras**?
- ¿Cuántas veces por minuto? ¿Qué latencia aguanta el mostrador?
- ¿Qué campos entran en el filtro (`hotel`, `checkin`, `comarca`)?
- ¿Hay algo que **cambia** (teléfono del hotel) y algo que **debe quedar congelado** (precio acordado de la reserva)?

Empezad con el diseño más sencillo que cumpla las operaciones y garantías. Que un documento quepa hoy no basta: estimad cuánto crecerá, quién lo actualizará y qué información se necesita junta. Una proyección o un índice pueden resolver un problema sin duplicar datos ni introducir otra colección.

### Carga de aula: no es el sensor de un MOOC

Imaginad 12 hoteles, 800 habitaciones y un sensor de puerta/temperatura por habitación. Cada minuto llega una medida. Gerencia, cada hora, quiere un resumen. Ciencia de datos, de vez en cuando, el minuto a minuto de un invierno.

| Actor | Gestos | Ritmo (orden) | Lectura o escritura | Nota de modelado |
| --- | --- | --- | --- | --- |
| Sensores del grupo | Hotel, habitación, sensor, instante y medida | 800/min si llegan todas las medidas | Escritura | Comparar documentos individuales, buckets acotados o una colección de series temporales |
| Proceso de gerencia | Leer medidas y actualizar el resumen | 1 ejecución/hora | Lectura y escritura | Conservar suma, recuento y periodo del resumen |
| Analista | Tendencia de un mes | Pocas, *scan* | Lectura | Puede ir a un secundario ([2.8](replicas-shards.md)) |

Con esas hipótesis llegan **48 000 medidas por hora** al grupo y **60 por hora y sensor**. El número permite estimar crecimiento, pero no obliga a agrupar manualmente. Compararemos alternativas. La práctica utiliza solo un sensor, durante dos horas, para comprobar exactamente qué se conserva. Un evento de puerta no demuestra disponibilidad comercial de una habitación.

## Solo hay dos gestos: meter dentro o señalar fuera

Decidid con cuatro preguntas: ¿se lee junto?, ¿cambia junto?, ¿crece de forma acotada?, ¿necesita una actualización atómica? Embeber favorece la lectura conjunta y la atomicidad de un documento. Referenciar evita repetir entidades compartidas y permite que cada una tenga su propio ciclo de vida.

Duplicar un nombre puede representar una **instantánea histórica** o una copia del nombre actual. En el primer caso no debemos actualizarlo si cambia el hotel; en el segundo necesitamos una estrategia para mantenerlo sincronizado. La duplicación solo está bien definida cuando explicitamos esa diferencia.

**Meter dentro (embeber):** una ficha pequeña de llegada puede viajar con la reserva. Su actualización conjunta cabe en una operación atómica de un documento. Si hablamos de cobros, primero debemos modelar pagos parciales y devoluciones, no asumir que existe uno solo.

El límite de un documento BSON es **16 MiB**. Con los datos preparados en la práctica guiada, esta agregación mide el documento de ejemplo:

```javascript
db.reservas_referencias.aggregate([
  {$match: {_id: "R27-1"}},
  {$project: {bytes: {$bsonSize: "$$ROOT"}}}
])
```

El resultado es el tamaño BSON, no el espacio total con índices y réplicas ni una predicción de rendimiento. Estimad también el crecimiento futuro.

Para archivos grandes, estudiad almacenamiento de objetos, GridFS o un sistema de ficheros como HDFS según el uso. La ficha puede conservar identificador, ubicación y metadatos. GridFS divide archivos en fragmentos; no elimina los límites ni hace atómica toda modificación de un archivo.

**Señalar fuera (referencia):** `id_hotel` en la reserva. Segunda lectura o `$lookup`. Bien cuando el hotel **cambia** el teléfono y no queréis tocar 40 000 copias.

La **referencia manual** guarda el identificador con el mismo tipo que el documento referenciado. El preparador de la práctica crea un hotel con `_id` ObjectId y una reserva `R27-1` con `hotel_id` apuntando a él. No ejecutéis una segunda inserción de esos ejemplos.

En `hotel_modelado`:

```javascript
db.reservas_referencias.aggregate([
  {$match: {_id: "R27-1"}},
  {$lookup: {
    from: "hoteles",
    localField: "hotel_id",
    foreignField: "_id",
    as: "hotel_actual"
  }}
])
```

`hotel_actual` es un **array** con las coincidencias; en este caso debe contener un hotel. Si no hay referencia válida, puede quedar vacío. MongoDB no crea una clave foránea ni borra referencias automáticamente. Una cadena con los caracteres de un ObjectId no es ese ObjectId.

Si la pantalla necesita el nombre histórico, podemos conservarlo en la reserva; si necesita el teléfono actual, consultamos `hoteles`. Un `$lookup` frecuente no demuestra por sí solo un mal diseño: comparad consulta, índices, duplicación y coste de actualización.

En documentación antigua aparecen **DBRef** (`$ref`, `$id`, `$db`). Para esta práctica bastan referencias manuales; resolver y mantener las relaciones sigue siendo responsabilidad del diseño.

## Cardinalidad: el hotel en cuatro tamaños

No memoricéis “1:N = array”. Preguntad **cuántos** y **si se leen siempre juntos**.

### Uno a uno (ficha y dirección de envío)

La cardinalidad 1:1 no obliga a embeber. Si los datos de llegada son pequeños y aparecen en la ficha de reserva, resulta cómodo. Si un documento médico u otra información con acceso separado tuviera un ciclo de vida distinto, la referencia podría ser más adecuada. El criterio es la operación, no solo el dibujo de la relación.

En nuestro ejemplo, recepción suele abrir la reserva junto con los datos breves de llegada; por eso proponemos embeberlos.

```json
{
  "hotel": "Potes",
  "noches": 2,
  "llegada": { "hora": "16:00", "matricula": "1234-ABC" }
}
```

Separarlos puede convenir si tienen permisos, tamaño o ciclos de actualización diferentes. Si deben cambiar juntos, comparad embeber con una transacción multidocumento: la atomicidad necesaria es un criterio más, no una orden de embeber cualquier contenido.

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

**Precio acordado:** conserva las condiciones de esa reserva aunque cambie el catálogo. Un cambio de tarifa no reescribe automáticamente el histórico. Esto no equivale a afirmar que ese importe se haya cobrado; pagos, devoluciones y rectificaciones requieren sus propios datos y reglas.

**Nombre del hotel en la ficha:** si recepción lo consulta con frecuencia, valorad copiar `nombre` + `comarca` en la reserva (*referencia extendida*), comparando el coste de consulta y de mantener esa copia. Definid si conserva el dato histórico o el actual. En este ejemplo, el teléfono actual se consulta en `hoteles`.

### Uno a tropecientos (habitación → logs de puerta)

Cada evento debe identificar inequívocamente habitación **y hotel**: la habitación 214 puede existir en varias sedes. Además se registra el instante y el tipo de evento. Para consultar un periodo, el índice debe seguir esa combinación; guardar eventos en otra colección sin diseñar el acceso solo desplaza el problema.

Millones de líneas. La habitación **no** guarda el array. Cada evento apunta a la habitación (muchos → uno). Invertís la flecha para no reventar el BSON.

Ejemplo en `mongosh` (la fecha se guarda como BSON Date):

```javascript
({hotel: "Laredo", hab: "214", sensor: "puerta-01",
  ts: ISODate("2026-04-12T22:03:00Z"), evento: "apertura"})
```

La práctica siguiente mide temperatura; no confunde ese dato con un evento de puerta.

### Varios a varios (habitaciones ↔ servicios)

Una colección de asociaciones es válida también en MongoDB. Resulta útil cuando la relación tiene atributos propios, como vigencia, precio contratado o disponibilidad. No implica necesariamente tres viajes a la base: una agregación puede reunir resultados. Comparad frecuencia de lectura y coste de mantener referencias duplicadas antes de elegir.

Spa, parking y cuna pueden relacionarse con muchas habitaciones. Hay varias opciones:

1. **Colección de asociaciones** con habitación y servicio, especialmente si la relación tiene vigencia, precio o atributos propios. Una consulta o agregación puede reunir lo necesario.
2. **Array de identificadores en un lado**, si su crecimiento está acotado. Mantenerlo en ambos lados exige coordinar las dos representaciones.
3. **Contenido embebido**, si los atributos son pequeños y poco cambiantes o representan una instantánea histórica.

Contar elementos ayuda, pero no decide por sí solo: tres objetos muy grandes pueden pesar más que muchos identificadores. La actualización del horario de un spa no debería requerir corregir copias sin una política definida.

!!! warning "Arrays que no paran de crecer"
    No hay un umbral universal de elementos. Importan el tamaño, el crecimiento, la frecuencia de actualización y qué parte se lee. Si el array crece sin límite, separadlo o divididlo en grupos acotados antes de acercaros al máximo del documento.

### Árboles (comarca → municipio → hotel)

Guardar ancestros permite buscar descendientes con una condición sencilla, pero mover un hotel o una rama exige actualizar esas rutas. Una referencia al padre simplifica los cambios, aunque recorrer varios niveles necesita más trabajo. Justificad qué operación es frecuente en vuestro caso.

Hijos en un array, o **ancestros** (`["Cantabria", "Trasmiera", "Laredo"]`) para preguntar “todo lo de Trasmiera” sin *join* recursivo. [Árboles en Mongo](https://www.mongodb.com/docs/manual/applications/data-models-tree-structures/). No traduzcáis el organigrama relacional *tal cual*.

## Un recetario (no un catecismo)

Mongo University parte los patrones en representación / acceso / agrupación. Aquí los agrupo por **el problema que os salta en recepción**. No hace falta recitar los veinte nombres; sí reconocer el gesto.

### El campo se multiplica (`precio_es`, `precio_uk`…)

Este es el **patrón de atributos**. Por ejemplo, `tarifas: [{canal: "web", precio: 90, moneda: "EUR"}]`. Para exigir canal web y precio menor que 100 en la misma tarifa, usad `$elemMatch`. Un índice sobre los campos del array puede ayudar, pero aumenta el coste de escritura.

En vez de una columna por país, un **array de objetos** (`sitio`, `importe`, `moneda`). Añadir Andorra es **otro elemento**, no otra clave. Puede facilitar índices y consultas comunes, pero hay que comprobar el plan y el coste de actualizar arrays.

En el hotel: tarifas por **canal** (`web`, `ota`, `recepcion`), no `tarifa_web`, `tarifa_ota`.

### Ayer el JSON no es el de hoy

El **versionado de esquema** exige lectores compatibles: si `v` falta, tratadlo como la versión antigua definida por el equipo. Primero desplegad un lector que entienda ambas versiones, después empezad a escribir la nueva y, si procede, migrad por lotes. Cambiar solo la etiqueta `v` sin transformar el contenido no es una migración correcta.

Un campo `v` identifica el contrato. Los documentos antiguos pueden permanecer mientras los lectores los entiendan. Esto permite planificar una transición gradual, pero no garantiza por sí solo cero interrupciones: consultas, índices, validadores y programas deben ser compatibles. La práctica distingue **clasificar versiones** de **transformar su contenido**.

### El mismo tipo de cosa, con rarezas

El **patrón polimórfico** conserva campos comunes y un discriminador de tipo. Por ejemplo, una reserva OTA añade localizador del proveedor; una de recepción añade puesto. La validación puede aplicar reglas diferentes según el tipo. Si las operaciones y el ciclo de vida son totalmente distintos, revisad si conviene separar colecciones.

Si comparten consultas y ciclo de vida, una colección `reservas` con un discriminador y un `detalle` variable permite consultas comunes. Si esas condiciones no se cumplen, separar colecciones puede estar justificado.

### La ficha pesa y la lista no

El **patrón de subconjunto** mantiene cerca la parte más utilizada. Antes de duplicar datos, probad una proyección: evita transferir campos innecesarios. Si aun así el volumen del documento y el conjunto de trabajo perjudican el acceso, separar contenido extenso puede ayudar. Las dos representaciones deben tener una regla de actualización.

Colección *gorda* (hotel con todos los textos legales) y una **flaca** (nombre, comarca, plazas) para el listado. Relación 1:1. Menos bytes por la red.

### No hace falta el número exacto *ahora*

Distinguid **agrupación de escrituras** y **aproximación estadística**. Acumular 100 clics y escribir el total puede ser exacto si no se pierde el acumulador; actualizar con probabilidad del 1 % y sumar 100 produce una estimación con variación. Ninguno debe aplicarse sin más a una cantidad que no puede perderse, como plazas disponibles.

Visitas a la web del hotel: el cliente **acumula** 100 clics y escribe **una** vez (o un aleatorio que dispara ~1 %). Menos escrituras; el contador **no** es de caja.

### El join os persigue

La **referencia extendida** conserva el identificador del hotel y unos pocos atributos copiados. Definid si esos atributos son históricos o deben actualizarse. Una caché o una proyección pueden ser alternativas: no hace falta duplicar toda la entidad para ahorrar una consulta.

Consultar frecuentemente el nombre del hotel puede justificar estudiar una copia, pero no obliga a duplicarlo. Comparad la referencia con una copia histórica o una copia actualizada, indicando cómo se mantiene. En este ejemplo dejamos el teléfono actual en el hotel y conservamos en la reserva el nombre histórico acordado.

### El informe es siempre la misma suma

El **patrón calculado** intercambia trabajo de lectura por trabajo de actualización. Puede recalcularse cada noche o mantenerse con eventos. En el primer caso hay retraso conocido; en el segundo debemos gestionar reintentos, anulaciones y fallos parciales. Conviene poder reconstruir el resumen desde los datos originales.

Una colección de resúmenes puede guardar `noches_totales` por hotel y periodo. Gerencia lee un resultado ya calculado. Debéis mantenerlo también al modificar o cancelar una reserva y evitar contar dos veces un evento reintentado. Para una ocupación diaria real hacen falta fechas y habitaciones disponibles; sumar noches reservadas no produce por sí solo un porcentaje de ocupación.

### El sensor no para (cubo)

El **patrón bucket** agrupa un número o periodo acotado de medidas. A una medida por minuto, una hora aporta hasta 60 valores por sensor. Guardad hotel, habitación, inicio de hora, suma y número de medidas; la media es `suma / n`, no se divide siempre por 60 si faltan lecturas. Definid qué ocurre con datos tardíos y evitad que un bucket crezca indefinidamente. Las colecciones de series temporales son una alternativa específica del motor.

Un documento **por hora** (o por día) con `medidas: [ … ]` y `suma` / `n`. Menos documentos, índices más flacos, fácil de **purgar** el mes viejo. Encaja con la carga de la 214.

### Uno de cada mil se sale (atípico)

El **patrón atípico** conserva el camino habitual sencillo y mueve el exceso a otra colección. La reserva debe indicar que existe continuación y cómo recuperarla. Comprobad tanto una reserva normal como una excepcional: optimizar el caso frecuente no permite perder extras del caso poco frecuente.

El 99 % de reservas tiene ≤ 6 extras. Una agencia deja 200. Podemos guardar hasta **6** extras en la reserva y el resto en `reservas_extras`, enlazados por el identificador de reserva. El indicador `rara` avisa de la continuación. Es un límite didáctico, no una restricción de MongoDB; una reserva excepcional con 200 extras conservaría 6 dentro y 194 fuera.

Otros nombres que veréis: **árbol** (ancestros) y **preasignación** (reservar una estructura de antemano). Su utilidad depende de la carga y del motor; no se aplican solo por aparecer en un catálogo de patrones.

### Lo que no queréis hacer

Evaluad los patrones con la consulta que intentan mejorar. Cread unos datos pequeños, ejecutad la lectura y la actualización y estimad cómo crecerían en un año. No se trata de aplicar todos los patrones: cada uno introduce un coste que debe compensar el problema que resuelve.

| Mal hábito | Qué duele | Salida |
| --- | --- | --- |
| Array sin techo | Lecturas lentas, 16 MiB | Otra colección o páginas |
| Documento grande para una lista pequeña | Transferencia o conjunto de trabajo excesivo | Proyección primero; estudiar subconjunto si sigue siendo necesario |
| Colecciones sin una razón de acceso o gestión | Mantenimiento innecesario | Revisar el propósito y los límites de cada colección |
| Índice sin uso demostrado | Coste de escritura y almacenamiento | Revisar uso y restricciones antes de retirarlo |
| Lecturas adicionales costosas | Latencia o trabajo repetido | Comparar índices, referencias, caché o datos embebidos |
| Sin versión de esquema | Migraciones a ciegas | Campo `v` |

## Un validador no es un `CREATE TABLE`

El validador expresa un contrato: campos obligatorios, tipos y límites. Un esquema abierto facilita nuevos campos; un esquema cerrado también puede ser apropiado si se evoluciona de forma controlada. **El criterio d) no obliga a aceptar campos desconocidos ni datos inválidos**. Lo importante es conservar información utilizable y planificar sus cambios.

Al crear una colección nueva en `hotel_modelado`, este contrato exige hotel, noches e importe. `canal` es opcional, pero si aparece debe ser uno de los valores indicados. Las noches entre 1 y 60 son una **regla del ejercicio**, no un límite universal del alojamiento. Los campos adicionales se permiten en este ejemplo:


```javascript
db.createCollection("reservas_validacion", {
  validationLevel: "strict",
  validationAction: "error",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      title: "Reserva del grupo",
      required: ["hotel", "noches", "importe"],
      properties: {
        hotel: { bsonType: "string", minLength: 1 },
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
              nombre: { bsonType: "string", minLength: 1 },
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

Colección **ya existente**: este comando ajusta el nivel y la acción del validador existente; **no crea uno ni cambia sus reglas**. Para sustituir el contrato se debe proporcionar también `validator`:

```javascript
db.runCommand({
  collMod: "reservas_validacion",
  validationLevel: "strict",
  validationAction: "error",
})
```

`collMod` requiere el privilegio correspondiente sobre la base. Un usuario de prácticas puede no tenerlo: solicitad al profesor un entorno con los permisos necesarios; no necesita por definición ser administrador de todo el servidor.

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

`strict` comprueba las inserciones y las actualizaciones sujetas a validación; `error` rechaza las que no cumplen. `moderate` permite actualizar documentos preexistentes que ya eran inválidos sin exigirles el contrato, por lo que no equivale a una limpieza. `warn` permite la escritura y registra el incumplimiento. Cambiar las reglas no recorre, repara ni elimina automáticamente los documentos anteriores. Para migrar una colección existente, inspeccionad los datos, preparad lectores compatibles y comprobad qué escrituras aceptará el nuevo validador.

## Compass como pizarra (no como examen)

Compass permite explorar el esquema inferido de una muestra; las opciones de diagramación dependen de la versión. Útil para **enseñar** el modelo. El RA2 se aguanta si justificáis **por qué** embebeis el huésped y **por qué** no el log de la puerta.

## Cómo se cierra el apartado

El modelo **parte de las historias de usuario** y se ajusta a la carga, los patrones de acceso, el crecimiento y las garantías necesarias. Si no podéis decir “recepción abre *esto* y por eso el cobro va *aquí*”, el dibujo es decoración.

!!! success "d) en voz alta"
    “Conservo los datos y su significado. Agrupo lo que conviene leer y cambiar junto, referencio lo compartido y limito el crecimiento. Si el esquema cambia, adapto lectores y validación. Compruebo que el rediseño no pierde información.”

## Relación con el RA2

| Criterio | Aquí |
| --- | --- |
| **d)** | Conservar y reutilizar información mediante contratos, versiones y lectores compatibles |
| **a)** | Justificar la organización según consultas, datos y costes; contrastar los resultados |
| Conexión con **e)** | Preparar un modelo que pueda crecer; añadir una colección o un bucket no demuestra añadir recursos al sistema |

## Práctica guiada: comprobar el rediseño

### Preparar un entorno independiente

Utilizad el servidor de MongoDB 7 del [2.6](mongodb.md). Este apartado usa **otra base, `hotel_modelado`**: no importéis ni modifiquéis `hotel.reservas` o `hotel.opiniones`. Los ejemplos de JSON anteriores ilustran decisiones; el conjunto ejecutable se prepara con el archivo siguiente.

Descargad [preparar_modelado.js](../assets/practicas/hotel-modelado/preparar_modelado.js). Desde la raíz del repositorio, en la **terminal del PC**:

```text
docker cp docs/assets/practicas/hotel-modelado/preparar_modelado.js hotel-mongo:/tmp/preparar_modelado.js
docker exec hotel-mongo mongosh hotel_modelado --quiet --file /tmp/preparar_modelado.js
docker exec -it hotel-mongo mongosh hotel_modelado
```

Con `mongosh` instalado en el PC, la alternativa es:

```text
mongosh "mongodb://127.0.0.1:27017/hotel_modelado" --quiet --file docs/assets/practicas/hotel-modelado/preparar_modelado.js
mongosh "mongodb://127.0.0.1:27017/hotel_modelado"
```

Si descargáis el archivo suelto, ajustad su ruta. Para un servidor compartido, el docente debe asignar un entorno aislado; el preparador exige expresamente `hotel_modelado` y no debe lanzarse en la base común del grupo. Atlas requiere además los permisos y la conexión correspondientes.

El preparador comprueba primero que sus cinco colecciones no existan. **No las sobrescribe**: repetirlo termina con un aviso. Si la carga se interrumpe, revisad qué quedó antes de reintentar. Guardad el trabajo previo antes de preparar una nueva ejecución; no borréis otras bases para repetir esta práctica.

| Colección | Contenido inicial |
| --- | --- |
| `hoteles` | Un hotel Laredo con ObjectId conocido |
| `reservas_referencias` | Una reserva que referencia ese hotel y conserva su nombre histórico |
| `tarifas` | Tres tarifas planas: web 90, OTA 110 y recepción 100, en EUR |
| `reservas_versionadas` | Dos reservas: hotel en cadena con teléfono plano, y hotel como objeto |
| `medidas` | 120 medidas del sensor `temp-01`, habitación 214 de Laredo, en dos horas UTC |

En `mongosh`, confirmad `db.getName()` y los recuentos. Los siguientes comandos pertenecen a **esa consola**, no a PowerShell.

### 1. Referenciar sin perder el significado

Ejecutad el `$lookup` de «Meter dentro o señalar fuera». Para `R27-1` debe devolver un único elemento en `hotel_actual`, con nombre Laredo y teléfono `942 60 00 00`. El campo `hotel_nombre_historico` conserva el nombre acordado en la ficha; la referencia permite obtener los datos actuales.

Medid su tamaño con `$bsonSize` y explicad por qué ni el tamaño ni la existencia de una referencia prueban que la consulta será rápida con cualquier volumen. Comprobad también que `hotel_id` y `_id` son ambos ObjectId.

### 2. Convertir tarifas en atributos

Primero consultad `T27-1` y anotad sus tres importes. Después, **una sola vez**, transformad el contenido usando una actualización con pipeline:

```javascript
db.tarifas.updateOne(
  {_id: "T27-1", tarifa_web: {$exists: true}},
  [
    {$set: {tarifas: [
      {canal: "web", precio: "$tarifa_web", moneda: "$moneda"},
      {canal: "ota", precio: "$tarifa_ota", moneda: "$moneda"},
      {canal: "recepcion", precio: "$tarifa_recepcion", moneda: "$moneda"}
    ]}},
    {$unset: ["tarifa_web", "tarifa_ota", "tarifa_recepcion", "moneda"]}
  ]
)
db.tarifas.updateOne(
  {_id: "T27-1", "tarifas.canal": {$ne: "agencias"}},
  {$push: {tarifas: {canal: "agencias", precio: 95, moneda: "EUR"}}}
)
db.tarifas.find({
  tarifas: {$elemMatch: {canal: "web", precio: {$lt: 100}, moneda: "EUR"}}
})
```

Debéis conservar 90, 110 y 100 y añadir agencias a 95. El filtro de la primera actualización evita reconstruir el array desde campos ya eliminados al repetirla. El segundo evita añadir otra tarifa de agencias en esta secuencia de aula; no sustituye a diseñar restricciones y concurrencia en una aplicación.

### 3. Etiquetar versiones y después migrar

Los dos documentos contienen información equivalente organizada de manera distinta. Empezamos **clasificando** su estructura conocida:

```javascript
db.reservas_versionadas.updateMany(
  {hotel: {$type: "string"}, telefono_hotel: {$type: "string"}, v: {$exists: false}},
  {$set: {v: Int32(1)}}
)
db.reservas_versionadas.updateMany(
  {hotel: {$type: "object"}, "hotel.id": {$type: "objectId"}, v: {$exists: false}},
  {$set: {v: Int32(2)}}
)
db.reservas_versionadas.find({
  $or: [{hotel: "Laredo"}, {"hotel.nombre": "Laredo"}]
})
```

La consulta compatible devuelve **dos reservas**. Etiquetar no ha trasladado ni eliminado campos. Una estructura inesperada no debería recibir una versión sin inspección.

Ahora migramos la reserva antigua, conservando nombre, teléfono, noches e importe:

```javascript
db.reservas_versionadas.updateOne(
  {_id: "V27-1", v: Int32(1)},
  [
    {$set: {
      hotel: {
        id: ObjectId("000000000000000000000027"),
        nombre: "$hotel",
        telefono: "$telefono_hotel"
      },
      v: Int32(2)
    }},
    {$unset: "telefono_hotel"}
  ]
)
db.reservas_versionadas.find({"hotel.nombre": "Laredo", v: 2})
```

Deben seguir existiendo dos reservas, ahora en versión 2. El teléfono de este ejercicio es una **instantánea del documento**, no una promesa de sincronización con el hotel actual. El identificador se conoce porque el conjunto solo contiene Laredo; en una migración real habría que resolver cada referencia y tratar las que no se encuentran.

### 4. Agrupar 120 medidas sin perderlas

El preparador genera medidas del **12 de abril de 2026**, desde las 08:00 hasta las 09:59 UTC, una por minuto. Las inserta en orden inverso para que el cálculo no dependa del orden de llegada. Cada medida tiene un `_id` estable.

| Hora UTC | Medidas | Suma de temperaturas | Media |
| --- | --- | --- | --- |
| 08:00–09:00 | 60 | 1470 | 24,5 °C |
| 09:00–10:00 | 60 | 1590 | 26,5 °C |

Agrupad por hotel, habitación, sensor e inicio de hora:

```javascript
db.medidas.aggregate([
  {$sort: {ts: 1, _id: 1}},
  {$group: {
    _id: {
      hotel: "$hotel", hab: "$hab", sensor: "$sensor",
      hora: {$dateTrunc: {date: "$ts", unit: "hour", timezone: "UTC"}}
    },
    medidas: {$push: {id: "$_id", ts: "$ts", temp_c: "$temp_c"}},
    suma: {$sum: "$temp_c"},
    n: {$sum: 1}
  }},
  {$set: {temp_media: {$divide: ["$suma", "$n"]}}},
  {$out: "medidas_hora"}
])
db.medidas_hora.find().sort({"_id.hora": 1})
```

`$out` crea o **reemplaza solo `medidas_hora`** en la base actual. Las medidas originales se conservan. Reejecutar este cálculo sobre las mismas 120 medidas reconstruye dos buckets; no añade otros dos. En producción, coordinar lectores y actualizaciones del resumen requiere un procedimiento adicional.

La suma 1470 no es una temperatura ambiental; es un acumulador para calcular la media de lecturas igualmente espaciadas. Comprobad **los 120 identificadores**, no solo los recuentos y las medias: una repetición y una omisión podrían compensarse. Si faltan medidas se divide por las recibidas, sin afirmar que representan todos los minutos; si se necesita una media temporal con intervalos irregulares, habrá que definir ponderaciones.

Para comprobar la conservación podéis usar [comprobar_buckets.js](../assets/practicas/hotel-modelado/comprobar_buckets.js), de **solo lectura**. Revisa cada identificador, instante y temperatura, además de sumas y medias. Se utiliza con los 120 datos originales, antes de las ampliaciones:

```text
docker cp docs/assets/practicas/hotel-modelado/comprobar_buckets.js hotel-mongo:/tmp/comprobar_buckets.js
docker exec hotel-mongo mongosh hotel_modelado --quiet --file /tmp/comprobar_buckets.js
```

Con `mongosh` en el PC:

```text
mongosh "mongodb://127.0.0.1:27017/hotel_modelado" --quiet --file docs/assets/practicas/hotel-modelado/comprobar_buckets.js
```

Ante un error, revisad la entrada, la clave de agrupación y el cálculo. No ajustéis las sumas esperadas para ocultar la pérdida de una medida. El comprobador está pensado para el conjunto pequeño de aula; no es una prueba de rendimiento.

### 5. Crear y probar el validador

En `hotel_modelado`, ejecutad el bloque de creación de `reservas_validacion` de este apartado. Si ya existe, no repitáis la creación como si modificara sus reglas: inspeccionadla y utilizad `collMod` con un contrato explícito si procede.

Probad **uno a uno** los tres `insertOne` del apartado «Probar el contrato». El segundo debe fallar; continuad con el tercero después de interpretar el error. Si los guardáis en un script sin capturar la excepción, el error interrumpe su ejecución y no se inserta el tercero.

Tras ejecutar una vez los casos válidos debe haber **dos documentos**. Añadid pruebas rechazadas por `noches: Int32(0)`, `importe: -1` y un huésped sin `nombre`; ninguna debe aumentar el recuento. No uséis la existencia de una colección como evidencia de que el contrato funciona: mostrad las operaciones aceptadas y rechazadas.

## Actividades

Entregad las decisiones con ejemplos y resultados, no solo el dibujo. Las actividades 1–6 consolidan el recorrido; las restantes permiten profundizar.

1. **Del ER a los documentos.** Diseñad hotel, habitación, reserva, huésped, cobro, servicio e incidencia para tres consultas: ficha de reserva, teléfono actual del hotel e incidencias de una habitación. Indicad qué embebéis, qué referenciáis, crecimiento esperado y una consulta por colección. Separad precio acordado de pagos efectuados. Un JSON por colección, sin comentarios dentro, basta para representar el diseño; explicaciones aparte.
2. **Referencias e historia.** Sobre una copia de los ejemplos, cambiad nombre y teléfono del hotel. Comprobad qué cambia en el `$lookup` y qué conserva la reserva. Sustituid temporalmente la referencia por una cadena del mismo aspecto y explicad el resultado vacío. No confundáis ese error de tipo con ausencia de datos en el hotel.
3. **Tarifas.** Realizad el rediseño guiado, comprobad las cuatro tarifas y explicad `$elemMatch`. Preparad un contraejemplo con web a 110 y OTA a 90: dos rutas independientes podrían seleccionar la ficha aunque web no cueste menos de 100. Proponed cómo evitar dos tarifas del mismo canal en una aplicación.
4. **Versionado.** Guardad evidencia de la reserva antigua, del etiquetado y de la migración. Deben conservarse 2 reservas, sus noches (2 y 3), importes (124 y 186,5) y teléfonos. Explicad qué lectores e índices revisaríais antes de cambiar la escritura de producción.
5. **Buckets.** Ejecutad la agrupación y contrastad horas, identificadores, sumas y medias con el origen. Repetid el cálculo para demostrar que no duplica buckets. Explicad qué ocurre si se divide por 60 cuando solo se recibieron 59 lecturas.
6. **Contrato.** Mostrad los casos válidos e inválidos de `reservas_validacion`. Diseñad además un validador para `hoteles` que requiera nombre y un teléfono de tipo cadena. Justificad si admite campos adicionales. Si decidís cerrarlo, incluid `_id` entre los campos permitidos y planificad cómo evolucionarlo.
7. **Datos tardíos — ampliación.** Trabajad sobre una copia de `medidas` y una salida distinta. Añadid una medida nueva a las 09:30:30 UTC con 30 °C e identificador propio. Deben resultar 61 medidas, suma 1620 y media `1620/61` para esa hora. Reintentad la inserción con el mismo `_id`: el rechazo de duplicado evita añadirla otra vez, pero la aplicación debe decidir cómo tratar ese reintento. Conservad el conjunto original de 120 para las comprobaciones comunes.
8. **Caso atípico.** Diseñad una reserva normal y otra con 200 extras: límite didáctico de 6 dentro y 194 fuera. Indicad la referencia de continuación y cómo recuperar todos sin duplicarlos. Explicad qué pasa si falla una de las dos escrituras.
9. **Subconjunto y proyección.** Comparad una proyección de hotel con una colección de resúmenes. Explicad qué información se duplica, cuándo se actualiza y cómo se reconstruye. No deduzcáis que menos campos devueltos significa menos documentos examinados.
10. **Revisión del modelo de 2.6.** Identificad tres decisiones ya presentes en reservas y opiniones (huéspedes, comentarios, etiquetas, datos opcionales). Explicad qué se mantiene y qué revisaríais al crecer. No hay obligación de aplicar todos los patrones.

??? success "Orientaciones para revisar las respuestas"
    **1–2.** No hay un único diseño. Debe responder a las consultas y mantener reglas de negocio. Una copia histórica puede permanecer aunque cambie el hotel actual; una referencia necesita igual valor y tipo. No hay integridad referencial automática.

    **3–4.** Las tarifas finales son 90, 110, 100 y 95. Etiquetar la estructura no migra sus campos. El resultado final conserva dos reservas y el teléfono, con `v: 2`; la consulta compatible permite leer ambas durante la transición.

    **5–7.** Los dos buckets conservan 120 medidas y 120 identificadores distintos. Sus sumas son 1470 y 1590 y sus medias 24,5 y 26,5. Con el dato tardío, solo la segunda hora pasa a 61 y `1620/61`. El contrato debe rechazar las entradas inválidas; permitir nuevos campos es una decisión del ejemplo, no una obligación del RA2.

    **8–10.** El caso excepcional requiere leer y mantener su continuación. Una colección de resúmenes añade obligaciones de actualización; una proyección no duplica contenido almacenado. Las decisiones se justifican por operaciones, crecimiento y garantías, no por el nombre del patrón.

### Criterios para revisar la entrega

Cada colección debe tener un ejemplo válido, una consulta y una explicación del crecimiento esperado. Para las referencias, contrastad tipos e identificadores; para las copias, documentad si son actuales o históricas; para los validadores, adjuntad pruebas aceptadas y rechazadas. Conservad el estado anterior y posterior a cada transformación.

La práctica se realiza en `hotel_modelado`. No se exige modificar los datos usados por 2.6 o 2.9. Los contadores y resultados de este apartado corresponden a sus propios ejemplos. Dibujar buckets o crear colecciones no demuestra capacidad adicional de un clúster; las pruebas de distribución y tolerancia se estudian en sus apartados específicos.

## Autoevaluación del 2.7

Diez preguntas (A–D, **una** correcta). No puntúan en Moodle. **Comprobar respuesta** muestra el resultado y explica el motivo. Revisad el apartado enlazado antes de repetir.

<div class="dwec-quiz" data-dwec-quiz data-src="../../assets/quizzes/ut2-2-7.json"></div>

En [2.8](replicas-shards.md) estudiaremos dónde viven las copias y las particiones y cómo responden ante fallos. El diseño documental sigue siendo necesario: repartir un modelo no corrige referencias incorrectas, arrays sin límite ni resúmenes incoherentes.

## Referencias

- Curso *M320 Data Modeling* (MongoDB University): la **idea** de carga → relaciones → patrones; los ejemplos de esta página son del hotel.
- “6 Rules of Thumb for MongoDB Schema Design” (blog de Mongo)
- [Schema validation](https://www.mongodb.com/docs/manual/core/schema-validation/)
- [2.6 MongoDB](mongodb.md) (oficios del *shell*) · [2.8](replicas-shards.md) (dónde viven las copias) · [2.9](pymongo.md) (`$lookup` en Python)

- [Modelado de datos](https://www.mongodb.com/docs/manual/data-modeling/).
- [Versionado del esquema](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/data-versioning/schema-versioning/).
- [Tamaño BSON en agregación](https://www.mongodb.com/docs/manual/reference/operator/aggregation/bsonSize/).
