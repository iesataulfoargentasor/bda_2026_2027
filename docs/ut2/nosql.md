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

El acrónimo suena a “cualquier cosa que no sea relacional y no hable SQL”. En la práctica el *No* es **not only**: sistemas **complementarios** al SGBD relacional. Sus garantías varían: algunas priorizan disponibilidad, otras ofrecen lecturas fuertes y transacciones. **NoSQL describe una familia de modelos, no una renuncia universal a ACID**.

Hay **más de una manera** de resolver el problema. A veces la mejor herramienta es PostgreSQL (cobrar, stock de minibar). A veces es Mongo (reserva con extras que cambian). A veces Redis (sesión). NoSQL no **sustituye** la caja: **amplía** el ecosistema. Eso se llama a menudo **persistencia políglota**: cada pregunta, su almacén.

### ACID (el listón del relacional)

ACID describe propiedades de una **transacción**, también disponible en ciertos motores NoSQL. La consistencia de ACID significa respetar invariantes, como que una cantidad no sea negativa. La C de CAP, que veremos después, se refiere a la visión de las operaciones entre nodos; son conceptos distintos.

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

Estas características son tendencias. Antes de elegir un producto hay que comprobar cuáles ofrece y con qué configuración.

1. **Flexibilidad del esquema.** Un documento puede incluir `mascota` y otro no. La aplicación debe definir qué significa la ausencia y validar los datos imprescindibles. Una base de grafos o de familias de columnas tiene sus propias reglas; no todas aceptan cualquier estructura.
2. **Escala horizontal.** Algunos motores reparten datos entre nodos mediante particiones. También existen motores SQL distribuidos. El reparto añade capacidad, pero introduce comunicaciones y puede complicar las consultas que cruzan particiones.
3. **Varios modelos.** Clave-valor, documental, familias de columnas y grafo facilitan diferentes accesos. Buscar una sesión por su clave y recorrer recomendaciones entre clientes son problemas distintos.
4. **Disponibilidad y tolerancia a fallos.** Las réplicas permiten sobrevivir a ciertos fallos. Hay que concretar cuántos nodos pueden perderse y qué operaciones siguen disponibles; una copia aislada no siempre puede aceptar escrituras.
5. **Cargas masivas.** La distribución puede mejorar el caudal de lecturas o escrituras. Los índices y la clave de partición deben corresponder a las consultas reales: un clúster no corrige automáticamente un filtro ineficiente.
6. **Consistencia configurable en algunos productos.** Una lectura de un secundario puede devolver una versión anterior. Una reserva de la última plaza necesita garantías diferentes a un contador aproximado de visitas.
7. **Despliegue distribuido.** Puede administrarse en servidores propios o contratarse como servicio. La nube cambia quién mantiene la infraestructura, pero no elimina los costes de almacenamiento, réplicas y transferencia.

En el hotel justificaríamos Redis por el acceso a sesiones, MongoDB por la ficha documental y HDFS por el histórico de ficheros. Esa justificación es más útil que afirmar que «NoSQL es más rápido».

## Esquema dinámico (criterio d)

Supongamos que las reservas antiguas contienen `hotel`, `noches` e `importe`, y las nuevas añaden `mascota`. En una colección documental pueden coexistir ambas versiones. La consulta por `hotel` sigue siendo válida, pero la aplicación debe decidir si la ausencia de `mascota` significa «no», «no se preguntó» o «dato desconocido».

En un sistema relacional se suele declarar la estructura antes de insertar. Añadir una columna **no exige siempre una parada**: depende del motor, la operación y el despliegue. A su vez, un esquema documental flexible también requiere migraciones si cambiamos el significado o el tipo de un campo.

Conviene separar tres decisiones: el **modelo** que organiza los datos, la **validación al escribir** y la **interpretación al leer**. Podemos conservar el JSON original en HDFS y, al mismo tiempo, exigir que `noches` sea un entero positivo en la colección operativa.

Desnormalizar consiste en guardar juntos datos que se leen juntos. Ahorra consultas, pero obliga a decidir cómo mantener las copias coherentes. El [modelado documental](modelado.md) desarrolla este intercambio entre facilidad de lectura, tamaño y coste de actualización.

## Fragmentación / particionado (criterio e)

**Escalar en vertical** es ampliar RAM, CPU o discos de una máquina. Es una opción tanto para SQL como para NoSQL; tiene límites de hardware y no aporta por sí sola alta disponibilidad.

La salida es escalar **en horizontal**: añadir servidores en vez de hinchar uno. Un clúster traga más dato del que cabe en **cualquier** máquina sola. A ese corte se le llama ***sharding*** o **particionado**.

El particionado **no es exclusivo** de NoSQL. En SQL también existe:

| Corte | Qué partes | Ejemplo hotel |
| --- | --- | --- |
| **Horizontal** | Distintas **filas** en distintas particiones | Clientes de Trasmiera en un nodo, Liébana en otro |
| **Vertical** | Distintas **columnas** en distintas particiones | Contacto en un sitio, datos fiscales en otro |

En NoSQL el corte **depende del modelo**:

- Clave-valor y documento: casi siempre **horizontal** (por `_id`, por hotel, por *hash*).
- Familias de columnas: reparto según claves de fila o de partición y reglas del producto; no se deduce un reparto por servidor para cada columna.

El particionado puede realizarlo la aplicación, una extensión o el propio motor, tanto en SQL como en NoSQL. Si lo hacemos a mano, debemos resolver el enrutamiento de consultas, la unión de resultados, las migraciones y los fallos. Un motor distribuido integra parte de ese trabajo, aunque sigue necesitando una clave adecuada.

En las familias de columnas, «columna» no implica que cada columna viva en una máquina diferente. HBase reparte rangos de filas en regiones y Cassandra distribuye mediante claves de partición. El modelo lógico y la distribución física son decisiones relacionadas, pero distintas.

### Auto-sharding

En los motores con **auto-sharding**, el sistema gestiona la distribución y el enrutamiento una vez configurado. La aplicación utiliza una entrada lógica, pero el administrador sigue eligiendo la clave y vigilando desequilibrios. Métodos habituales:

| Método | Idea | Hotel |
| --- | --- | --- |
| **Por rango** | “`id` 1–1 000 000 en el *shard* 1”; o hoteles A–L / M–Q / R–Z | Cuidado: Laredo puede ser un *hotspot* si casi todas las reservas empiezan por L |
| **Por lista** | Por **categoría** | Novelas vs recetas; aquí: canal `web` / `ota` / `recepcion` en *shards* distintos (raro si un canal se come el 90 %) |
| **Por hash** | Una función decide el *shard* a partir de la clave | Reparte más **uniforme**; las consultas por rango de `_id` se **complican** |

### Cuándo particionar

Sí, cuando:

- **no cabe** (disco o RAM de un solo servidor);
- las **escrituras** saturan un nodo y queréis **repartir** la carga;
- la carga puede dividirse de forma útil entre particiones. La disponibilidad requiere además réplicas y un protocolo de recuperación.

No, cuando el volumen es **pequeño**: repartir **cuesta** (red, *routers*, rebalanceos). Tampoco esperéis a tener **demasiado**: partir un lago ya enorme **satura** el sistema. El [2.8](replicas-shards.md) lo enseña en Mongo.

La nube (AWS, Azure) vende capacidad **bajo demanda** y os quita parte de la administración. Una granja de *commodity* puede igualar a un servidor carísimo **por menos dinero**. El criterio **e)** en una frase: *añades un nodo, no reescribes la recepción*.

## Replicación (criterio c)

La **réplica** mantiene **copias** del mismo dato en varios servidores. La *app* sigue aunque una máquina muera. La mayoría de NoSQL lo hacen **solas**, sin un producto de terceros. Para el desarrollador el almacén es un *servicio*; no abre sockets a `mongo-2`.

Sirve para:

- **Escala:** las lecturas se **reparten**; cada nodo tiene (casi) los mismos bytes.
- **Disponibilidad:** fallo de hardware o corrupción. Una copia puede **tomar el relevo**. Informes y *backups* en secundarios para no tumbar el primario.
- **Separación de cargas:** determinadas lecturas analíticas pueden dirigirse a secundarios. Esto reduce trabajo en el primario, pero **no es el aislamiento transaccional de ACID**. Una réplica operativa tampoco es un entorno de pruebas independiente: los cambios del primario llegan a ella.

Antes de elegir arquitectura, decidid el **oficio** de la copia: ¿solo **lectura** (informes) o también **escritura**?

| Arquitectura | Quién escribe | Precio |
| --- | --- | --- |
| **Primario–secundario** (*master–slave*) | Solo el primario; los demás siguen | El primario es **SPOF** si no hay elección automática |
| **Varios primarios / entre pares** | Casi todos aceptan escritura | Escrituras simultáneas → **discrepancias** un rato |

### Consistencia

La consistencia describe qué versiones pueden observar los clientes. **Leer tus propias escrituras** es una garantía concreta; la consistencia linealizable exige además que las operaciones de todos los clientes se comporten como si actuaran sobre una única copia, respetando el orden temporal.

| Modelo | Garantía | Encaje |
| --- | --- | --- |
| **Fuerte** | Tras confirmar, **toda** lectura ve el valor | Banca, caja, fianza |
| **Eventual** | Las copias se igualan *al rato*; puedes leer **atrasado** | *Likes*, comentarios, a veces stock no crítico |

Stock del minibar: si es **fuerte**, cada consulta es el inventario real. Si es **eventual**, puede mentir un instante y **arreglarse**. Décadas de SQL os hacen ver la consistencia fuerte como “lo natural”. A veces el desfase es un **precio aceptable** a cambio de que la web **no se caiga**.

La consistencia eventual encaja en *apps* de **solo lectura**, históricos que casi no cambian, o **mucha escritura y poca lectura** (un log).

!!! warning "Réplica no es shard"
    **Replicar** = el **mismo** dato en varias máquinas. **Particionar** = cada máquina un **trozo**. Se pueden combinar: cada shard mantiene réplicas. La seguridad y el rendimiento dependen de cuántas, cómo votan y dónde se alojan; dos votantes no toleran perder uno y seguir eligiendo primario. El [2.8](replicas-shards.md) lo monta.

## Implantar sin drama

Las empresas empiezan con una prueba **pequeña** (Community, un nodo, poco riesgo). Las licencias y modalidades de servicio varían; revisad las del producto elegido. Ciclos más cortos → innovar más barato. Preguntas de aula (escribidlas **antes** de elegir producto):

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

La unidad de lectura es una ficha con campos relacionados. En el hotel, reserva, huéspedes y extras pueden viajar juntos. Antes de embeber, estimad tamaño y crecimiento y decidid qué cambios deben ser atómicos. El documento no elimina las relaciones: permite representarlas dentro de la ficha o mediante referencias.

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

**Hay que evaluarlo con cuidado** cuando abundan relaciones cruzadas, restricciones entre documentos o transacciones largas. MongoDB admite transacciones, pero su coste y el modelo deben compararse con una solución relacional. No basta con que la información pueda escribirse como JSON.

Productos: **MongoDB** (el de esta UT), **CouchDB**.

## Modelo clave-valor

La pregunta típica es «dame el valor de esta clave», por ejemplo `sesion:991`. Si necesitamos buscar por el contenido de todos los valores, quizá hagan falta estructuras auxiliares o un motor con índices. Una sesión puede caducar; una reserva confirmada requiere una política de conservación diferente. Los ejemplos de Redis presuponen un servidor Redis y su cliente, independientes del laboratorio MongoDB.

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

El acceso directo por clave puede ser eficiente. Guardar en RAM y persistir mediante snapshots o registro de operaciones afecta a rendimiento y recuperación ante fallos. **No determina por sí solo la consistencia entre réplicas**: esa propiedad depende del protocolo y de las opciones de lectura y escritura.

**Sirve para:** `sessionid` del motor de reservas, preferencias, carrito **antes** de cobrar, **caché** de disponibilidad.

**No encaja:** relaciones entre datos, transacciones de **varios** pasos, consultas **por dentro** del valor, operaciones sobre **conjuntos de claves** (“todas las que empiezan por `Laredo:`” si el producto no lo ayuda).

Productos: **Redis**, **DynamoDB**, Voldemort (clon abierto de Dynamo).

## Dos modelos que comparten la palabra «columna»

En el [1.3](../ut1/almacenamiento.md) ya quedó la frontera. Aquí se usan los dos, y no son el mismo oficio.

### Fichero o almacén columnar

Muchos motores transaccionales almacenan por filas, lo que favorece leer o escribir una reserva completa. El modelo relacional también puede utilizar almacenamiento columnar. Cuando escribís **poco** y leéis **unas pocas columnas de muchas filas** (ocupación de 80 hoteles × 365 días), un motor analítico **gira** el almacenamiento: los valores del mismo campo van juntos y se **comprimen** mejor. Eso es Parquet, ORC o un *warehouse* como Redshift. El detalle del fichero está en el [1.7](../ut1/formatos.md).

```text
Por filas:     [Laredo,web,3,186] [Potes,ota,2,90] [Noja,web,4,210]
Por columnas:  [Laredo,Potes,Noja] [web,ota,web] [3,2,4] [186,90,210]
```

!!! question "Autoevaluación de pizarra"
    ¿Añadir **un** registro (una reserva nueva) es más barato en filas o en un fichero columnar? En **filas**: un sitio, un append. En Parquet tocáis **varias** estructuras. Por eso el columnar brilla en el **panel** (OLAP), no en el clic de recepción (OLTP).

Con Spark en memoria, la ventaja relativa *a veces* se estrecha. El oficio sigue: **scan** de una métrica en millones de filas.

**Sirve para:** BI, *warehouse* columnar, cubos OLAP, el panel de las 8.

**No encaja:** actualizar la celda del sensor de la 214, ni picar el cobro.

**Productos de este oficio:** Parquet, ORC, Amazon Redshift.

### Wide-column (familias de columnas)

HBase y Cassandra comparten la familia general, pero no una API ni un esquema idénticos. HBase admite calificadores de columna dinámicos por familia; las tablas CQL de Cassandra declaran columnas y claves. En Cassandra se diseña la clave de partición según la consulta, por ejemplo hotel, habitación y día para leer medidas de un periodo acotado.

Otra familia, la de [Bigtable](https://research.google.com/archive/bigtable.html): mapa **ordenado**, **multidimensional** y **repartido**. Cada fila puede tener **muchísimas** columnas (a menudo dispersas) y hay **miles de millones** de filas, con **versiones**. No es un Parquet: guardáis **filas** bajo una clave, y cada fila trae las columnas que tenga.

Dos niveles: la clave de fila → un mapa de **familias de columnas** → columnas.

Una **columna** es `nombre` + `valor` + **`timestamp`** (caducidad y “quién gana” si hay dos escrituras):

```json
{ "name": "temp_c", "value": "21.4", "timestamp": 1710000000 }
```

Una **fila** es un conjunto de columnas bajo una clave (`hab:214:2026-04-01`). Una **familia** agrupa columnas de un mismo asunto, **sin** exigir las mismas columnas en cada fila:

```text
sensores
  hab:214 : { temp_c, humedad, ultima_lectura }
  hab:108 : { temp_c, puerta }          ← no tiene humedad
```

Se accede por **clave de fila** (toda la familia o una columna), no barriendo «la columna importe de todo el lago» como hace Parquet. Cassandra ofrece **CQL**, parecido a SQL **sin** *joins* ni subconsultas; el `WHERE` es limitado:

```sql
SELECT temp_c FROM sensores WHERE hab_id = '214';
```

En Cassandra antiguo existían las **supercolumnas** (un mapa anidado dentro de otra columna). CQL ya no las usa: hoy anidáis con un mapa o con otra tabla.

Actualizar una celda es **encontrar la fila** y reescribir esa columna. A veces se reescribe más de la cuenta.

**Sirve para:** series que **cambian** (el sensor de la 214), filas muy anchas y dispersas, metadatos cuyas columnas aparecen y desaparecen.

**Conviene evaluar otras opciones** para agregaciones globales sobre muchas columnas o transacciones con relaciones complejas. Estos motores también pueden recorrer datos, pero un formato columnar y un motor analítico pueden ser más adecuados para el informe.

**Productos:** **HBase** (encima de [HDFS](hdfs.md)), **Cassandra**. Redshift queda en el apartado anterior.

## Modelo de grafos

Partimos de una pregunta de recorrido: «¿qué hoteles recomiendan las personas relacionadas con este huésped?». Los nodos representan entidades y las aristas relaciones con significado. El coste depende de cuántos vecinos se visitan, de los filtros y de los índices; tener un grafo no hace barata cualquier consulta global.

Guarda **entidades** y **relaciones**. Las entidades son **nodos** (con propiedades). Las relaciones son **aristas** (también con propiedades y **sentido**). Un nodo ≈ una instancia. La dirección tiene significado, aunque una consulta puede recorrer una relación en ambos sentidos. Solo añadimos otra arista si representa otra relación del dominio.

```text
(Huésped:Ana) -[:RECOMENDO {año:2025}]-> (Hotel:Potes)
(Huésped:Luis) -[:AMIGO]-> (Huésped:Ana)
```

Los nodos se organizan por relaciones: el **mismo** dato se interpreta distinto según el camino (*quién recomendó*, *quién es VIP*, *quién está a dos saltos*). No hay techo práctico de tipos de arista en el mismo grafo.

**Recorrer** (*traverse*) es la consulta: “huéspedes del club de senderismo **y** con más de dos estancias en Liébana”. En Neo4j las relaciones **ya están persistidas**: no se calculan al vuelo como un `JOIN` de ocho tablas.

En SQL podemos representar relaciones mediante claves y tablas de asociaciones, incluso de forma genérica. Un motor de grafos facilita expresar y ejecutar recorridos de relaciones. Ambos modelos requieren diseñar identificadores, propiedades e índices según las preguntas; ninguno elimina el modelado.

**Sirve para:** redes (quién conoce a quién), rutas y distancias (hoteles cercanos, camino más corto), **recomendaciones** (“quien reservó Potes también reservó Fuente Dé”).

**No encaja:** cambiar **una** propiedad en **todos** los nodos (operación cara).

Productos: **Neo4j**, ArangoDB, OrientDB, TinkerPop, Amazon Neptune.

## Consistencia según la familia

No se deduce la consistencia únicamente del modelo. Un documento, una clave o un nodo de grafo pueden almacenarse con garantías distintas según el producto y el despliegue.

En MongoDB distinguimos **dónde leer** (`readPreference`), **qué confirmación exigir al escribir** (`writeConcern`) y **qué visibilidad exigir al leer** (`readConcern`). Leer del primario no convierte automáticamente toda operación en linealizable. El [2.8](replicas-shards.md) combina estas opciones.

Cuando varios nodos aceptan cambios concurrentes, también necesitamos resolver conflictos. Los relojes vectoriales detectan relaciones causales y concurrencia; no eligen simplemente «el más reciente». CouchDB conserva revisiones en conflicto para resolverlas. Cassandra utiliza marcas temporales para reconciliar escrituras; no debemos resumirlo como «gana el número mayor».

Finalmente, **persistencia y consistencia son ejes distintos**: guardar periódicamente una instantánea en disco determina qué puede recuperarse tras un fallo; no determina por sí solo qué versión lee otro cliente. Esto es especialmente importante al estudiar Redis.

## Teorema CAP

CAP analiza qué puede garantizar un sistema distribuido **cuando se interrumpe la comunicación entre grupos de nodos**. No significa «elige dos características para siempre».

| Letra | Significado en CAP | Pregunta del hotel |
| --- | --- | --- |
| **C** | Consistencia linealizable: comportamiento como una copia única | ¿Ambas recepciones observan un orden compatible de reservas? |
| **A** | Toda petición a un nodo no fallido obtiene una respuesta válida de la operación | ¿Pueden seguir aceptando reservas ambos lados? |
| **P** | El modelo contempla la pérdida de comunicación entre nodos | ¿Qué hacemos mientras Laredo no puede hablar con Potes? |

Si queda una sola plaza y cada lado acepta una reserva sin comunicarse, podemos venderla dos veces. Para preservar la visión única, alguno de los lados debe esperar o rechazar la operación: se sacrifica disponibilidad en el sentido de CAP. Si ambos lados responden, habrá que aceptar versiones divergentes y resolverlas después. Un mensaje de error no cuenta como disponibilidad de la operación solicitada.

### Clasificación habitual (no es dogma)

Las etiquetas **CP** y **AP** resumen comportamientos bajo particiones, no todo un catálogo de productos. **CA** puede describir un escenario en el que no se consideran particiones; no prueba que una base SQL distribuida escape al problema.

| Comportamiento | Ejemplo de decisión | Consecuencia |
| --- | --- | --- |
| Preservar C ante P | El lado sin mayoría no acepta nuevas reservas confirmadas | Parte de las escrituras deja de estar disponible |
| Preservar A ante P | Ambos lados registran comentarios localmente | Se admiten diferencias temporales y posibles conflictos |
| Sin partición en el escenario | Una única instancia responde a clientes | No se ha probado la tolerancia a una partición entre réplicas |

Para clasificar MongoDB, HBase, DynamoDB, Redis o PostgreSQL hay que indicar versión, topología y operación. Una lectura local y una escritura con mayoría pueden tener condiciones distintas incluso en el mismo sistema.

### BASE (el otro extremo de ACID)

El nombre reúne tres ideas frecuentes en diseños que aceptan convergencia posterior:

- **Basically Available:** el servicio intenta seguir ofreciendo operaciones durante fallos parciales, con las limitaciones definidas por el diseño.
- **Soft state:** el estado observado puede cambiar por la propagación de actualizaciones, aunque este cliente no escriba.
- **Eventual consistency:** si dejan de llegar cambios y se restablece la comunicación, las réplicas convergen conforme a sus reglas de resolución.

BASE no es una especificación equivalente a ACID ni convierte automáticamente cualquier motor en AP. Un sistema puede usar transacciones en un ámbito y replicación eventual en otro. Para una plaza de parking debemos proteger el invariante «no vender más plazas que las disponibles»; para un contador de visitas quizá sea aceptable un retraso. La decisión nace de la operación de negocio.

Para repasar la distinción entre consistencia de transacciones y consistencia entre réplicas, vuelve al [ejemplo de la UT1](../ut1/almacenamiento.md).

## Resumen de aula

NoSQL agrupa modelos no relacionales con distintas interfaces, esquemas y garantías. La licencia, la distribución y las transacciones dependen del producto. Debemos justificar la elección con el patrón de acceso y las garantías necesarias.

NewSQL (CockroachDB, etc.) intenta **SQL + escala horizontal + ACID**. No es el núcleo de esta página; si Moodle lo pide, es una presentación de 5–6 diapositivas: qué problema cierra respecto a NoSQL y respecto a un PostgreSQL de un solo nodo.

!!! success "En voz alta"
    “NoSQL es *not only*. Elegís la familia por la pregunta. Partís cuando no cabe; replicáis para no morir. CAP os obliga a elegir. La caja sigue en ACID.”

## Relación con el RA2

| Criterio | En este apartado |
| --- | --- |
| **a)** | Depositar **cualquier** forma (JSON, grafo, serie) y responder **a su** pregunta, rápido |
| **c)** | Réplica, elección de primario, conflictos; el lab está en el [2.8](replicas-shards.md) |
| **d)** | Esquema al guardar **flojo**, esquema al leer; documentos que **crecen** |
| **e)** | *Auto-sharding*, más nodos, cloud |

## Cómo justificar una elección

Utiliza una ficha con **dato → consulta → garantía → modelo → coste**. Por ejemplo: «sesión de usuario → recuperar por identificador → puede caducar → clave-valor → definir expiración y reconstrucción». Para la última plaza de parking, la garantía cambia: hace falta comprobar y descontar de forma atómica. Una respuesta que solo diga «MongoDB porque admite JSON» está incompleta.

En las prácticas se espera una decisión razonada, no una única combinación de productos. Comprueba que no presentas réplica como aumento de capacidad útil ni una caché como única fuente de reservas confirmadas.

## Para practicar (Moodle manda la nota)

1. ¿Qué significa el *No* de NoSQL? Relación con el relacional (complemento, no sustituto).
2. ¿Un sistema puede **replicar y particionar** a la vez? Dibujad el hotel: tres *shards* (comarcas) × dos copias.
3. Elegid **familia y por qué**:
    - wiki de fichas de habitación (texto, fotos, campos que aparecen);
    - expediente académico de un país (centros, alumnos, notas, muchas relaciones fijas);
    - caché de “¿queda habitación doble en Laredo esta noche?”;
    - “quién recomendó Potes a quién” para una campaña.
4. Investigad **persistencia políglota** y aplicadla al grupo hotelero (caja + Mongo + Redis + HDFS).
5. Elegid tres productos entre Bigtable, Cassandra, DynamoDB, HBase, MongoDB, Redis, Neo4j, PostgreSQL e InfluxDB. Indicad modelo, versión, topología y una operación concreta. Con documentación oficial, explicad qué ocurre si se parte la red y justificad si la operación prioriza C o A. Si consultáis [DB-Engines](https://db-engines.com/en/ranking), anotad fecha: popularidad no equivale a rendimiento ni a garantía de consistencia.
6. (Opcional) 5–6 diapositivas: movimiento **NewSQL** y qué ofrece CockroachDB frente a un relacional clásico.

## Referencias

- Guy Harrison, *Next Generation Databases*
- Sadalage y Fowler, *NoSQL Distilled* (*polyglot persistence*)
- [1.3 Almacenamiento](../ut1/almacenamiento.md) (ACID, CAP, BASE con la transferencia)
- [2.6 MongoDB](mongodb.md), [2.7 Modelado](modelado.md), [2.8 Réplicas y shards](replicas-shards.md)
