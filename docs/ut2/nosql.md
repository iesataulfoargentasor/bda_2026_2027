---
title: 2.5 Familias NoSQL
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.5. Familias NoSQL

Se puede decir que el almacenamiento de datos va por la **tercera plataforma**.

1. **Primera:** los primeros computadores. Bases **jerárquicas** y en **red**, ficheros **ISAM**.
2. **Segunda:** Internet y el cliente-servidor. Ahí se imponen las bases **relacionales**.
3. **Tercera:** Big Data, móviles, *cloud*, IoT y redes sociales. El volumen obliga a paradigmas nuevos: **NoSQL**, **NewSQL** y las plataformas de lago (Hadoop, almacenes en la nube).

Esta página se centra en **NoSQL**. El relacional no desaparece: la caja del hotel sigue cobrando en PostgreSQL. Lo que aparece es **otra familia** cuando el volumen, la variedad o la escala horizontal dejan corto al SQL.

Los SGBD relacionales **no se diseñaron** para crecer añadiendo máquinas ni para que el esquema cambie cada *sprint*. Tampoco aprovechan que el disco **hoy es barato** ni que un clúster de *commodity* suma más CPU que un único *mainframe*. La respuesta de la industria: **desplegar la aplicación y el dato en un clúster**, repartiendo el trabajo entre servidores.

El criterio **a)** del RA2 aquí: estas bases **depositan** formas raras (JSON, grafos, series) y **responden rápido** a *su* tipo de pregunta. El **d)**: muchas permiten **guardar sin esquema rígido** y validar **al leer**. El **e)** y el **c)** se ven en el *auto-sharding* y en la réplica (el detalle de Mongo está en el [2.8](replicas-shards.md)).

## No solo SQL

Si lo definimos en serio: NoSQL es un conjunto de tecnologías para procesar conjuntos grandes de datos dando **prioridad al rendimiento, la fiabilidad y la agilidad**.

El acrónimo suena a “cualquier cosa que no sea relacional y no hable SQL”. En la práctica el *No* es **not only**: sistemas **complementarios** al SGBD relacional. Priorizan **escala y disponibilidad** frente a la atomicidad y la consistencia *estrictas* de cada escritura.

Hay **más de una manera** de resolver el problema. A veces la mejor herramienta es PostgreSQL (cobrar, stock de minibar). A veces es Mongo (reserva con extras que cambian). A veces Redis (sesión). NoSQL no **sustituye** la caja: **amplía** el ecosistema. Eso se llama a menudo **persistencia políglota**: cada pregunta, su almacén.

### ACID (el listón del relacional)

Las relacionales ofrecen **transaccionalidad** con [ACID](../ut1/almacenamiento.md). En el hotel: transferir un depósito de la fianza a la cuenta de Laredo son **dos** cambios. O salen los dos o no sale ninguno.

| Letra | Nombre | En recepción |
| --- | --- | --- |
| **A** | Atomicidad | Todo el paquete o nada |
| **C** | Consistencia | Las reglas se cumplen (un saldo no queda “prohibido”) |
| **I** | Aislamiento | Nadie ve el cobro a medias |
| **D** | Durabilidad | Lo confirmado **no se pierde** si se va la luz |

Un *like* en la web del hotel puede retrasarse un segundo. Un cobro, no.

### Cuatro familias (elige el problema)

| Familia | Unidad | Encaje en el hotel | Productos que veréis citados |
| --- | --- | --- | --- |
| **Clave-valor** | `clave → valor` (a menudo un *blob*) | Sesión, caché de disponibilidad | Redis, Riak, DynamoDB |
| **Documento** | JSON/BSON anidado | Reserva con huéspedes y extras | MongoDB, CouchDB |
| **Columnas** | Familia de columnas, filas enormes | Series de sensores, logs | Cassandra, HBase, Bigtable |
| **Grafo** | Nodos y aristas | “Quién recomendó el hotel a quién” | Neo4j, Neptune, ArangoDB |

Más abajo cada modelo se desarrolla. Elegir “NoSQL” sin decir **cuál** es como decir “voy en vehículo” sin decir si es bici o camión.

## Siete características (frente al relacional)

1. **Esquema flexible.** No exigen un contrato fijo al guardar. Tragan estructurado, semiestructurado y sin estructurar. Empiezas con `hotel` y `noches`; en abril añades `mascota` **solo** en los documentos nuevos. Los de 2024 siguen sin ese campo.
2. **Escala horizontal.** *Sharding* / particionado: más nodos, más capacidad. El relacional suele crecer **en vertical** (más RAM, más CPU en *una* máquina). NoSQL crece **repartido**, a menudo **sin** que el código sepa cuántos servidores hay.
3. **Varios modelos.** Clave-valor, documento, columnas, grafo: problemas que el modelo relacional **no** planteó en los 70.
4. **Alta disponibilidad y tolerancia a fallos.** Réplica y distribución. Maestro-esclavo o entre pares. Un disco de Potes se funde: el clúster **sigue** (criterio **c)**).
5. **Lectura y escritura masivas.** Pensadas para redes sociales, sensores IoT, analítica continua. El PMS deja 40 000 eventos/hora: este es el terreno.
6. **Consistencia eventual (a menudo).** Frente a ACID, muchas priorizan disponibilidad y particiones ([CAP](#teorema-cap)). Los nodos se igualan *al rato*. Útil cuando la **latencia** duele más que un segundo de desfase.
7. **Almacén distribuido.** Encajan en AWS, Azure, GCP. El hotel no monta un SAN para fingir un solo servidor.

Por eso aparecen en *apps* modernas, IoT y tiempo (casi) real. **No** por eso cobran mejor que PostgreSQL.

## Esquema dinámico (criterio d)

El relacional pide el esquema **antes**. Si a mitad de un *sprint* gerencia quiere “productos favoritos del cliente” además de dirección y teléfonos, en SQL **añades columna** y **migras** la tabla. En una base grande eso es parada, o un despliegue azul/verde con otra copia. El desarrollo ágil **choca** con migraciones semanales.

NoSQL se construye para **insertar sin esquema predefinido**. Cambiáis la *app* sin tumbar el almacén. Eso no significa “cualquier basura vale”: podéis definir un **esquema al leer** (*schema-on-read*) para que cada consumidor compruebe *su* contrato. Guardáis hoy; el informe de 2027 **interpreta** mañana.

Los modelos NoSQL **priman la redundancia**: se **desnormaliza** para no hacer *joins*. Por eso el esquema **tiene** que poder crecer (un campo nuevo en el documento de reserva) sin rehacer cinco tablas. El [2.7](modelado.md) entra en embeber frente a referenciar.

## Fragmentación / particionado (criterio e)

El relacional, por cómo está hecho, suele escalar **en vertical**: un servidor cada vez más gordo para no perder disponibilidad. Eso cuesta, tiene **techo de hardware** y concentra el fallo en pocos puntos.

La salida es escalar **en horizontal**: añadir servidores en vez de hinchar uno. Un clúster traga más dato del que cabe en **cualquier** máquina sola. A ese corte se le llama ***sharding*** o **particionado**.

El particionado **no es exclusivo** de NoSQL. En SQL también existe:

| Corte | Qué partes | Ejemplo hotel |
| --- | --- | --- |
| **Horizontal** | Distintas **filas** en distintas particiones | Clientes de Trasmiera en un nodo, Liébana en otro |
| **Vertical** | Distintas **columnas** en distintas particiones | Contacto en un sitio, datos fiscales en otro |

En NoSQL el corte **depende del modelo**:

- Clave-valor y documento: casi siempre **horizontal** (por `_id`, por hotel, por *hash*).
- Columnas: horizontal **o** vertical (familias de columnas distintas en sitios distintos).

Escalar un SQL **entre muchas instancias** se *puede*: SAN, *shared disk*, pegamento. El motor **no** lo trae de serie. Entonces el equipo:

- guarda cada trozo **autónomo** en su instancia;
- escribe código para **repartir** consultas y **juntar** resultados;
- escribe más código para fallos, *joins* entre bases, equilibrado y réplica.

Muchos beneficios (integridad transaccional) se **debilitan o se pierden**. Por eso “SQL partido a mano” duele; NoSQL suele traer el corte **de fábrica**.

### Auto-sharding

Las NoSQL suelen **partir solas**: datos y consultas se **balancean**. La *app* no conoce el *pool* de servidores. Métodos habituales:

| Método | Idea | Hotel |
| --- | --- | --- |
| **Por rango** | “`id` 1–1 000 000 en el *shard* 1”; o hoteles A–L / M–Q / R–Z | Cuidado: Laredo puede ser un *hotspot* si casi todas las reservas empiezan por L |
| **Por lista** | Por **categoría** | Novelas vs recetas; aquí: canal `web` / `ota` / `recepcion` en *shards* distintos (raro si un canal se come el 90 %) |
| **Por hash** | Una función decide el *shard* a partir de la clave | Reparte más **uniforme**; las consultas por rango de `_id` se **complican** |

### Cuándo particionar

Sí, cuando:

- **no cabe** (disco o RAM de un solo servidor);
- las **escrituras** saturan un nodo y queréis **repartir** la carga;
- un servidor **ocupado** no debe ser el único que responda (disponibilidad).

No, cuando el volumen es **pequeño**: repartir **cuesta** (red, *routers*, rebalanceos). Tampoco esperéis a tener **demasiado**: partir un lago ya enorme **satura** el sistema. El [2.8](replicas-shards.md) lo enseña en Mongo.

La nube (AWS, Azure) vende capacidad **bajo demanda** y os quita parte de la administración. Una granja de *commodity* puede igualar a un servidor carísimo **por menos dinero**. El criterio **e)** en una frase: *añades un nodo, no reescribes la recepción*.

## Replicación (criterio c)

La **réplica** mantiene **copias** del mismo dato en varios servidores. La *app* sigue aunque una máquina muera. La mayoría de NoSQL lo hacen **solas**, sin un producto de terceros. Para el desarrollador el almacén es un *servicio*; no abre sockets a `mongo-2`.

Sirve para:

- **Escala:** las lecturas se **reparten**; cada nodo tiene (casi) los mismos bytes.
- **Disponibilidad:** fallo de hardware o corrupción. Una copia puede **tomar el relevo**. Informes y *backups* en secundarios para no tumbar el primario.
- **Aislamiento** (la I de ACID, en versión *ops*): cambios que se **propagan**. Analítica y preproducción en una copia, sin pegar al nodo que cobra.

Antes de elegir arquitectura, decidid el **oficio** de la copia: ¿solo **lectura** (informes) o también **escritura**?

| Arquitectura | Quién escribe | Precio |
| --- | --- | --- |
| **Primario–secundario** (*master–slave*) | Solo el primario; los demás siguen | El primario es **SPOF** si no hay elección automática |
| **Varios primarios / entre pares** | Casi todos aceptan escritura | Escrituras simultáneas → **discrepancias** un rato |

### Consistencia

En un sistema **consistente**, lo que acabas de escribir **aparece** en la siguiente lectura.

| Modelo | Garantía | Encaje |
| --- | --- | --- |
| **Fuerte** | Tras confirmar, **toda** lectura ve el valor | Banca, caja, fianza |
| **Eventual** | Las copias se igualan *al rato*; puedes leer **atrasado** | *Likes*, comentarios, a veces stock no crítico |

Stock del minibar: si es **fuerte**, cada consulta es el inventario real. Si es **eventual**, puede mentir un instante y **arreglarse**. Décadas de SQL os hacen ver la consistencia fuerte como “lo natural”. A veces el desfase es un **precio aceptable** a cambio de que la web **no se caiga**.

La consistencia eventual encaja en *apps* de **solo lectura**, históricos que casi no cambian, o **mucha escritura y poca lectura** (un log).

!!! warning "Réplica no es shard"
    **Replicar** = el **mismo** dato en varias máquinas. **Particionar** = cada máquina un **trozo**. Lo más seguro y lo que mejor rinde: **las dos cosas** (cada *shard* replicado × 2 o × 3). El [2.8](replicas-shards.md) lo monta.

## Implantar sin drama

Las empresas empiezan con una prueba **pequeña** (Community, un nodo, poco riesgo). Casi todas las NoSQL son *open source* al inicio. Ciclos más cortos → innovar más barato. Preguntas de aula (escribidlas **antes** de elegir producto):

- ¿Cuántos usuarios / reservas en 3, 6, 12 meses?
- ¿Qué funciones **comerán** más disco al crecer?
- ¿Se puede **partir** por geografía (Laredo / Potes / Santander)?
- ¿Qué pasa si el almacén **cae** un viernes de agosto? (alta disponibilidad)
- ¿Ratio **lectura / escritura**? ¿Pico? ¿Tamaño del *payload*? ¿CPU por operación?
- ¿Esquema **fijo** o inquieto? ¿Migrar duele (parada, scripts)?
- ¿Podemos **bajar tráfico** al almacén (caché) y ganar rendimiento?

Dimensiones al elegir (no “el que salga en un tutorial”):

| Dimensión | Pregunta |
| --- | --- |
| **Modelo de datos** | Documento, columnas, grafo, clave-valor |
| **Consultas** | ¿Solo por clave primaria o por **varios** campos? ¿Índice secundario? ¿Hay que **modificar**? |
| **Consistencia** | Fuerte o eventual (varias copias) |
| **API** | **No hay estándar.** Cada producto es un idioma. Un API inmaduro cuesta **años** |
| **Comunidad y soporte** | ¿Hay *enterprise*? ¿Se encuentra gente? ¿Hay documentación y conectores (Python)? |

Casos típicos de arranque:

- Web con campos **a medida** → documental.
- Capa de **caché** → clave-valor.
- Binarios + metadatos consultables (fotos de habitación) → documento o clave-valor; los bytes gordos a menudo en [HDFS](hdfs.md) / objeto, el JSON en Mongo.
- Volumen enorme, consistencia **no** crítica, sí disponibilidad y distribución → documento o columnas.

### Limitaciones (las honestas)

- **Poco estándar.** Cada NoSQL nació de un caso distinto. No hay un SQL único.
- **Riesgo *open source*.** Algunas no se mantienen. Mirad comunidad y si existe versión de pago.
- **GUI desigual.** Pocas tienen un Compass cómodo.
- **Perfiles escasos** (y caros) frente a SQL.

## Modelo documental

El relacional guarda filas y columnas. El documental guarda **documentos** (casi siempre **JSON**): un objeto, como en programación. Los documentos se agrupan en **colecciones** (o “bases”, según el producto).

Un campo tiene tipo: cadena, entero, fecha, binario, *array* u **otro documento**. En vez de **esparcir** la reserva en cinco tablas, **hotel, huéspedes y extras viven juntos**. El acceso se simplifica: menos *joins*, menos transacciones largas.

*Lo que se usa junto, se guarda junto.* El [2.6](mongodb.md) y el [2.7](modelado.md) lo practican.

El esquema es **dinámico**: dos documentos de `reservas` **no** tienen por qué traer las mismas claves.

```json
{
  "_id": "R-18442",
  "hotel": "Laredo",
  "canal": "web",
  "noches": 3,
  "importe": 186.5
}
```

```json
{
  "_id": "R-18499",
  "hotel": "Potes",
  "noches": 2,
  "cobro": {
    "medio": "tarjeta",
    "ok": true
  },
  "extras": ["parking", "cuna"]
}
```

El objeto `cobro` agrupa lo que en SQL sería una relación **1:1** (tabla `Cobro`). El *array* `extras` agrupa un **1:N** (tabla `Extra`). No hace falta *join* para pintar la reserva.

Suele haber una **clave** (`_id`) que identifica el documento. Además, consultas por **cualquier** campo. Índices: compuestos, dispersos, **TTL** (la sesión caduca sola), únicos, texto, geo (hoteles cerca de una playa). Agregación y, en algunos productos, MapReduce.

Actualizar **un** documento suele ser **una** sentencia: no recorréis tres tablas.

**Sirve para:** flujos de eventos entre *apps*, CMS / blog (comentarios, usuarios), analítica web (un campo nuevo cuando aparece una métrica), *e-commerce* que **crece** de esquema.

**No encaja:** operativa con **transacciones complejas** (el cobro ACID); agregados cuya **forma** cambia cada semana (acabaréis normalizando otra vez).

Productos: **MongoDB** (el de esta UT), **CouchDB**.

## Modelo clave-valor

Es una **tabla hash**: casi todo el acceso va por la **clave primaria**. Desde el modelo de datos, es el más **simple**.

Imaginad una tabla SQL de dos columnas (`id`, `nombre`). En clave-valor el “nombre” puede ser un entero, un JSON o un **BLOB**. Si la clave existe, el `SET` **pisa** el valor.

El cliente: obtener, asignar, borrar. El valor es **opaco** para el motor: **no** sabe qué hay dentro. No podéis pedir “todas las de Trasmiera” si Trasmiera está **dentro** del *blob*. La *app* es responsable de recordar el contrato.

Algunos productos agrupan claves en ***buckets*** (como una tabla). Riak, por ejemplo, habla HTTP:

```text
curl -X PUT http://localhost:8098/riak/sesiones/S-991 \
  -H "Content-Type: application/json" \
  -d "{\"hotel\":\"Laredo\",\"canal\":\"web\"}"
```

**Redis** tipa el valor: cadenas, *hashes*, conjuntos, listas. Entonces sí hay intersección, unión, rangos. Ya no es “solo un *blob*”: se usa como caché, cola y contador.

```text
SET sesion:991 "huésped-Laredo"
HSET reserva:18442 hotel "Laredo"
HSET reserva:18442 canal "web"
SADD hotel:Laredo:extras parking cuna
```

```python
import redis

r = redis.Redis(host="localhost", port=6379)
r.mset({"Laredo": "disponible", "Potes": "completo"})
r.get("Potes")  # b'completo'
```

El acceso por clave primaria da **muy buen** rendimiento y escala fácil. Para ir al máximo: todo en **RAM** y serializar a disco de vez en cuando → consistencia **eventual**.

**Sirve para:** `sessionid` del motor de reservas, preferencias, carrito **antes** de cobrar, **caché** de disponibilidad.

**No encaja:** relaciones entre datos, transacciones de **varios** pasos, consultas **por dentro** del valor, operaciones sobre **conjuntos de claves** (“todas las que empiezan por `Laredo:`” si el producto no lo ayuda).

Productos: **Redis**, **DynamoDB**, Voldemort (clon abierto de Dynamo).

## Modelo basado en columnas

El relacional usa la **fila** como unidad: bien para **escribir** una reserva completa. Cuando escribís **poco** y leéis **unas pocas columnas de muchas filas** (ocupación de 80 hoteles × 365 días), conviene **girar** el modelo: guardar por **columnas**. Los valores del mismo tipo quedan juntos → se **comprimen** mejor.

```text
Por filas:     [Laredo,web,3,186] [Potes,ota,2,90] [Noja,web,4,210]
Por columnas:  [Laredo,Potes,Noja] [web,ota,web] [3,2,4] [186,90,210]
```

!!! question "Autoevaluación de pizarra"
    ¿Añadir **un** registro (una reserva nueva) es más barato en filas o en columnas? En **filas**: un sitio, un append. En columnas: tocáis **varias** estructuras. Por eso las columnares brillan en **analítica** (OLAP), no en el clic de recepción (OLTP).

Con Spark en memoria, la ventaja relativa *a veces* se estrecha. El oficio sigue: **scan** de una métrica en millones de filas.

### Representación (Bigtable)

Se inspiran en [Bigtable](https://research.google.com/archive/bigtable.html) de Google: mapa **ordenado**, **multidimensional** y **repartido**. Cada fila puede tener **del orden de un millón** de columnas y hay **miles de millones** de filas, con **versiones**.

Dos niveles: la clave de fila → un mapa de **familias de columnas** → columnas.

Una **columna** es `nombre` + `valor` + **`timestamp`** (caducidad y “quién gana” si hay dos escrituras):

```json
{ "name": "temp_c", "value": "21.4", "timestamp": 1710000000 }
```

Una **fila** es un conjunto de columnas bajo una clave (`hab:214:2026-04-01`). Una **familia** agrupa filas parecidas (como una “tabla”), **sin** exigir las mismas columnas:

```text
sensores
  hab:214 : { temp_c, humedad, ultima_lectura }
  hab:108 : { temp_c, puerta }          ← no tiene humedad
```

Las **supercolumnas** anidan un mapa dentro de otra columna (metadatos de un ISBN, un cobro). Familias de supercolumnas = ese patrón a escala.

Se accede por **clave de fila** (toda la familia o una columna). Cassandra ofrece **CQL**, parecido a SQL **sin** *joins* ni subconsultas; el `WHERE` es limitado:

```sql
SELECT temp_c FROM sensores WHERE hab_id = '214';
```

Actualizar = **encontrar** + **reescribir**. A veces se reescribe el registro **entero** aunque cambien dos bytes.

**Sirve para:** BI, *warehouse* columnar, cubos OLAP, metadatos, analítica (casi) en tiempo real. Menos disco (compresión + autoíndice) y agregados que en filas cruzarían muchas tablas.

**No encaja:** OLTP concurrente: el relacional aísla mejor el clic de caja.

Productos: **HBase** (encima de [HDFS](hdfs.md)), **Cassandra**, Amazon Redshift (almacén columnar en la nube; no es “la misma pieza” que HBase, pero el giro fila/columna es el mismo oficio).

## Modelo de grafos

Guarda **entidades** y **relaciones**. Las entidades son **nodos** (con propiedades). Las relaciones son **aristas** (también con propiedades y **sentido**). Un nodo ≈ una instancia. La dirección importa: si queréis ida y vuelta, **dos** aristas.

```text
(Huésped:Ana) -[:RECOMENDO {año:2025}]-> (Hotel:Potes)
(Huésped:Luis) -[:AMIGO]-> (Huésped:Ana)
```

Los nodos se organizan por relaciones: el **mismo** dato se interpreta distinto según el camino (*quién recomendó*, *quién es VIP*, *quién está a dos saltos*). No hay techo práctico de tipos de arista en el mismo grafo.

**Recorrer** (*traverse*) es la consulta: “huéspedes del club de senderismo **y** con más de dos estancias en Liébana”. En Neo4j las relaciones **ya están persistidas**: no se calculan al vuelo como un `JOIN` de ocho tablas.

En SQL, un grafo “jefe–empleado” es una FK. Añadir *otra* relación (recomendó, visitó, canceló) pide **cambiar el esquema** y mover datos. Además tenéis que **saber las preguntas** al modelar. En el grafo cambiáis el *traverse* **sin** rehacer nodos.

**Sirve para:** redes (quién conoce a quién), rutas y distancias (hoteles cercanos, camino más corto), **recomendaciones** (“quien reservó Potes también reservó Fuente Dé”).

**No encaja:** cambiar **una** propiedad en **todos** los nodos (operación cara).

Productos: **Neo4j**, ArangoDB, OrientDB, TinkerPop, Amazon Neptune.

## Consistencia según la familia

Documentales y grafos pueden ser **fuertes o eventuales**. **MongoDB** es configurable: por defecto lecturas y escrituras al **primario** (consistencia fuerte); podéis leer de **secundarios** (eventual) **por consulta**. El [2.8](replicas-shards.md) lo enseña.

Clave-valor y columnas suelen ser **eventuales**. Cualquier copia puede recibir una escritura → **conflictos**. Estrategias que veréis citadas:

- **Relojes vectoriales** (Riak): ordenan eventos; gana el más reciente.
- **CouchDB:** guarda los valores en conflicto y **el usuario** decide.
- **Cassandra:** a menudo “el valor **más grande**” (o el *timestamp* más nuevo) gana.

Las **escrituras** rinden; las **actualizaciones** con conflicto las paga la *app*.

## Teorema CAP

[Eric Brewer, 2000](https://en.wikipedia.org/wiki/CAP_theorem): en un sistema **distribuido** no podéis tener a la vez las tres:

| Letra | Nombre | Oficio |
| --- | --- | --- |
| **C** | Consistencia | La escritura es atómica; **toda** lectura posterior ve el valor nuevo |
| **A** | Disponibilidad (*Available*) | Siempre hay **respuesta** (no *downtime* eterno) |
| **P** | Tolerancia a **particiones** | El sistema sigue si se corta el enlace entre nodos |

Podéis ser **CP**, **AP** o **CA**. **No** las tres en un clúster partido. En el [1.3](../ut1/almacenamiento.md) ya está el triángulo; aquí lo usáis para **clasificar productos**.

En la práctica **P no es opcional** en un hotel con dos sedes: un *switch* se cuelga. La pelea real es **C frente a A**. Si elegís disponibilidad, aún podéis tener **consistencia eventual**: cada nodo responde; el dato puede ir **un poco atrasado** y **igualarse**.

Algunos (Riak) dejan elegir el nivel **por petición**.

### Clasificación habitual (no es dogma)

Muchos productos **se configuran**. “Mongo es CP” es el **defecto**, no una ley.

| Tipo | Prioriza | Ejemplos que salen en textos |
| --- | --- | --- |
| **CP** | Consistencia + particiones | MongoDB, HBase: pueden **no** responder en un secundario; un secundario puede **promocionar** si cae el primario |
| **AP** | Disponibilidad + particiones | DynamoDB: replica; **no** garantiza la misma versión en todos los nodos al instante |
| **CA** | Consistencia + disponibilidad | Relacionales de **un** sitio (PostgreSQL). El dato **no** está partido, así que P “no entra”. Hay extensiones (*Pgpool*, *Citus*…) cuando sí se parte |

CouchDB y Mongo **pueden** moverse en el mapa según lectura en secundarios, *write concern*, etc.

### BASE (el otro extremo de ACID)

Las distribuidas que eligen **responder** siguen **BASE** (disponibilidad antes que consistencia estricta → AP):

- **Basically Available:** siempre hay respuesta (éxito o error claro), aunque un nodo no haya visto la última escritura.
- **Soft state:** dos lecturas seguidas pueden **diferir** sin que vosotros hayáis escrito: un nodo iba atrasado.
- **Eventual consistency:** tras escribir, el clúster es consistente **cuando el cambio llega a todos**. Mientras tanto, estado blando.

!!! failure "¿BASE para la caja?"
    **No.** Cobro, fianza, nota oficial: **ACID**. BASE: timeline, catálogo replicado, sensores, carrito **antes** de pasar la tarjeta.

## Resumen de aula

Un sistema NoSQL, en la frase que cierra el tema de referencia: *open source* (a menudo), **no relacional**, **sin esquema predefinido**, **escala horizontal**, transaccionalidad **BASE** (salvo que lo endurezcáis).

NewSQL (CockroachDB, etc.) intenta **SQL + escala horizontal + ACID**. No es el núcleo de esta página; si Moodle lo pide, es una presentación de 5–6 diapositivas: qué problema cierra respecto a NoSQL y respecto a un PostgreSQL de un solo nodo.

!!! success "En voz alta"
    “NoSQL es *not only*. Eligo la familia por la pregunta. Parto cuando no cabe; replico para no morir. CAP me obliga a elegir. La caja sigue en ACID.”

## Relación con el RA2

| Criterio | En este apartado |
| --- | --- |
| **a)** | Depositar **cualquier** forma (JSON, grafo, serie) y responder **a su** pregunta, rápido |
| **c)** | Réplica, elección de primario, conflictos; el lab está en el [2.8](replicas-shards.md) |
| **d)** | Esquema al guardar **flojo**, esquema al leer; documentos que **crecen** |
| **e)** | *Auto-sharding*, más nodos, cloud |

## Para practicar (Moodle manda la nota)

1. ¿Qué significa el *No* de NoSQL? Relación con el relacional (complemento, no sustituto).
2. ¿Un sistema puede **replicar y particionar** a la vez? Dibujad el hotel: tres *shards* (comarcas) × dos copias.
3. Elegid **familia y por qué**:
    - wiki de fichas de habitación (texto, fotos, campos que aparecen);
    - expediente académico de un país (centros, alumnos, notas, muchas relaciones fijas);
    - caché de “¿queda habitación doble en Laredo esta noche?”;
    - “quién recomendó Potes a quién” para una campaña.
4. Investigad **persistencia políglota** y aplicadla al grupo hotelero (caja + Mongo + Redis + HDFS).
5. Clasificad según CAP (**CA / CP / AP**) y anotad modelo + puesto aproximado en [DB-Engines](https://db-engines.com/en/ranking): Bigtable, Cassandra, DynamoDB, HBase, MongoDB, Redis, Neo4j, PostgreSQL, InfluxDB. Decid **qué pasa si se parte la red**, no solo la etiqueta.
6. (Opcional) 5–6 diapositivas: movimiento **NewSQL** y qué ofrece CockroachDB frente a un relacional clásico.

## Referencias

- Guy Harrison, *Next Generation Databases*
- Sadalage y Fowler, *NoSQL Distilled* (*polyglot persistence*)
- [1.3 Almacenamiento](../ut1/almacenamiento.md) (ACID, CAP, BASE con la transferencia)
- [2.6 MongoDB](mongodb.md), [2.7 Modelado](modelado.md), [2.8 Réplicas y shards](replicas-shards.md)
