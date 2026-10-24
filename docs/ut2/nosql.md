---
title: 2.5 Familias NoSQL
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.5. Familias NoSQL

!!! info "Ruta de estudio"
    **Esencial:** elegir entre clave-valor, documento, familias de columnas y grafo según las consultas; distinguir modelo, esquema, particionado y replicación.

    **Aplicación al hotel:** justificar qué guardar, cómo consultarlo y qué debe ocurrir ante un fallo. No se necesita instalar cuatro motores para realizar las actividades.

    **Ampliación:** contrastar productos con su documentación y estudiar SQL distribuido. Las condiciones de entrega se concretan en Moodle.

En [2.4](computacion-distribuida.md) recorrimos un fichero de reservas para sumar noches por hotel. Ahora recepción necesita **recuperar una reserva concreta, actualizar sus extras o consultar las recomendaciones de un huésped**. Son preguntas diferentes: el modelo que organiza los datos debe facilitar las operaciones previstas.

Seguimos con el grupo hotelero de la UT1. No cambiamos de tecnología porque los datos hayan alcanzado un tamaño mágico: primero describimos la consulta, el volumen, la frecuencia de cambios y las garantías. Un sistema relacional puede seguir siendo una buena elección, incluso con datos semiestructurados o despliegues distribuidos.

Como contexto histórico, se suele hablar de tres etapas que **coexisten**, no de sustituciones completas:

1. Primeros sistemas: bases jerárquicas, en red y ficheros con acceso indexado, como ISAM.
2. Expansión del modelo relacional y de las aplicaciones cliente-servidor.
3. Crecimiento de servicios web, móviles, nube e IoT: se amplía la oferta con NoSQL, SQL distribuido y plataformas analíticas.

El volumen y la variedad impulsaron esas soluciones, pero **SQL es un lenguaje, relacional es un modelo y distribuido es una forma de desplegar y ejecutar**. No son opciones mutuamente excluyentes.

Aquí preparamos las decisiones de los criterios **a), c), d) y e) del RA2**. Las consultas documentales se practicarán en 2.6, el diseño en 2.7 y las pruebas de réplicas y particiones en 2.8. Los JSON de MongoDB son un conjunto diferente del CSV de Hadoop; no se presupone una migración entre laboratorios.

## No solo SQL

NoSQL agrupa sistemas con modelos como documentos, clave-valor, familias de columnas y grafos. El término no garantiza un tamaño mínimo, una velocidad superior ni una configuración distribuida. Algunos productos combinan varios modelos.

El acrónimo suena a “cualquier cosa que no sea relacional y no hable SQL”. En la práctica el *No* es **not only**: sistemas **complementarios** al SGBD relacional. Sus garantías varían: algunas priorizan disponibilidad, otras ofrecen lecturas fuertes y transacciones. **NoSQL describe una familia de modelos, no una renuncia universal a ACID**.

Hay **más de una manera** de resolver el problema. A veces la mejor herramienta es PostgreSQL (cobrar, stock de minibar). A veces es Mongo (reserva con extras que cambian). A veces Redis (sesión). NoSQL no **sustituye** la caja: **amplía** el ecosistema. Eso se llama a menudo **persistencia políglota**: cada pregunta, su almacén.

### ACID: garantías de las transacciones

ACID describe propiedades de una **transacción**, también disponible en ciertos motores NoSQL. La consistencia de ACID significa respetar invariantes, como que una cantidad no sea negativa. La C de CAP, que veremos después, se refiere a la visión de las operaciones entre nodos; son conceptos distintos.

Los SGBD relacionales suelen ofrecer **transaccionalidad** con [ACID](../ut1/almacenamiento.md). En el hotel: transferir un depósito de la fianza a la cuenta de Laredo son **dos** cambios. O salen los dos o no sale ninguno.

| Letra | Nombre | En recepción |
| --- | --- | --- |
| **A** | Atomicidad | Todo el paquete o nada |
| **C** | Consistencia | Las reglas se cumplen (un saldo no queda “prohibido”) |
| **I** | Aislamiento | Controla cómo interfieren transacciones concurrentes; depende del nivel elegido |
| **D** | Durabilidad | Lo confirmado se conserva ante los fallos cubiertos por la configuración |

Un contador de visitas puede admitir un retraso visible. Para confirmar la última plaza de parking, en cambio, necesitamos comprobar y descontar la disponibilidad de forma atómica. Leer un valor reciente y actualizarlo después sin proteger la operación puede permitir dos ventas. ACID no sustituye a definir bien esa regla de negocio.

### Cuatro familias (elige el problema)

| Familia | Unidad | Encaje en el hotel | Productos que veréis citados |
| --- | --- | --- | --- |
| **Clave-valor** | `clave → valor` (a menudo un *blob*) | Sesión, caché de disponibilidad | Redis, Riak, DynamoDB |
| **Documento** | JSON/BSON anidado | Reserva con huéspedes y extras | MongoDB, CouchDB |
| **Familias de columnas** | Filas y claves de partición según el motor | Series de sensores, logs | Cassandra, HBase, Bigtable |
| **Grafo** | Nodos y aristas | “Quién recomendó el hotel a quién” | Neo4j, Neptune, ArangoDB |

Más abajo cada modelo se desarrolla. Elegir “NoSQL” sin decir **cuál** es como decir “voy en vehículo” sin decir si es bici o camión.

## Siete características que debemos comprobar

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

Otra opción es escalar **en horizontal**, añadiendo servidores. Para repartir los datos usamos particionado; cuando las partes se distribuyen entre nodos se habla habitualmente de *sharding*. Puede ampliar la capacidad útil, pero exige distribuir también la carga de forma adecuada. No todo el conjunto debe caber en RAM: índices, cachés y lectura desde disco forman parte del diseño.

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
| **Por hash** | Una función transforma la clave para distribuir sus valores | Puede equilibrar claves distintas; las consultas por rangos originales pueden visitar varios shards |

Los métodos son generales; no todos los productos ofrecen los tres. Si usamos solo `hotel` y casi todo corresponde a Laredo, aplicar un hash no divide las reservas que tienen ese mismo valor. Igual que en el shuffle de 2.4, la elección de la clave puede concentrar el trabajo. Debemos estudiar cardinalidad, frecuencia y consultas, además del número de servidores.

### Cuándo particionar

Conviene estudiarlo cuando la capacidad o el caudal de un nodo no cumplen la necesidad, después de revisar consultas, índices, conservación de datos y recursos. Añadir RAM puede ayudar a una carga concreta; superar la RAM no obliga por sí solo a particionar.

El reparto tiene costes: red, enrutamiento, movimiento de datos y consultas que reúnen resultados. Con pocos datos puede no compensar, pero el tamaño tampoco es el único motivo: importan la carga y otros requisitos del servicio. Planificamos y probamos la ampliación antes de saturar el sistema.

La nube permite contratar recursos y delegar parte de la administración, pero no elimina el coste ni asegura que más nodos mejoren el rendimiento. El criterio **e)** se demuestra observando qué recurso se añade y qué aporta, no solo nombrando el auto-sharding. El [2.8](replicas-shards.md) desarrolla el caso de MongoDB.

## Replicación (criterio c)

La **replicación** mantiene copias del mismo conjunto de datos. Si falla un miembro, otro puede prestar servicio **según el protocolo, las copias disponibles y las garantías exigidas**. Puede haber una interrupción durante la detección y elección de un nuevo primario. El cliente debe estar configurado para conectarse al conjunto y gestionar esa transición.

Sirve para:

- **Disponibilidad:** conservar otras copias ante determinados fallos. No protege frente a todo: un borrado erróneo también puede replicarse, por lo que necesitamos copias de seguridad y recuperación probada.
- **Lecturas:** algunos sistemas permiten repartirlas entre réplicas, aceptando las condiciones de visibilidad correspondientes. No aumenta automáticamente la capacidad útil ni el caudal de escritura.
- **Separación de cargas:** ciertas consultas pueden dirigirse a secundarios. Esto no equivale al aislamiento transaccional de ACID ni convierte una réplica en un entorno de pruebas independiente.

| Arquitectura | Quién recibe escrituras | Qué debemos comprobar |
| --- | --- | --- |
| **Primario–secundario** | El primario coordina las escrituras y los secundarios replican | Elección, mayoría necesaria, confirmación y retraso de las copias |
| **Varios primarios o entre pares** | Varios nodos pueden recibir escrituras según el protocolo | Coordinación, conflictos y garantías de cada operación |

No todas las topologías con varios nodos escritores funcionan igual. Una escritura puede requerir comunicación con otros miembros antes de confirmarse.

### Consistencia

La consistencia describe qué versiones pueden observar los clientes. **Leer tus propias escrituras** es una garantía concreta; la consistencia linealizable exige además que las operaciones de todos los clientes se comporten como si actuaran sobre una única copia, respetando el orden temporal.

| Modelo | Garantía | Encaje |
| --- | --- | --- |
| **Linealizable** | Las operaciones se comportan como sobre una copia única y respetan el orden temporal | Lecturas y escrituras que necesitan esa garantía, con las opciones adecuadas |
| **Eventual** | Sin nuevos cambios y con comunicación recuperada, las réplicas convergen según el protocolo | Contadores o contenidos donde el negocio acepta desfases y sus consecuencias |

«Consistencia fuerte» puede usarse con distintos alcances; aquí concretamos la linealizabilidad. No significa que un inventario refleje físicamente un consumo que nadie ha registrado. Tampoco evita por sí sola una venta doble si la comprobación y el descuento son dos operaciones sin protección conjunta.

La consistencia eventual no se elige solo por tener muchas escrituras o pocas lecturas. Preguntamos qué daño causaría una versión anterior y cómo resolveríamos los conflictos. Un comentario puede mostrarse después; una plaza confirmada necesita un procedimiento que preserve su disponibilidad.

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
| **Consistencia** | ¿Qué versión puede leerse y qué cambios deben confirmarse juntos? |
| **API** | ¿Qué consultas y operaciones ofrece? ¿Qué trabajo exige cambiar de producto? |
| **Comunidad y soporte** | ¿Hay *enterprise*? ¿Se encuentra gente? ¿Hay documentación y conectores (Python)? |

Casos típicos de arranque:

- Web con campos **a medida** → documental.
- Capa de **caché** → clave-valor.
- Binarios + metadatos consultables (fotos de habitación) → documento o clave-valor; los bytes gordos a menudo en [HDFS](hdfs.md) / objeto, el JSON en Mongo.
- Muchas medidas por sensor y periodo → estudiar familias de columnas, un motor de series temporales u otras opciones según consulta, conservación y garantías; medir antes de decidir.

### Limitaciones que debemos evaluar

- **Portabilidad:** APIs y modelos diferentes pueden exigir adaptar consultas y datos.
- **Operación:** copias, índices, actualizaciones, seguridad y monitorización siguen siendo necesarios.
- **Mantenimiento y soporte:** comprobar versiones mantenidas, licencias y documentación, tanto en software abierto como comercial.
- **Equipo y herramientas:** valorar conocimientos, conectores y herramientas de administración disponibles; no deducir su calidad solo de la familia.

La persistencia políglota añade integración y mantenimiento. Si un único motor cumple los requisitos, introducir cuatro puede complicar el trabajo sin aportar una mejora demostrada.

## Modelo documental

La unidad de lectura es una ficha con campos relacionados. En el hotel, reserva, huéspedes y extras pueden viajar juntos. Antes de embeber, estimad tamaño y crecimiento y decidid qué cambios deben ser atómicos. El documento no elimina las relaciones: permite representarlas dentro de la ficha o mediante referencias.

El relacional guarda filas y columnas. El documental guarda **documentos** (casi siempre **JSON**): un objeto, como en programación. En MongoDB, los documentos se agrupan en **colecciones**, dentro de una base de datos; otros productos utilizan sus propios contenedores.

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

En este ejemplo decidimos guardar un único resumen `cobro` y una lista de extras dentro de la reserva. En un diseño relacional podrían representarse con columnas o tablas relacionadas. No significa que una reserva solo pueda tener un cobro: si hay pagos parciales o devoluciones, habrá que modelarlos. Estos JSON son ejemplos de estructura, no los archivos de importación de 2.6.

En MongoDB, `_id` identifica el documento dentro de su colección. Podemos filtrar por otros campos, pero sin un índice adecuado puede ser necesario recorrer muchos documentos. Los índices disponibles dependen del producto: compuestos, únicos, de texto, geoespaciales o TTL, entre otros. Un índice TTL permite eliminar datos caducados mediante un proceso de fondo; no promete borrarlos en el instante exacto de caducidad. Para resumir documentos utilizaremos agregaciones en los siguientes apartados.

Actualizar **un** documento suele ser **una** sentencia: no recorréis tres tablas.

**Sirve para:** flujos de eventos entre *apps*, CMS / blog (comentarios, usuarios), analítica web (un campo nuevo cuando aparece una métrica), *e-commerce* que **crece** de esquema.

**Hay que evaluarlo con cuidado** cuando abundan relaciones cruzadas, restricciones entre documentos o transacciones largas. MongoDB admite transacciones, pero su coste y el modelo deben compararse con una solución relacional. No basta con que la información pueda escribirse como JSON.

Productos: **MongoDB** (el de esta UT), **CouchDB**.

## Modelo clave-valor

La pregunta típica es «dame el valor de esta clave», por ejemplo `sesion:991`. Si necesitamos buscar por el contenido de todos los valores, quizá hagan falta estructuras auxiliares o un motor con índices. Una sesión puede caducar; una reserva confirmada requiere una política de conservación diferente. Los ejemplos de Redis presuponen un servidor Redis y su cliente, independientes del laboratorio MongoDB.

El modelo básico es una asociación **clave → valor**. Puede imaginarse como un diccionario, sin presuponer que su implementación física sea una tabla hash. Su acceso característico recupera el valor mediante una clave conocida.

Imaginad una tabla SQL de dos columnas (`id`, `nombre`). En clave-valor el “nombre” puede ser un entero, un JSON o un **BLOB**. Si la clave existe, el `SET` **pisa** el valor.

En el modelo básico, el cliente obtiene, asigna o borra por clave y el valor se trata como opaco. Buscar «todas las reservas de Trasmiera» dentro de esos valores exige otros mecanismos. Algunos productos ofrecen tipos estructurados e índices adicionales: debemos distinguir la idea básica de las capacidades del motor.

Algunos productos agrupan claves en *buckets*. Este ejemplo de la API HTTP de Riak es ilustrativo, no un comando para el laboratorio MongoDB; exige una instancia compatible:

```text
curl -X PUT http://localhost:8098/riak/sesiones/S-991 \
  -H "Content-Type: application/json" \
  -d "{\"hotel\":\"Laredo\",\"canal\":\"web\"}"
```

**Redis** tipa el valor: cadenas, *hashes*, conjuntos, listas. Entonces sí hay intersección, unión, rangos. Ya no es “solo un *blob*”: se usa como caché, cola y contador.

Los siguientes comandos corresponden a `redis-cli`, con un servidor Redis disponible. No se ejecutan en `mongosh`:

```text
SET sesion:991 "huésped-Laredo"
HSET reserva:18442 hotel "Laredo"
HSET reserva:18442 canal "web"
SADD hotel:Laredo:extras parking cuna
```

El ejemplo Python necesita el paquete `redis` y un servidor local en el puerto 6379. Sus etiquetas son datos ficticios de caché; no confirman disponibilidad comercial:

```python
import redis

r = redis.Redis(host="localhost", port=6379)
r.mset({"Laredo": "disponible", "Potes": "completo"})
r.get("Potes")  # b'completo'
```

El acceso directo por clave puede ser eficiente. Guardar en RAM y persistir mediante snapshots o registro de operaciones afecta a rendimiento y recuperación ante fallos. **No determina por sí solo la consistencia entre réplicas**: esa propiedad depende del protocolo y de las opciones de lectura y escritura.

**Sirve para:** `sessionid` del motor de reservas, preferencias, carrito **antes** de cobrar, **caché** de disponibilidad.

**Requiere evaluación adicional:** relaciones, búsquedas por contenido y operaciones sobre varias claves. Algunos motores incorporan transacciones, scripts o índices, con límites propios. No se puede deducir su ausencia de la etiqueta clave-valor. Una caché de disponibilidad debe contrastarse con el sistema que confirma la reserva.

Productos de referencia: **Redis** y **DynamoDB**; este último ofrece modelos clave-valor y documental. Riak y Voldemort son referencias históricas del ecosistema Dynamo, no instalaciones exigidas en esta unidad.

## Dos modelos que comparten la palabra «columna»

En el [1.3](../ut1/almacenamiento.md) ya quedó la frontera. Aquí se usan los dos, y no son el mismo oficio.

### Fichero o almacén columnar

Muchos motores transaccionales almacenan por filas, lo que favorece leer o escribir una reserva completa. El modelo relacional también puede utilizar almacenamiento columnar. Cuando escribís **poco** y leéis **unas pocas columnas de muchas filas** (ocupación de 80 hoteles × 365 días), un motor analítico **gira** el almacenamiento: los valores del mismo campo van juntos y se **comprimen** mejor. Eso es Parquet, ORC o un *warehouse* como Redshift. El detalle del fichero está en el [1.7](../ut1/formatos.md).

```text
Por filas:     [Laredo,web,3,186] [Potes,ota,2,90] [Noja,web,4,210]
Por columnas:  [Laredo,Potes,Noja] [web,ota,web] [3,2,4] [186,90,210]
```

!!! question "Para distinguir formato y motor"
    ¿Modificar una reserva dentro de un Parquet equivale a actualizar una fila en una base operativa? No. Parquet organiza archivos para lecturas analíticas; una actualización suele requerir reescribir datos o apoyarse en una capa de tablas que gestione los cambios. El coste depende del sistema y de cómo agrupe las operaciones, no solo de decir «filas» o «columnas».

**Encaje habitual:** leer pocas columnas de muchas filas para BI o el panel de las 8. Un almacén columnar puede ofrecer actualizaciones y transacciones; no debemos atribuirle las limitaciones de un archivo aislado.

**Niveles distintos:** Parquet y ORC son formatos de archivo; Amazon Redshift es un sistema de almacén analítico. Spark es un motor que puede consultar formatos diferentes. Ninguno de esos nombres convierte el archivo en una base de familias de columnas.

### Wide-column (familias de columnas)

HBase y Cassandra comparten la familia general, pero no una API ni un esquema idénticos. HBase admite calificadores de columna dinámicos por familia; las tablas CQL de Cassandra declaran columnas y claves. En Cassandra se diseña la clave de partición según la consulta, por ejemplo hotel, habitación y día para leer medidas de un periodo acotado.

El modelo de Bigtable y HBase organiza filas por clave y columnas dentro de familias. Es distinto de un archivo Parquet: no describe simplemente colocar juntos todos los importes para un análisis.

Ejemplo conceptual de HBase, con una familia `medidas`:

```text
clave de fila              familia:calificador     valor
Laredo:214:2026-04-01:0800   medidas:temp_c          21.4
Laredo:214:2026-04-01:0800   medidas:humedad         55
Potes:108:2026-04-01:0800    medidas:temp_c          19.8
```

Las familias se declaran; los calificadores pueden variar por fila. Las celdas pueden conservar versiones identificadas por una marca temporal. **La marca temporal no es el TTL**: la caducidad se configura mediante políticas de conservación. El ejemplo no es una sentencia que debáis ejecutar.

En Cassandra, CQL declara tablas y claves. Para una consulta «medidas de una habitación en un día», un diseño ilustrativo sería:

```sql
CREATE TABLE sensores (
  hotel text,
  hab_id text,
  dia date,
  instante timestamp,
  temp_c double,
  PRIMARY KEY ((hotel, hab_id, dia), instante)
);
SELECT instante, temp_c FROM sensores
WHERE hotel = 'Laredo' AND hab_id = '214' AND dia = '2026-04-01';
```

Las tres primeras columnas de la clave forman la **clave de partición**; `instante` ordena las filas dentro de ella. Acotar por día ayuda a limitar su crecimiento, pero hay que estimar cuántas medidas llegan. Este ejemplo requeriría Cassandra y un *keyspace* seleccionado: aquí se estudia el diseño, no se instala ese laboratorio.

CQL se parece a SQL, pero sus consultas se diseñan alrededor de las claves y no ofrece los joins relacionales habituales. Las antiguas supercolumnas de Cassandra son contexto histórico, no el modelo CQL que usamos como referencia.

**Encaje posible:** medidas y eventos consultados por entidad y periodo, con volumen y patrones de acceso conocidos. No hace falta que los datos sean sensores para usar el modelo, ni que toda serie temporal se guarde en él.

**Precaución:** una consulta global o una relación nueva puede exigir otra tabla, índices o procesamiento adicional. HBase se apoya habitualmente en HDFS; Cassandra utiliza su propio almacenamiento distribuido. Un archivo Parquet puede ser adecuado para analizar exportaciones de cualquiera de ellos.

## Modelo de grafos

Partimos de una pregunta de recorrido: «¿qué hoteles recomiendan las personas relacionadas con este huésped?». Los nodos representan entidades y las aristas relaciones con significado. El coste depende de cuántos vecinos se visitan, de los filtros y de los índices; tener un grafo no hace barata cualquier consulta global.

Guarda **entidades** y **relaciones**. Las entidades son **nodos** (con propiedades). Las relaciones son **aristas** (también con propiedades y **sentido**). Un nodo ≈ una instancia. La dirección tiene significado, aunque una consulta puede recorrer una relación en ambos sentidos. Solo añadimos otra arista si representa otra relación del dominio.

```text
(Huésped:Ana) -[:RECOMENDO {año:2025}]-> (Hotel:Potes)
(Huésped:Luis) -[:AMIGO]-> (Huésped:Ana)
```

Los nodos se organizan por relaciones: el **mismo** dato se interpreta distinto según el camino (*quién recomendó*, *quién es VIP*, *quién está a dos saltos*). Los tipos de relación y sus propiedades forman parte del diseño y están sujetos a los límites del producto.

**Recorrer** (*traverse*) es la consulta: “huéspedes del club de senderismo **y** con más de dos estancias en Liébana”. En Neo4j las relaciones **ya están persistidas**: no se calculan al vuelo como un `JOIN` de ocho tablas.

En SQL podemos representar relaciones mediante claves y tablas de asociaciones, incluso de forma genérica. Un motor de grafos facilita expresar y ejecutar recorridos de relaciones. Ambos modelos requieren diseñar identificadores, propiedades e índices según las preguntas; ninguno elimina el modelado.

**Sirve para:** redes (quién conoce a quién), rutas y distancias (hoteles cercanos, camino más corto), **recomendaciones** (“quien reservó Potes también reservó Fuente Dé”).

**Conviene comparar alternativas:** las actualizaciones globales o agregados que recorren gran parte del grafo pueden ser costosos, como los recorridos amplios en otros modelos. El encaje debe comprobarse con las consultas previstas.

Productos: **Neo4j**, ArangoDB, OrientDB y Amazon Neptune. **Apache TinkerPop** es un framework de computación sobre grafos, no una base de datos equivalente a esos productos.

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

### BASE: convergencia y estado observado

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
    “Elegimos el modelo por las consultas y las garantías. Particionar reparte datos; replicar mantiene copias. Ambos necesitan diseño y comprobación. Durante una partición de red no podemos garantizar a la vez linealizabilidad y disponibilidad de todas las operaciones. El modelo no determina por sí solo las transacciones.”

## Relación con el RA2

| Criterio | En este apartado |
| --- | --- |
| **a)** | Justificar el modelo según los datos, consultas y rendimiento necesario; cada motor tiene tipos y límites |
| **c)** | Réplica, elección de primario, conflictos; el lab está en el [2.8](replicas-shards.md) |
| **d)** | Conservar datos y metadatos para reutilizarlos; distinguir esquema flexible de ausencia de validación |
| **e)** | Explicar qué aporta particionar o añadir recursos y qué debe observarse al ampliar |

Este apartado prepara el razonamiento. Explicar una réplica no demuestra haber probado tolerancia a fallos, ni dibujar shards prueba una ampliación. Las observaciones se recogen en los laboratorios correspondientes. La capacidad tampoco es ilimitada: depende de recursos, costes y políticas de conservación.

## Cómo justificar una elección

Utiliza una ficha con **dato → consulta → garantía → modelo → coste**. Por ejemplo: «sesión de usuario → recuperar por identificador → puede caducar → clave-valor → definir expiración y reconstrucción». Para la última plaza de parking, la garantía cambia: hace falta comprobar y descontar de forma atómica. Una respuesta que solo diga «MongoDB porque admite JSON» está incompleta.

En las prácticas se espera una decisión razonada, no una única combinación de productos. Comprueba que no presentas réplica como aumento de capacidad útil ni una caché como única fuente de reservas confirmadas.

## Actividades

Estas actividades pueden resolverse con los ejemplos de la página, sin instalar Redis, Cassandra ni un motor de grafos. Justificad **dato → consulta → garantía → modelo → coste**. Las entregas evaluables se concretan en Moodle.

1. **Del histórico a recepción.** Comparad sumar noches de todo un CSV con recuperar y modificar una reserva. Explicad por qué MongoDB puede ser una opción para la segunda necesidad y por qué el tamaño no descarta una base relacional.
2. **Elegir por la pregunta.** Proponed modelo para una wiki de habitaciones, un expediente académico con relaciones y restricciones, una sesión recuperada por identificador y una cadena de recomendaciones. Añadid una alternativa y qué dato os haría cambiar de decisión.
3. **Ausencia de un campo.** Una reserva antigua no contiene `mascota`; otra contiene `mascota: false`. ¿Podemos contarlas como equivalentes? Definid una regla y explicad cómo validaríais `noches` sin impedir nuevos campos opcionales.
4. **Replicar y particionar.** Dibujad tres shards con dos copias de datos cada uno. Con 90 GB lógicos repartidos por igual, calculad datos por shard y contenido físico total, sin índices ni sobrecostes. Si cada shard usa exactamente dos miembros votantes y necesita mayoría para elegir primario, ¿puede perder uno y elegirlo? Separad copias de datos y votos.
5. **La clave concentra la carga.** El 90 % de las reservas pertenece a Laredo. ¿Aplicar hash solo a `hotel` resuelve el desequilibrio? Comparad con una clave de mayor cardinalidad e indicad qué consultas podrían necesitar reunir resultados.
6. **Dos significados de columna.** Comparad un Parquet de reservas con la tabla `sensores` del ejemplo CQL. Identificad formato, motor, clave de partición y consulta prevista. Explicad por qué no se asigna una máquina a cada columna.
7. **La última plaza.** Dos recepciones pierden comunicación y quieren confirmar la misma plaza. Explicad qué operación debe protegerse y qué implica esperar o rechazar en un lado. Comparad con registrar comentarios para sincronizarlos después. No basta con etiquetar un producto como CP o AP.
8. **Persistencia políglota.** Proponed cómo combinar caja, documentos, caché e histórico. Indicad qué sistema confirma la reserva, qué copia puede estar atrasada y cómo recuperaríais una caché vacía. Explicad también cuándo simplificaríais a menos sistemas.
9. **Contrastar documentación — ampliación.** Elegid tres productos entre Bigtable, Cassandra, DynamoDB, HBase, MongoDB, Redis, Neo4j, PostgreSQL e InfluxDB. Indicad versión, topología y operación. Buscad evidencia oficial sobre qué sucede al perder comunicación; si falta información, señaladla sin deducir la garantía del modelo. Un ranking de popularidad no demuestra rendimiento.
10. **SQL distribuido — ampliación.** Preparad 5–6 diapositivas sobre NewSQL y CockroachDB: qué problema aborda, qué conserva del modelo relacional y qué costes de coordinación introduce frente a una instancia única.

??? success "Orientaciones para revisar las respuestas"
    **1–2.** Recorrer un histórico y acceder a una reserva son patrones distintos. Documento, relacional, clave-valor y grafo son candidatos para los cuatro casos, respectivamente; no son respuestas exclusivas. La justificación debe mencionar consultas, restricciones y coste.

    **3.** Ausencia puede significar desconocido, no «no». Debe documentarse antes de consultar. Un validador puede exigir un entero positivo en `noches` y admitir campos opcionales.

    **4.** Cada shard contiene 30 GB lógicos; dos copias por shard suman 180 GB físicos de contenido. Con dos votantes, la mayoría es dos: perder uno impide elegir un primario. La mera existencia de una copia no garantiza escrituras disponibles.

    **5–6.** El mismo hotel produce el mismo hash; no se divide por ello su carga. Más valores distintos pueden ayudar, con costes de consulta. Parquet es un formato; Cassandra es un motor y la clave ilustrativa combina hotel, habitación y día. Las columnas no equivalen a servidores.

    **7–8.** Confirmar una plaza exige proteger comprobación y descuento; una lectura reciente aislada no basta. Mantener una visión única puede dejar operaciones sin disponibilidad durante la partición. Una caché puede reconstruirse desde la fuente definida, pero no debe confirmar una reserva solo porque conserva un dato antiguo.

    **9–10.** Las conclusiones deben acompañarse de fuente y condiciones. Las garantías de una operación o configuración no se generalizan a toda una familia.

## Autoevaluación del 2.5

Diez preguntas (A–D, **una** correcta). No puntúan en Moodle. **Comprobar respuesta** muestra el resultado y explica el motivo. Revisad el apartado enlazado antes de repetir.

<div class="dwec-quiz" data-dwec-quiz data-src="../../assets/quizzes/ut2-2-5.json"></div>

Antes de pasar a [2.6 MongoDB](mongodb.md), debéis poder explicar por qué elegimos documentos para las consultas de aula y qué no garantiza esa elección. Allí utilizaremos sus propios archivos de reservas y opiniones; más adelante añadiremos modelado, réplicas y acceso desde Python.

## Referencias

- Guy Harrison, *Next Generation Databases*
- Sadalage y Fowler, *NoSQL Distilled* (*polyglot persistence*)
- [1.3 Almacenamiento](../ut1/almacenamiento.md) (ACID, CAP, BASE con la transferencia)
- [2.6 MongoDB](mongodb.md), [2.7 Modelado](modelado.md), [2.8 Réplicas y shards](replicas-shards.md)

- [MongoDB: validación del esquema](https://www.mongodb.com/docs/manual/core/schema-validation/).
- [MongoDB: elección de primario](https://www.mongodb.com/docs/manual/core/replica-set-elections/) y [elección de clave de particionado](https://www.mongodb.com/docs/manual/core/sharding-choose-a-shard-key/).
- [Redis: tipos de datos](https://redis.io/docs/latest/develop/data-types/).
- [Cassandra: modelado orientado a consultas](https://cassandra.apache.org/doc/latest/cassandra/developing/data-modeling/intro.html).
- [Neo4j: conceptos del modelo de grafos](https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/).
