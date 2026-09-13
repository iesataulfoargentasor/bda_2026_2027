---
title: 1.6 Ingesta de datos
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.6. Ingesta de datos

**Ingesta** es incorporar datos de orígenes distintos (estructura, ritmo, calidad) a un almacén o a un proceso. Es el criterio **b)** del RA1: *determinar procedimientos y mecanismos*.

Si la ingesta es frágil, el resto del pipeline (ciencia de datos, cuadro de mando) trabaja sobre arena.

![Fases de un pipeline de datos](../assets/ut1/pipeline.png)

## Empieza por el problema, no por la herramienta

Un **pipeline** consume de un origen, limpia/transforma y deja el dato en un destino. Se diseña **desde la pregunta de negocio hacia atrás** hasta el origen. “Montar Kafka porque está de moda” no es un procedimiento.

En muchas empresas el destino de la primera consolidación es un **data lake**; luego se curan copias hacia el warehouse.

## ETL y ELT

![Esquema ETL](../assets/ut1/etl.png)

| | **ETL** | **ELT** |
| --- | --- | --- |
| Orden | Extraer → **transformar** → cargar | Extraer → **cargar** → transformar |
| Dónde se transforma | Motor intermedio (Pentaho, Talend…) | En el destino (SQL en el warehouse, Spark sobre el lago) |
| Cuándo brilla | Destino rígido, hay que limpiar *antes* | Destinos elásticos (lago, cloud) y varios consumidores |
| Tiempo hasta “ver el bruto” | Más tarde (espera a la T) | Antes (el bruto ya está) |

El mercado ha girado hacia **ELT** en cloud, pero **ETL sigue** cuando el destino no puede tragarse basura o no tienes motor potente detrás. Pentaho Data Integration implementa sobre todo el estilo **ETL visual**.

Una herramienta ETL/ELT de este módulo debe ser **flexible** (CSV, JSON, Parquet…), **escalable y tolerante a fallos**, y **conectada** a muchos orígenes.

### Las tres fases (aunque el orden cambie)

**Extracción.** Leer el origen sin tumbarlo: incrementales, ventanas, APIs con cuota, CDC si hay que capturar cambios.

**Transformación.** Tipos, recodificar, unir, agregar, reglas de calidad. En streaming, cada milisegundo de T cuenta.

**Carga.** Escribir en el destino con el método que ese sistema lleva bien:

- SQL / *bulk* (PostgreSQL, SQL Server, Redshift…).
- Ficheros que el destino ingiere.
- Cargadores de HDFS o S3.

Ahí importan índices, **particionado**, tamaño de transacción y `COMMIT`. Una carga que reconstruye todos los índices en cada fila es un procedimiento mal determinado.

## Qué preguntar antes de elegir el mecanismo

| Tema | Preguntas |
| --- | --- |
| Origen y formato | ¿API, IoT, SQL, fichero? ¿Interno o externo? ¿Estructurado? |
| Volumen y ritmo | ¿Eventos/s, GB/h? ¿Carga inicial histórica? |
| Latencia | ¿Vale un lote nocturno o tiene que verse en segundos? |
| Actualizaciones | ¿Cambian columnas? ¿Hace falta histórico de cambios? |
| Destinos | ¿Uno o varios? ¿Filas (Avro) o columnas (Parquet)? |
| Calidad | ¿Duplicados, nulos, relojes? ¿Metadatos y linaje? |
| Seguridad | ¿Hay que enmascarar? ¿Quién no puede ver el campo? |

## Familias de herramientas (para orientar, no para certificar todas)

**Ingesta / movimiento**

- **Sqoop** — SQL ↔ HDFS/Hive/HBase (estructurado, sobre todo batch). Proyecto en modo mantenimiento: la idea (bulk JDBC ↔ Hadoop) sigue; en cloud verás equivalentes.
- **Flume** — flujos (logs) hacia HDFS/HBase.
- **NiFi** — pipelines visuales, batch y streaming.
- **Logstash** / **OpenSearch** — logs y eventos.
- **AWS Glue** — ETL gestionado en AWS.

**Mensajería (desacopla productor y consumidor)**

- **Kafka**, **RabbitMQ**, **Kinesis**, **Event Hubs**, **Pub/Sub**.

**Conectores “de catálogo”**

- Fivetran (comercial), **Airbyte** (también open source): menos ingeniería por fuente, más suscripción o operación del servicio.

**ETL de aula en este módulo:** **Pentaho Data Integration**, Talend, Informatica, etc. En [1.8](pentaho.md) se concreta PDI.

!!! success "Criterio b) en un examen o práctica"
    No basta con nombrar Kafka. Debes decir: origen, ritmo, batch o stream, ETL o ELT, destino y **por qué** ese mecanismo y no otro.
