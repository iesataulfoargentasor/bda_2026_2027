---
title: 1.6 Ingesta de datos
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.6. Ingesta de datos

**Ingesta** es incorporar datos de orígenes distintos (estructura, ritmo, calidad) a un almacén o a un proceso. Es el criterio **b)** del RA1: *determinar los procedimientos y mecanismos*.

Si la ingesta es frágil, el resto de la tubería (ciencia de datos, cuadro de mando) trabaja sobre arena: el modelo será brillante y la cifra, mentira. Es el **primer** paso al diseñar una arquitectura Big Data: sin origen claro y sin objetivo de negocio, no hay herramienta que salve el diseño.

![Fases de un pipeline de datos](../assets/ut1/pipeline.png)

## Empieza por el problema, no por la herramienta

Un **pipeline** (tubería de datos) es un proceso partido en fases: consume de un origen, limpia o transforma y deja el resultado en un destino. En su forma más simple: recoger, guardar, procesar y **construir algo útil**.

Se diseña **desde la pregunta de negocio hacia atrás** hasta el origen.

Ejemplo: dirección quiere “ocupaciones de hotel por comarca, cada mañana a las 8”.

1. ¿Qué tabla o gráfico necesitan ver? (destino / presentación)
2. ¿Qué hay que agregar y limpiar? (transformación)
3. ¿De qué programa de reservas, Excel o API salen las reservas? (origen)

“Montar Kafka porque está de moda” no es un procedimiento. Kafka *puede* ser el mecanismo **si** el ritmo y el desacoplo lo piden.

### Por qué no se analiza en el mismo sitio donde se crea el dato

El análisis (resúmenes, cruces, modelos) es **caro** para la máquina. Si lo haces sobre la caja o el programa de reservas, el cajero espera. Por eso se **copia** el dato a otro sitio: el sistema del día a día sigue cobrando; el de informes trabaja aparte. Eso es lo de [operar frente a analizar](procesamiento.md).

En muchas empresas el primer destino consolidado es un **data lake**; luego se curan copias hacia el warehouse que alimenta el panel. Dos saltos, dos procedimientos, no uno solo “mágico”.

### Pipeline no es lo mismo que ETL

Se usan como sinónimos y **no lo son**.

- Un **pipeline** es *cualquier* movimiento o procesamiento de datos entre sistemas (incluida una cola, un filtro ligero, un lote nocturno).
- Un **ETL** es un **caso particular**: extraer, transformar y cargar. Toda ETL es un pipeline; no todo pipeline es una ETL.

### Data wrangling (el dato “en disputa”)

Conforme el dato avanza por la tubería, casi siempre hay que **limpiarlo**: otra fuente usa `M`/`F` en vez de `1`/`2`, hay huecos, hay duplicados, un campo llega como texto `"10"`. Ese trabajo de pasar del crudo al dato que ya se puede usar se llama **data wrangling** (manipulación o “disputa” de datos). No es un producto: es el oficio de dejar el dato **listo**.

### El pipeline es iterativo

Negocio lanza una hipótesis (“¿cancelan más los que reservan el viernes?”). Miras lo que hay. Si falta un campo, **vuelves a ingerir** (otra fuente o el mismo origen con más columnas), lo integras con lo anterior y analizas otra vez. Si el número no convence, se itera. La ingesta no es un acto único el día 1.

## Extraer, transformar y cargar: el orden cambia el oficio

Tres verbos, siempre los mismos:

1. **Extraer:** leer el origen (una tabla, un CSV, una API).
2. **Transformar:** limpiar, unir, recodificar, agregar.
3. **Cargar:** escribir el resultado en el destino.

Las siglas inglesas **ETL** y **ELT** solo cambian **cuándo** haces el paso 2.

![Esquema ETL](../assets/ut1/etl.png)

| | **ETL** | **ELT** |
| --- | --- | --- |
| Orden | Extraer → **transformar** → cargar | Extraer → **cargar** → transformar |
| Dónde se transforma | Motor intermedio (Pentaho, Talend…) | En el destino (SQL del warehouse, Spark sobre el lago) |
| Cuándo brilla | El destino es rígido y no debe tragar basura | Destinos elásticos y **varios** consumidores del mismo bruto |
| Tiempo hasta “ver el crudo” | Más tarde (esperas a la T) | Antes (el bruto ya está) |
| Quién “duele” si cambia la pregunta | Hay que retocar el flujo de T **antes** de recargar | A menudo basta una consulta nueva sobre lo ya cargado |
| Oficio | Más trabajo del ingeniero de datos *antes* | El analista o científico puede transformar con SQL o Python |

Unificar orígenes distintos **gasta** una parte enorme del proyecto. No es “un script de una tarde” cuando hay veinte fuentes y diez años de histórico.

El mercado ha girado hacia **ELT** en cloud (el almacén es potente y barato de escalar; el lago se llena antes). **ETL sigue** cuando el destino no puede tragarse basura, no hay motor detrás o trabajas en aula con [Pentaho](pentaho.md): PDI se enseña como **ETL visual**.

Una herramienta de este módulo debe ser:

- **flexible** (CSV, JSON, Parquet, SQL, Excel, una petición HTTP…),
- **escalable y tolerante a fallos** (si cae a la mitad, no dejes el destino a medias sin saberlo),
- **conectada** a muchos orígenes (fichero, BD, cola, API).

Además conviene que deje **rastro** (qué se ejecutó, qué falló) y que puedas **planificarla**: cada noche, al llegar un fichero, o en continuo.

### Extracción

Recopila los datos del sistema original y los lleva a un sitio de trabajo (a menudo un almacén de informes o una zona temporal). Las fuentes van de un CSV a una base relacional, pasando por un mensaje de red social o un sensor.

Dos exigencias, en castellano:

1. **Rápida y ligera.** Que el origen casi no se entere.
2. **Que no tumbe el origen.** No se puede poner en riesgo la caja ni **cambiar** sus datos. Si colapsa el programa de reservas, la empresa pierde dinero *operando*, no “analizando”.

Por eso no vuelcas **toda** la caja en hora punta si puedes leer solo lo nuevo, una ventana de tiempo o una API con cuota. La primera carga histórica es un procedimiento **distinto** del día a día.

En la extracción también **miras** si el dato es el que esperabas (columnas, tipos, que no venga vacío). Si no, se **rechaza** o se aparta: no lo cuelas “para que el job acabe”.

Al salir de esta fase, el dato ya está en un formato con el que se puede empezar a transformar.

### Transformación

Cambios para que el dato tenga el **formato y el contenido** que el destino espera. Ejemplos de aula:

- Cambiar la codificación (tildes que se rompen).
- Quitar duplicados.
- Cruzar dos fuentes (reservas + pagos) para obtener una tercera.
- Agregar (ventas por día, no cada ticket).
- Quedarte solo con parte de las columnas.
- Fabricar un código o un identificador estable.
- Ordenar mejor la información.
- Calcular un indicador que el informe ya pide (ocupación %, ticket medio).

Debe **mejorar** calidad, integrar y quitar ambigüedad. **No** debe inventar hechos, duplicar a ciegas, borrar lo relevante ni ser impredecible.

En streaming cada milisegundo de T cuenta: a veces dejas la transformación pesada para un lote posterior.

### Carga

Escribe en el destino y **se adapta a él**. Minimiza el tiempo que el destino está “ocupado” escribiendo.

Cada sistema tiene su forma cómoda de recibir datos:

- instrucciones SQL o carga masiva (*bulk*) — PostgreSQL, SQL Server, Redshift…;
- ficheros que el destino lee de una carpeta;
- cargadores propios — HDFS, S3.

Ahí importan los **índices** (el “índice del libro”: si lo reconstruyes **en cada fila**, la carga masiva se muere), partir el destino en trozos y confirmar por **bloques**, no fila a fila. Funciona en 100 filas de práctica y revienta en 10 millones.

## Lotes o continuo (batch frente a streaming)

El movimiento entre origen y destino no es siempre el mismo reloj:

| | **Por lotes** (*batch*) | **En continuo** (*streaming*) |
| --- | --- | --- |
| Cuándo corre | Cada X horas o al llegar un fichero | En cuanto el dato aparece |
| Latencia | Minutos u horas; a menudo no importa | Crítica (segundos o menos) |
| Dato | Un bloque que **ya está** (estático en ese instante) | Un flujo que no para |
| Encaja | Cierre nocturno, volcado SQL → HDFS | Logs, sensores, clics |
| Herramientas típicas | Sqoop, un job Spark, Pentaho de noche | Kafka, NiFi, Flume, Spark Structured Streaming |

Un pipeline sencillo a veces solo filtra o enriquece un poco y escribe en una cola. Otro pipeline, más tarde, hace los cruces y los resúmenes para el informe. No tienes que meter **toda** la lógica en el primer salto.

## La ingesta por dentro

En la práctica extraes de donde el dato **nació** (o ya está guardado) y cargas en un destino o en una **zona temporal**. Orígenes y destinos que vas a citar:

**De dónde suele salir**

- una cola (Kafka) que a su vez ya recogió IoT o redes sociales;
- una base relacional (a menudo por un conector tipo JDBC: un “enchufe” estándar a SQL);
- un servicio web que responde JSON;
- un almacén de ficheros (HDFS, S3).

**Adónde suele ir**

- otra cola;
- otra base relacional o una NoSQL;
- HDFS / S3;
- una plataforma (Snowflake, Databricks…).

En la [arquitectura por capas](arquitectura.md) la ingesta es la **primera**. El primer paso suele ser el más pesado: cientos o miles de fuentes, velocidades distintas, formatos distintos. Hay que:

1. **Priorizar** fuentes (no todas importan el día 1).
2. **Validar** cada fichero o lote por separado.
3. **Enrutar** cada pieza a su destino.

Cuatro parámetros en los que centrar el esfuerzo (suenan a las [5 V](por-que-big-data.md), aplicados al *cómo entra*):

| Parámetro | Pregunta |
| --- | --- |
| Velocidad | ¿El flujo es continuo o a trompicones? ¿Máquinas, personas, redes sociales? |
| Tamaño | ¿Cuántos GB/día? ¿Crecerá al añadir fuentes? |
| Frecuencia | ¿Lote o streaming? |
| Formato | ¿Tabla, JSON, imagen, audio? |

## Qué preguntar antes de elegir el mecanismo

Usa esta lista como **guion de práctica o de examen**. No hace falta contestarlo todo; sí las que duelen en *tu* caso.

| Tema | Preguntas | Por qué importa |
| --- | --- | --- |
| Origen y formato | ¿API, IoT, SQL, fichero? ¿Interno o externo? ¿Estructurado? ¿Entrarán fuentes nuevas? | El conector no es el mismo |
| Volumen y ritmo | ¿Eventos/s, GB/h? ¿Hay carga inicial histórica? | Batch frente a stream; dimensionar |
| Latencia | ¿Vale un lote a las 02:00 o tiene que verse en segundos? | Kafka no es “mejor”; es *otra* necesidad |
| Actualizaciones | ¿El origen cambia? ¿Guardamos histórico? ¿Pisamos el dato o añadimos una versión? | Cómo evoluciona el modelo |
| Transformaciones | ¿Hacen falta *durante* la ingesta? ¿Añaden espera? ¿Perdemos el original? | ETL frente a ELT |
| Destinos | ¿Uno o varios (S3 y Mongo)? ¿Filas (Avro) o columnas (Parquet)? ¿Cómo se consultará? | Ver [formatos](formatos.md) |
| Calidad | ¿Duplicados, nulos, relojes desfasados? ¿Linaje? | Veracidad (5 V) |
| Seguridad | ¿Hay que enmascarar el DNI o *no ingerirlo*? ¿Quién puede ver el campo, y en qué estado? | Capa transversal |

## Familias de herramientas (para orientar)

No tienes que certificar todas. Sí saber **para qué familia** las citarías.

**Movimiento / ingesta en el ecosistema Hadoop y cloud**

- **Sqoop** — puente **SQL ↔ HDFS/Hive/HBase**, datos estructurados, sobre todo **batch**. El proyecto está en mantenimiento; la *idea* (volcado masivo JDBC ↔ Hadoop) sigue y en cloud verás equivalentes.
- **Flume** — flujos de **logs** (semi o no estructurados) hacia HDFS/HBase.
- **NiFi** — pantalla **visual**: cargas de varias fuentes (lote o stream), las pasas por un grafo de procesos y las vuelcas a otra parte.
- **Logstash** — nació para logs hacia Elasticsearch; admite muchas entradas y salidas (también AWS).
- **AWS Glue** — ETL gestionado en AWS (descubrimiento de esquemas incluido). Aparece junto a Athena o Data Pipeline.

**Mensajería** (el productor no espera al consumidor)

- **Kafka**, **RabbitMQ**, **Kinesis** (AWS), **Event Hubs** (Azure), **Pub/Sub** (Google).  
  Analogía: un tablón donde unos *publican* y otros *se suscriben*. Si el consumidor se cae, el mensaje **puede** seguir ahí (según la herramienta y la retención).

**Suites ETL de “toda la vida”** (conectores, planificación, errores, metadatos)

En el aula usamos **Pentaho Data Integration**. En el mercado verás también Talend, Informatica, Oracle Data Integrator, MuleSoft… El detalle de PDI está en [1.8](pentaho.md).

Las transformaciones que anuncian esas suites van de lo simple (tipos, textos, cuentas) a cruces y búsquedas en otra tabla, y a veces a código o un modelo. En este módulo nos quedamos en lo que puedes **ver** en Spoon.

**Conectores “de catálogo”**

- Fivetran (comercial), **Airbyte** (también open source): menos ingeniería por cada aplicación nueva; más suscripción u operación del servicio.

!!! example "Tres enunciados, tres mecanismos"
    1. “Cada noche, la tabla Oracle de pedidos → HDFS.” → **Sqoop** (o un ETL batch), no un bus de eventos.  
    2. “Los logs de la web deben verse en el panel en pocos segundos.” → **flujo** (Flume/Kafka + consumidor).  
    3. “Un CSV de Airbnb que limpiamos en clase y sacamos a JSON.” → **Pentaho** (ETL visual).

!!! success "Criterio b) en un examen"
    No basta con escribir “Kafka”. Debes decir: **origen**, **ritmo**, **batch o stream**, **ETL o ELT**, **destino** y **por qué** ese mecanismo y no el de al lado.
