---
title: 1.6 Ingesta de datos
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.6. Ingesta de datos

**Ingesta** es incorporar datos de orígenes distintos (estructura, ritmo, calidad) a un almacén o a un proceso. Es el criterio **b)** del RA1: *determinar los procedimientos y mecanismos*.

Si la ingesta es frágil, el resto del pipeline (ciencia de datos, cuadro de mando) trabaja sobre arena: el modelo será brillante y la cifra, mentira.

![Fases de un pipeline de datos](../assets/ut1/pipeline.png)

## Empieza por el problema, no por la herramienta

Un **pipeline** (tubería de datos) consume de un origen, limpia o transforma y deja el resultado en un destino. Se diseña **desde la pregunta de negocio hacia atrás** hasta el origen.

Ejemplo: dirección quiere “ocupaciones de hotel por comarca, cada mañana a las 8”.

1. ¿Qué tabla o gráfico necesitan ver? (destino / presentación)
2. ¿Qué hay que agregar y limpiar? (transformación)
3. ¿De qué PMS, Excel o API salen las reservas? (origen)

“Montar Kafka porque está de moda” no es un procedimiento. Kafka *puede* ser el mecanismo **si** el ritmo y el desacoplo lo piden.

En muchas empresas el primer destino consolidado es un **data lake**; luego se curan copias hacia el warehouse que alimenta el panel. Dos saltos, dos procedimientos, no uno solo “mágico”.

## ETL y ELT: el orden cambia el oficio

![Esquema ETL](../assets/ut1/etl.png)

Las tres letras son las mismas; **cambia el orden** de la T y la L.

| | **ETL** | **ELT** |
| --- | --- | --- |
| Orden | Extraer → **transformar** → cargar | Extraer → **cargar** → transformar |
| Dónde se transforma | Motor intermedio (Pentaho, Talend…) | En el destino (SQL del warehouse, Spark sobre el lago) |
| Cuándo brilla | El destino es rígido y no debe tragar basura | Destinos elásticos y **varios** consumidores del mismo bruto |
| Tiempo hasta “ver el crudo” | Más tarde (esperas a la T) | Antes (el bruto ya está) |
| Quién “duele” si cambia la pregunta | Hay que retocar el flujo de T **antes** de recargar | A menudo basta una consulta nueva sobre lo ya cargado |

El mercado ha girado hacia **ELT** en cloud (el almacén es potente y barato de escalar). **ETL sigue** cuando el destino no puede tragarse basura, no hay motor detrás o trabajas en aula con [Pentaho](pentaho.md): PDI se enseña como **ETL visual**.

Una herramienta de este módulo debe ser:

- **flexible** (CSV, JSON, Parquet, SQL…),
- **escalable y tolerante a fallos** (si cae a la mitad, no dejes el destino a medias sin saberlo),
- **conectada** a muchos orígenes (HTTP, fichero, BD, cola).

### Las tres fases (aunque el orden cambie)

**Extracción.** Leer el origen **sin tumbarlo**. No haces un `SELECT *` a la caja en hora punta si puedes leer incrementales (solo lo nuevo), ventanas de tiempo, APIs con cuota o CDC (capturar cambios). La primera carga histórica es un procedimiento **distinto** del día a día.

**Transformación.** Tipos (`"10"` no es 10), recodificar (`M`/`F` frente a `1`/`2`), unir, agregar, reglas de calidad (nulos, duplicados). En streaming cada milisegundo de T cuenta: a veces dejas la T pesada para un lote posterior.

**Carga.** Escribir en el destino con el método que **ese** sistema lleva bien:

- SQL o *bulk* (PostgreSQL, SQL Server, Redshift…),
- ficheros que el destino ingiere,
- cargadores de HDFS o S3.

Ahí importan los **índices** (¿los desactivas durante la carga masiva?), el **particionado**, el tamaño de transacción y el `COMMIT`. Una carga que reconstruye todos los índices **en cada fila** es un procedimiento mal determinado: funciona en 100 filas de práctica y muere en 10 millones.

## Qué preguntar antes de elegir el mecanismo

Usa esta lista como **guion de práctica o de examen**. No hace falta contestarlo todo; sí las que duelen en *tu* caso.

| Tema | Preguntas | Por qué importa |
| --- | --- | --- |
| Origen y formato | ¿API, IoT, SQL, fichero? ¿Interno o externo? ¿Estructurado? | El conector no es el mismo |
| Volumen y ritmo | ¿Eventos/s, GB/h? ¿Hay carga inicial histórica? | Batch frente a stream; dimensionar |
| Latencia | ¿Vale un lote a las 02:00 o tiene que verse en segundos? | Kafka no es “mejor”; es *otra* necesidad |
| Actualizaciones | ¿Cambian columnas? ¿Hace falta histórico de cambios? | Evolución de esquema; SCD |
| Destinos | ¿Uno o varios? ¿Filas (Avro) o columnas (Parquet)? | Ver [formatos](formatos.md) |
| Calidad | ¿Duplicados, nulos, relojes desfasados? ¿Linaje? | Veracidad (5 V) |
| Seguridad | ¿Hay que enmascarar el DNI? ¿Quién no puede ver el campo? | Capa transversal |

## Familias de herramientas (para orientar)

No tienes que certificar todas. Sí saber **para qué familia** las citarías.

**Movimiento / ingesta**

- **Sqoop** — puente **SQL ↔ HDFS/Hive/HBase**, datos estructurados, sobre todo **batch**. El proyecto está en mantenimiento; la *idea* (volcado masivo JDBC ↔ Hadoop) sigue y en cloud verás equivalentes.
- **Flume** — flujos de **logs** hacia HDFS/HBase.
- **NiFi** — pipelines **visuales**, batch y streaming (grafos de procesadores).
- **Logstash** / ecosistema **OpenSearch** — logs y eventos.
- **AWS Glue** — ETL gestionado en AWS (descubrimiento de esquemas incluido).

**Mensajería** (el productor no espera al consumidor)

- **Kafka**, **RabbitMQ**, **Kinesis**, **Event Hubs**, **Pub/Sub**.  
  Analogía: un tablón donde unos *publican* y otros *se suscriben*. Si el consumidor se cae, el mensaje **puede** seguir ahí (según la herramienta y la retención).

**Conectores “de catálogo”**

- Fivetran (comercial), **Airbyte** (también open source): menos ingeniería por cada SaaS nuevo; más suscripción u operación del servicio.

**ETL de aula en este módulo:** **Pentaho Data Integration**, y en el mercado Talend, Informatica, etc. El detalle de PDI está en [1.8](pentaho.md).

!!! example "Tres enunciados, tres mecanismos"
    1. “Cada noche, la tabla Oracle de pedidos → HDFS.” → **Sqoop** (o un ETL batch), no un bus de eventos.  
    2. “Los logs de la web deben verse en el panel en pocos segundos.” → **flujo** (Flume/Kafka + consumidor).  
    3. “Un CSV de Airbnb que limpiamos en clase y sacamos a JSON.” → **Pentaho** (ETL visual).

!!! success "Criterio b) en un examen"
    No basta con escribir “Kafka”. Debes decir: **origen**, **ritmo**, **batch o stream**, **ETL o ELT**, **destino** y **por qué** ese mecanismo y no el de al lado.
