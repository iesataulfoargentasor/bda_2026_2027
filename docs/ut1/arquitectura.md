---
title: 1.5 Arquitectura y ecosistema
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.5. Arquitectura por capas y paisaje de herramientas

Un sistema Big Data no es “un programa que lo hace todo”. Se parte en **capas** que se hablan entre sí. Así caracterizas el diseño (criterio **a)**) y sabes **dónde** encajan ingesta, formato, Pentaho y el cuadro de mando.

## Las capas (flujo del dato)

1. **Ingesta** — Entras a las fuentes que *ya existen* (BD, API, IoT, ficheros) con el protocolo de cada una.
2. **Colección / integración** — Unificas formatos y semántica: un mismo “cliente” no se llama distinto en cada origen.
3. **Almacenamiento** — Lago, warehouse, HDFS, objeto en cloud… distribuido si el volumen lo pide.
4. **Procesamiento** — Infraestructura batch, streaming o híbrida. *No* extrae valor ella sola: deja el dato listo.
5. **Consulta y analítica** — SQL, notebooks, modelos. Aquí sale conocimiento.
6. **Visualización** — Informes y cuadros de mando para el cliente final (**criterio e)**).
7. **Seguridad** (transversal) — Quién lee, cifrado, copias, amenazas internas y externas.
8. **Monitorización** (transversal) — ¿El job acabó? ¿El dato está fresco? Auditoría y gobierno.

Si omites 7 y 8, el prototipo de clase funciona y el de producción no.

## El paisaje (*Big Data landscape*)

No memorices logotipos. Sitúa **la capa**:

| Capa | Ejemplos que verás en el ciclo |
| --- | --- |
| Ingesta / mensajería | Sqoop, Flume, NiFi, Kafka, Kinesis |
| Almacén | HDFS, S3, warehouses cloud, MongoDB, HBase |
| Proceso | MapReduce, Spark, Hive, Pig |
| Orquestación | Oozie, Airflow, jobs de Pentaho (Kitchen) |
| Visualización | Power BI, Tableau, informes Pentaho |

**Hadoop** fue la plataforma pionera de **lotes** sobre HDFS. **Spark** cubre lotes y streaming en memoria y convive con ese ecosistema. Pentaho (siguiente apartado) se usa en este módulo para **ETL visual** y para **mostrar** el resultado sin exigir que el alumnado programe el motor.

Busca “big data landscape” y verás mapas distintos: cambian las marcas, **no** las capas.

## Big Data y cloud

El BOE cita expresamente cloud. Un bucket S3 o un Glue no cambian el razonamiento: sigues decidiendo Vs, CAP/SCV, ETL o ELT y el formato. Cambia quién opera los discos y cómo pagas (a menudo **por dato escaneado**: por eso Parquet importa).

!!! success "Al terminar 1.5"
    Debes poder dibujar, para un caso (p. ej. lecturas de contadores o reservas turísticas), las ocho capas y **una** herramienta por capa, justificando la de almacenamiento.
