---
title: 1.6 Ingesta de datos
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.6. Ingesta de datos

**Ingesta** es incorporar datos de orígenes distintos (estructura, ritmo, calidad) a un almacén o a un proceso. Es el criterio **b)** del RA1: *determinar los procedimientos y mecanismos*.

Si la ingesta es frágil, el resto de la tubería (ciencia de datos, cuadro de mando) trabaja sobre arena: el modelo será brillante y la cifra, mentira. La productividad del equipo **depende** de que este proceso sea flexible y ágil: cuando funciona, analistas y científicos pueden montar sus propias tuberías hacia la herramienta con la que trabajan.

Es el **primer** paso al diseñar una arquitectura Big Data. Hay que tener claros el tipo y la fuente **y** el objetivo de negocio. Sin eso, no hay herramienta que salve el diseño. Unificar muchas fuentes en un solo sitio (hoy, a menudo un **data lake**) es un procedimiento largo, partido en fases.

![Fases de un pipeline de datos](../assets/ut1/pipeline.png)

## Empieza por el problema, no por la herramienta

Un **pipeline** (tubería de datos) es una construcción lógica: un proceso partido en fases, con las tecnologías de cada fase. Consume de un origen, limpia o transforma y deja el resultado en un destino. En su forma más simple: recoger, guardar, procesar y **construir algo útil**.

Se diseña **desde la pregunta de negocio hacia atrás** hasta el origen. Ese análisis es la base para elegir tecnologías.

Ejemplo: dirección quiere “ocupaciones de hotel por comarca, cada mañana a las 8”.

1. ¿Qué tabla o gráfico necesitan ver? (destino / presentación)
2. ¿Qué hay que agregar y limpiar? (transformación)
3. ¿De qué programa de reservas, Excel o API salen las reservas? (origen)

“Montar Kafka porque está de moda” no es un procedimiento. Kafka *puede* ser el mecanismo **si** el ritmo y el desacoplo lo piden.

### Un recorrido típico (con una cola en medio)

Los datos no siempre van “origen → informe” en un solo salto. Un ejemplo que verás en arquitectura:

1. **Ingesta.** Recoges eventos y los dejas en un *topic* de **Kafka** (un canal con nombre: `reservas`, `logs-web`…).
2. **Almacenamiento temporal.** Kafka hace de **sala de espera** (*buffer*): el productor ya soltó el mensaje; el que procesa aún no tiene que estar listo.
3. **Procesamiento.** Un job (lote o continuo) lee esa sala de espera, calcula, filtra, agrupa.
4. **Análisis y visualización.** Spark (u otra herramienta) deja el resultado en un panel, en MongoDB / DynamoDB o en S3.

Un pipeline sencillo a veces solo filtra un poco y escribe en la cola. Otro, más tarde, hace los cruces pesados para el informe. No tienes que meter **toda** la lógica en el primer salto.

### Por qué no se analiza en el mismo sitio donde se crea el dato

El análisis (resúmenes, cruces, modelos) es **caro** para la máquina. Si lo haces sobre la caja o el programa de reservas, el cajero espera. Por eso se **copia** el dato a otro sitio: el sistema del día a día sigue cobrando; el de informes trabaja aparte. Eso es lo de [operar frente a analizar](procesamiento.md) (en los libros, OLTP frente a OLAP).

En muchas empresas el primer destino consolidado es un **data lake**; luego se curan copias hacia el warehouse que alimenta el panel. Dos saltos, dos procedimientos, no uno solo “mágico”.

### Pipeline no es lo mismo que ETL

Se usan como sinónimos y **no lo son**.

- Un **pipeline** es *cualquier* movimiento o procesamiento de datos entre sistemas (incluida una cola, un filtro ligero, un lote nocturno).
- Un **ETL** es un **caso particular**: extraer, transformar y cargar. Toda ETL es un pipeline; no todo pipeline es una ETL.

### Data wrangling (el dato “en disputa”)

Conforme el dato avanza por la tubería, casi siempre hay que **limpiarlo**: otra fuente usa `M`/`F` en vez de `1`/`2`, hay huecos, hay duplicados, un campo llega como texto `"10"`. A veces rellenas un vacío con un cero o con un valor que *sí* aporta (la media del grupo, un “desconocido”). Ese trabajo de pasar del crudo al dato que ya se puede usar se llama **data wrangling** (manipulación o “disputa” de datos). No es un producto: es el oficio de dejar el dato **listo**.

### El pipeline es iterativo

Negocio lanza una hipótesis (“¿cancelan más los que reservan el viernes?”). Miras lo que hay. Si falta un campo, **vuelves a ingerir** (otra fuente o el mismo origen con más columnas), lo integras con lo anterior y analizas otra vez. Si el número no convence, se itera. La ingesta no es un acto único el día 1.

## Extraer, transformar y cargar: el orden cambia el oficio

Tres verbos, siempre los mismos:

1. **Extraer:** leer el origen (una tabla, un CSV, una API).
2. **Transformar:** limpiar, unir, recodificar, agregar.
3. **Cargar:** escribir el resultado en el destino.

Las siglas inglesas **ETL** y **ELT** solo cambian **cuándo** haces el paso 2. Llevar el dato de A a B se puede hacer con un script, con Python o con una suite; en **Big Data** hace falta que la herramienta sea:

- **flexible** (CSV, JSON, Parquet, SQL, Excel, una petición HTTP…),
- **escalable y tolerante a fallos** (si cae a la mitad, no dejes el destino a medias sin saberlo),
- **conectada** a muchos orígenes y destinos.

Además conviene que deje **rastro** (qué se ejecutó, qué falló) y que puedas **planificarla**: cada noche, al llegar un fichero, o en continuo.

![Esquema ETL](../assets/ut1/etl.png)

| | **ETL** | **ELT** |
| --- | --- | --- |
| Orden | Extraer → **transformar** → cargar | Extraer → **cargar** → transformar |
| Dónde se transforma | Motor intermedio (Pentaho, Talend, un script…) | En el destino (SQL del warehouse, Spark o DuckDB sobre el lago) |
| Cuándo brilla | El destino es rígido y no debe tragar basura | Destinos elásticos y **varios** consumidores del mismo bruto |
| Tiempo hasta “ver el crudo” | Más tarde (esperas a la T) | Antes (el bruto ya está) |
| Quién “duele” si cambia la pregunta | Hay que retocar el flujo de T **antes** de recargar | A menudo basta una consulta nueva sobre lo ya cargado |
| Oficio | Más trabajo del ingeniero de datos *antes* | El analista o científico puede transformar con SQL o Python |

Unificar orígenes distintos **gasta** una parte enorme del proyecto. No es “un script de una tarde” cuando hay veinte fuentes y diez años de histórico. La calidad y la veracidad hay que **cuidarlas aquí**: si cuelas basura, el error se multiplica en el informe.

El mercado ha girado hacia **ELT** en cloud (el almacén es potente; el lago se llena antes; más departamentos tocan la T). **ETL sigue** cuando el destino no puede tragarse basura, no hay motor detrás o trabajas en aula con [Pentaho](pentaho.md): PDI se enseña como **ETL visual**.

Hoy es habitual un **híbrido**: la suite (Pentaho, Talend…) más scripts Python (pandas, PySpark, DuckDB) y un orquestador (**Airflow**) que dispara los pasos en orden y avisa si uno falla. No tienes que montar Airflow en esta UT; sí saber *para qué existe*.

### Tres formas de acercar el dato: push, pull y poll

Antes de elegir Sqoop o Kafka, decide **quién da el primer paso**. Son tres planteamientos, no tres productos.

| | **Push** (empujar) | **Pull** (tirar) | **Poll** (preguntar) |
| --- | --- | --- | --- |
| Quién inicia | El **origen** envía al destino | El **destino** va a buscar al origen | El destino **mira de vez en cuando** si hay cambios; si los hay, hace un *pull* |
| Analogía | El hotel te manda un WhatsApp “hay una reserva nueva” | Tú abres el programa de reservas y te copias la tabla | Cada 10 minutos miras la carpeta compartida; si hay un CSV nuevo, te lo llevas |
| Encaja | Eventos, webhooks, sensores, “en cuanto ocurra” | Lote nocturno, Sqoop, Pentaho leyendo Oracle | Carpetas, buzones, APIs que no avisan solas |
| Cuidado | El origen tiene que saber *adónde* empujar y no inundarte | Si tiras en hora punta, tumas el origen | Si preguntas poco, te enteras tarde; si preguntas mucho, molestas |

!!! example "Mismo hotel, tres diseños"
    - **Push:** el programa de reservas publica cada alta en un *topic* Kafka.  
    - **Pull:** a las 02:00 Pentaho lee la tabla de ocupaciones.  
    - **Poll:** cada cuarto de hora un script lista el FTP; solo descarga si el fichero cambió de fecha.

No hay uno “más Big Data”. El *push* encaja con el stream; el *pull* y el *poll*, con el lote. Mezclarlos en la misma empresa es lo normal.

### Extracción

Recopila los datos del sistema original y los lleva a un sitio de trabajo (a menudo un almacén de informes o una zona temporal). Las fuentes van de un CSV a una base relacional, pasando por un mensaje de red social o un sensor.

Dos exigencias, en castellano:

1. **Rápida y ligera.** Que el origen casi no se entere. Transparente para quien opera e independiente de “en qué máquina está”.
2. **Que no tumbe el origen.** No se puede poner en riesgo la caja ni **cambiar** sus datos. Si colapsa el programa de reservas, la empresa pierde dinero *operando*, no “analizando”.

Por eso no vuelcas **toda** la caja en hora punta si puedes leer solo lo nuevo, una ventana de tiempo o una API con cuota. La primera carga histórica es un procedimiento **distinto** del día a día.

En la extracción también **miras** si el dato es el que esperabas (columnas, tipos, que no venga vacío). Si no, se **rechaza** o se aparta: no lo cuelas “para que el job acabe”.

Al salir de esta fase, el dato ya está en un formato con el que se puede empezar a transformar.

### Transformación

Cambios para que el dato tenga el **formato y el contenido** que el destino espera. Ejemplos de aula:

- Cambiar la codificación (tildes que se rompen).
- Quitar duplicados.
- Cruzar dos fuentes (reservas + pagos, productos + fabricantes) para obtener una tercera.
- Agregar (ventas por día, no cada ticket).
- Quedarte solo con parte de las columnas.
- Fabricar un código o un identificador estable.
- Ordenar mejor la información.
- Calcular un indicador que el informe ya pide (ocupación %, ticket medio).

Debe **mejorar** calidad, integrar y quitar ambigüedad. **No** debe inventar hechos, duplicar a ciegas, borrar lo relevante ni ser impredecible.

En streaming cada milisegundo de T cuenta: a veces dejas la transformación pesada para un lote posterior. Si transformas *al vuelo*, pregúntate si pierdes el original.

### Carga

Escribe en el destino y **se adapta a él**. Minimiza el tiempo que el destino está “ocupado” escribiendo.

Cada sistema tiene su forma cómoda de recibir datos:

- instrucciones SQL o carga masiva (*bulk*) — PostgreSQL, SQL Server, Redshift…;
- ficheros que el destino lee de una carpeta;
- cargadores propios — HDFS, S3.

Ahí importan los **índices** (el “índice del libro”: si lo reconstruyes **en cada fila**, la carga masiva se muere), las **claves de distribución y el particionado** (por fecha, por tienda: el clúster sabe en qué trozo buscar) y confirmar por **bloques**, no fila a fila. Funciona en 100 filas de práctica y revienta en 10 millones.

## Hola ETL: el mismo oficio en Python

En [Pentaho](pentaho.md) harás esto en Spoon. Aquí ves las **tres letras** en código, con los CSV de productos y fabricantes de las prácticas.

Los productos vienen separados por **coma** y traen `ManufacturerID`. Los fabricantes vienen separados por **punto y coma**. El cruce es ese identificador. Objetivo: un JSON con los productos de categoría `Mix` y una columna nueva `ProductAndManufacturer` (`Abbas MA-01 (Abbas)`).

**Extracción** = leer los dos ficheros. **Transformación** = filtrar `Mix`, unir (*join*: “pon al lado el nombre del fabricante”) y crear la columna. **Carga** = escribir el JSON.

### Con pandas

```python
import pandas as pd

# E
df_products = pd.read_csv("pdi_product.csv")
df_manufacturers = pd.read_csv("pdi_manufacturer.csv", sep=";")

# T
df_mix = df_products[df_products["Category"] == "Mix"]
df_joined = df_mix.merge(df_manufacturers, on="ManufacturerID", how="left")
df_joined["ProductAndManufacturer"] = (
    df_joined["Product"] + " (" + df_joined["Manufacturer"] + ")"
)

# L
df_joined.to_json("pdi_product_mix.json", orient="records", force_ascii=False)
```

`how="left"` = “me quedo con todos los productos Mix; si un fabricante no aparece, el nombre queda vacío”. No inventes un fabricante.

### Con DuckDB

[DuckDB](formatos.md) es un motor SQL **dentro** de tu programa. Puedes tratar un CSV como si fuera una tabla, sin cargarlo antes en una base “de verdad”:

```python
import duckdb

duckdb.sql("""
CREATE OR REPLACE VIEW productos AS
SELECT * FROM read_csv('pdi_product.csv', header=true);
""")
duckdb.sql("""
CREATE OR REPLACE VIEW fabricantes AS
SELECT * FROM read_csv('pdi_manufacturer.csv', header=true, delim=';');
""")

duckdb.sql("""
COPY (
    SELECT
        p.ProductID,
        p.Product,
        p.Category,
        f.Manufacturer,
        p.Product || ' (' || f.Manufacturer || ')' AS ProductAndManufacturer
    FROM productos p
    LEFT JOIN fabricantes f
        ON p.ManufacturerID = f.ManufacturerID
    WHERE p.Category = 'Mix'
) TO 'pdi_product_mix_ddb.json' (FORMAT JSON)
""")
```

Mismas tres letras, otro idioma (SQL). En clase compara **tamaño del código**, **tiempo** y si el JSON te sale legible. Luego haz el mismo flujo en Pentaho y verás que el oficio no cambia: cambia la herramienta.

## El formato también se decide en la ingesta

La **L** de ETL no es “escribir un fichero”. Es escribirlo en un formato que el **siguiente** paso pueda partir, comprimir y consultar sin arruinarte. Conforme el dato viaja por la tubería, hay que **serializarlo** (pasarlo a bytes) y a menudo **convertirlo**. Cada conversión gasta CPU y puede **perder tipos**: no cambies de formato en cada capa “porque sí”.

El detalle de cada formato está en [1.7](formatos.md). Aquí, lo que pide el criterio **b)** es **elegir el de la carga** y saber decir por qué.

### Qué le pides al fichero que dejas

Para que Hadoop, Spark o Athena puedan repartir el trabajo, el fichero tiene que ser **partible** (*splittable*): cortarlo en trozos. Un JSON con diez millones de objetos dentro de un único `[` `]` **no** se parte bien. Un objeto por línea (JSONL), un Avro o un Parquet, sí.

También quieres que sea **independiente del lenguaje** (lo escribe Java, lo lee Python), **expresivo** (nulos y anidados de verdad), **compacto** y, si el origen cambia columnas, que el esquema pueda **evolucionar** sin reescribir el histórico.

| Si la carga es… | Formato razonable | Por qué en la ingesta |
| --- | --- | --- |
| Un extracto para un compañero o una API | CSV / JSON | Se abre y se depura |
| Un *topic* de Kafka, el esquema va a cambiar | **Avro** | Filas + esquema en el mensaje; típico en *push* |
| El lago / S3 para Spark o Athena (informes) | **Parquet** | Columnas: lees 3 de 80; pagas por lo *escaneado* |
| Un paso intermedio entre dos scripts del mismo pipeline | **Feather** | Muy rápido de leer/escribir; no es archivo de años |
| Tablas Hive | **ORC** (o Parquet si el equipo es Spark) | Encaje con Hive |
| La caja o las reservas | **No** Parquet/ORC como almacén de operación | Actualizar una fila es carísimo |

!!! example "1 TB mal ingerido"
    1 TB en CSV plano puede quedar en ~**130 GB** en Parquet. En Athena, del orden de **5 $ por TB leído**. Si dejas el bruto en CSV “porque es más simple”, el informe del lunes **escanea y factura** el texto entero. Elegir Parquet **en la carga** no es capricho: es el procedimiento.

### Misma T, otra L (sigue el Hola ETL)

El JSON del ejemplo vale para **ver** el resultado en clase. Si esos productos Mix fueran 50 GB y el destino un lago, la carga cambiaría así:

```python
# misma transformación; cambia solo la carga
df_joined.to_parquet("pdi_product_mix.parquet")
```

O, si el siguiente script del pipeline tiene que recoger el resultado **ahora**:

```python
import pyarrow.feather as feather

feather.write_feather(df_joined, "pdi_product_mix.feather")
```

O, si el destino es una cola y el esquema puede ganar un campo el mes que viene, la carga sería **Avro** (el esquema viaja con el dato; el código está en [1.7](formatos.md)).

Un job de ingesta muy habitual: llega **JSONL** (un objeto por línea) y lo **dejas en Parquet** para el análisis. No hace falta pasar por pandas:

```python
import pyarrow.parquet as pq
from pyarrow import json as pajson

tabla = pajson.read_json("empleados.json")  # un objeto JSON por línea
pq.write_table(tabla, "empleados.parquet")
```

Comprimir en la carga (Snappy, gzip, zstd) ocupa menos disco y viaja menos por la red; a cambio, **cuesta CPU**. En Big Data suele ganar el algoritmo **rápido** (Snappy, zstd), no el que más aprieta. El catálogo está en [1.7](formatos.md).

!!! tip "Tres preguntas al cerrar un procedimiento de ingesta"
    1. ¿El destino va a **escribir** muchos registros o a **leer** pocas columnas?  
    2. ¿El clúster puede **partir** ese fichero?  
    3. ¿Mañana cambia el esquema? → Avro. ¿Mañana solo suman una columna? → Parquet.

## Lotes, micro-lotes o continuo

El movimiento entre origen y destino no es siempre el mismo reloj:

| | **Por lotes** (*batch*) | **Micro-lotes** | **En continuo** (*streaming*) |
| --- | --- | --- | --- |
| Cuándo corre | Cada X horas o al llegar un fichero | Cada pocos minutos, un bloque pequeño | En cuanto el dato aparece |
| Latencia | Horas; a menudo no importa | Compromiso | Crítica (segundos o menos) |
| Dato | Un bloque que **ya está** | Varios bloques chicos | Un flujo que no para |
| Encaja | Cierre nocturno, volcado SQL → HDFS | Paneles “casi en vivo” | Logs, sensores, clics |
| Herramientas típicas | Sqoop, un job Spark, Pentaho de noche, un script Python | Spark (micro-batch) | Kafka, NiFi, Flume, Storm, Spark Structured Streaming |

La ingesta puede ser **síncrona** (esperas a que el destino confirme) o **asíncrona** (sueltas el mensaje y sigues). Las colas son el caso típico de lo segundo.

## Colas: productor, consumidor y contrapresión

Los sistemas de mensajería (Kafka, RabbitMQ, Kinesis…) **desacoplan** a quien envía de quien recibe. Los verás a fondo más adelante; aquí basta el mecanismo.

- Un **productor** deja un mensaje en una cola o en un bus.
- Un **consumidor** lo recoge. En muchas colas clásicas, al recogerlo el mensaje **desaparece**.
- Si el consumidor va lento, la cola **aguanta** el chaparrón: eso es **contrapresión** (*back pressure*). Sin cola, el origen te tumba o tiras eventos.

Kafka (y similares) es **distribuido**: el orden no siempre se respeta entre *varios* canales, hay que pensar en nodos que fallan y en crecer añadiendo máquinas. No es “una carpeta con ficheros”.

!!! tip "Para el examen"
    Si te piden “desacoplar productor y consumidor” o “que el sensor no espere al informe”, la familia es **mensajería**, no Sqoop.

## La ingesta por dentro

En la práctica extraes de donde el dato **nació** (o ya está guardado) y cargas en un destino o en una **zona temporal**.

**De dónde suele salir**

- una cola (Kafka) que a su vez ya recogió IoT o redes sociales;
- una base relacional (a menudo por un conector tipo JDBC: un “enchufe” estándar a SQL);
- un servicio web que responde JSON (REST);
- un almacén de ficheros (HDFS, S3).

**Adónde suele ir**

- otra cola;
- otra base relacional o una NoSQL;
- HDFS / S3;
- una plataforma (Snowflake, Databricks…).

En la [arquitectura por capas](arquitectura.md) la ingesta es la **primera**. El primer paso suele ser el más pesado: decenas o cientos de fuentes, velocidades distintas, formatos distintos. Hay que:

1. **Priorizar** fuentes (no todas importan el día 1).
2. **Validar** cada fichero o lote por separado.
3. **Enrutar** cada pieza a su destino.

Cuatro parámetros en los que centrar el esfuerzo (suenan a las [5 V](por-que-big-data.md), aplicados al *cómo entra*):

| Parámetro | Pregunta |
| --- | --- |
| Velocidad | ¿Continuo o a trompicones? ¿Síncrono o asíncrono? ¿Máquinas, personas, redes sociales? |
| Tamaño | ¿Cuántos GB/día? ¿Crecerá al añadir fuentes? |
| Frecuencia | ¿Lote, micro-lote o streaming? |
| Formato | ¿Tabla / Parquet, JSON, imagen, audio? |

## Qué preguntar antes de elegir el mecanismo

Usa esta lista como **guion de práctica o de examen**. No hace falta contestarlo todo; sí las que duelen en *tu* caso. Si te dan un supuesto (por ejemplo, medir reacciones en redes a un producto nuevo), elige **al menos tres preguntas de cada bloque**.

| Tema | Preguntas | Por qué importa |
| --- | --- | --- |
| Origen y formato | ¿API, IoT, SQL, fichero? ¿Interno o externo? ¿Estructurado? ¿Eventos/s o GB/h? ¿Carga histórica? ¿Fuentes nuevas? ¿Hay que **cruzar** dos sistemas para tener la foto completa? | El conector y el *join* no son el mismo |
| Cómo se acerca el dato | ¿Push, pull o poll? | Quién inicia y quién puede tumbarse |
| Latencia | ¿Lote a las 02:00 o segundos? Si llega **tarde**, ¿hasta cuándo sigue siendo válido? | Kafka no es “mejor”; es *otra* necesidad |
| Actualizaciones | ¿El origen cambia? ¿Cómo te **avisan** de una columna nueva? ¿Histórico? ¿Reutilizas o vuelves a ingerir la misma versión? ¿Pisas (`UPDATE`) o borras y insertas? | Cómo evoluciona el modelo |
| Transformaciones | ¿Durante la ingesta o después? ¿Añaden espera al origen? ¿Pierdes el original? ¿En stream hay que transformar al vuelo? | ETL frente a ELT |
| Destino | ¿Aguanta la velocidad de lectura/escritura? ¿Almacén “tonto” (S3) o con consultas (Snowflake, Databricks)? ¿Uno o varios destinos? ¿Avro o Parquet? ¿Particionar? ¿Búsquedas al azar? ¿Hive / Spark? | Ver [formatos](formatos.md) |
| Calidad y gobierno | ¿Fallos al leer? ¿Anómalos, duplicados? ¿Metadatos, linaje, evolución del esquema? | Veracidad (5 V) |
| Seguridad | ¿Enmascarar el DNI o *no ingerirlo*? ¿Quién puede ver el campo, y en qué estado? | Capa transversal |

## Familias de herramientas (para orientar)

No tienes que certificar todas. Sí saber **para qué familia** las citarías. Varias se profundizan más adelante (Sqoop, Flume, NiFi, Kafka); aquí basta el *para qué*.

**Movimiento / ingesta en el ecosistema Hadoop y cloud**

- **Sqoop** — puente **SQL ↔ HDFS/Hive/HBase**, datos estructurados, sobre todo **batch** (*pull*). El proyecto está en mantenimiento; la *idea* sigue y en cloud verás equivalentes.
- **Flume** — flujos de **logs** (semi o no estructurados) hacia HDFS/HBase (*push* / stream).
- **NiFi** — pantalla **visual**: cargas de varias fuentes (lote o stream), las pasas por un grafo de procesos y las vuelcas a otra parte.
- **Logstash** — nació para logs hacia Elasticsearch; admite muchas entradas y salidas (también AWS).
- **AWS Glue** — ETL gestionado en AWS (descubrimiento de esquemas incluido). Aparece junto a Athena o Data Pipeline.

**Mensajería** (ingesta **asíncrona**: el productor no espera al consumidor)

- **Kafka** (publicador / suscriptor), **RabbitMQ** (cola clásica), **Kinesis** (AWS), **Event Hubs** (Azure), **Pub/Sub** (Google).

**Suites ETL** (conectores, planificación por lote / evento / stream, errores, metadatos)

En el aula: **Pentaho Data Integration**. En el mercado: Talend, Informatica, Oracle Data Integrator, MuleSoft…

Transformaciones que anuncian: simples (tipos, textos), intermedias (agregar, buscar un valor en otra tabla) y complejas (un modelo, código de terceros). En este módulo nos quedamos en lo que puedes **ver** en Spoon o en el “Hola ETL” de arriba.

**Conectores “de catálogo”** (tendencia ELT)

- **Fivetran** (comercial, muchos conectores), **Airbyte** (open source y también en cloud): menos ingeniería por cada aplicación nueva.

!!! example "Tres enunciados, tres mecanismos"
    1. “Cada noche, la tabla Oracle de pedidos → HDFS.” → **Sqoop** o ETL batch (*pull*), no un bus de eventos.  
    2. “Los logs de la web deben verse en el panel en pocos segundos.” → **flujo** (Flume/Kafka + consumidor; a menudo *push*).  
    3. “Un CSV de productos y otro de fabricantes → JSON de la categoría Mix.” → **Pentaho** o el script pandas/DuckDB de esta página.

!!! success "Criterio b) en un examen"
    No basta con escribir “Kafka”. Debes decir: **origen**, **push/pull/poll**, **ritmo** (lote, micro-lote o stream), **ETL o ELT**, **destino**, **formato de la carga** (Avro, Parquet, Feather…) y **por qué** ese mecanismo y no el de al lado.

## Para practicar

No sustituye a Moodle. Sirve para comprobar que el apartado se sostiene en voz alta.

1. ¿Cuál es el **primer** paso al diseñar un pipeline de ingesta?  
2. Relación entre **pipeline** y **ETL**.  
3. ¿ETL y ELT son lo mismo? ¿Cuándo usarías cada uno? En Big Data, ¿cuál suele verse más y por qué?  
4. Repite el “Hola ETL” uniendo **productos + ventas**: CSV de una categoría, nombre del fabricante y **cantidad total vendida** de cada producto (pandas y DuckDB).  
5. Misma transformación, **tres cargas**: JSON (para verlo), Parquet (lago) y Feather (paso intermedio). Anota tamaño y di **cuándo** usarías cada una.  
6. Supuesto: lanzáis un producto y queréis medir reacciones en redes. Contesta **al menos tres preguntas de cada bloque** de la tabla de consideraciones. Incluye **en qué formato** dejarías el dato en S3 y por qué.
