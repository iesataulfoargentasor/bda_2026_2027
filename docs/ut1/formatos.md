---
title: 1.7 Formatos de datos
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.7. Formatos de datos

El criterio **c)** pide **elegir el formato adecuado para almacenar**. El mismo dataset en CSV o en Parquet cambia el tiempo de consulta, el coste en cloud y si Spark puede **partir** el fichero entre nodos.

## Qué se le pide a un formato

- Independiente del lenguaje.
- Expresivo (anidados, nulos, tipos).
- Eficiente (CPU y bytes).
- Evolucionable (añadir un campo sin reescribir el mundo).
- **Partible** (*splittable*) y comprimible: si no se puede trocear, el clúster no paraleliza bien.

## Texto frente a binario

| | Texto (CSV, JSON, XML) | Binario (Avro, Parquet, ORC) |
| --- | --- | --- |
| Leer con un editor | Sí | No (hace falta herramienta) |
| Tamaño | Mayor | Menor (sobre todo con compresión) |
| Esquema | Implícito o a medias | Suele ir **con** el fichero |
| Uso típico | Intercambio, APIs, carga humana | Lago y analítica a escala |

**CSV** es simple y universal; no tipa bien, se rompe con comas y saltos de línea, y para agregar una columna sueles leer **todo**.

**JSON** es expresivo. Un documento único con un array enorme **no** se parte bien. **JSON Lines (JSONL)** — un objeto por línea — sí encaja en lotes:

```json
{"nombre": "Carlos", "altura": 180, "edad": 44}
{"nombre": "Juan", "altura": 175, "edad": null}
```

(`null` es JSON; `None` es Python: no lo mezcles.)

## Filas frente a columnas

![Filas frente a columnas](../assets/ut1/filas-columnas.png)

| Orientado a **filas** | Orientado a **columnas** |
| --- | --- |
| Cada registro junto (CSV, JSON, Avro) | Cada columna junta (Parquet, ORC) |
| Escribir y leer **filas enteras** es barato | Leer **tres columnas de un millón** es barato |
| Compresión peor (tipos mezclados) | Mejor compresión (valores del mismo tipo) |
| Actualizar una fila, más natural | Actualizar una fila: descomprimir / reescribir (caro) |

Las bases **OLTP** guardan en filas. La analítica masiva (OLAP, data lake) prefiere **columnar**. Un artículo habitual: 1 TB en CSV puede quedar en ~130 GB en Parquet; en Athena/BigQuery **pagas por dato escaneado**, no por dato almacenado.

## Avro, Parquet y ORC

![Cabecera y bloques Avro](../assets/ut1/avro.png)

**Avro** (filas, esquema en JSON dentro del fichero):

- Escrituras y **evolución de esquema** (añadir/quitar campos).
- Muy usado en **Kafka** y en la capa de ingesta.
- Compacto; con Snappy o GZIP aún más.

**Parquet** (columnar, anidado):

- Lecturas analíticas, Spark, muchos lakes.
- Ideal si consultas **un subconjunto** de columnas o estructuras anidadas.

![ORC: stripes e índices](../assets/ut1/orc.png)

**ORC** (columnar, nacido en **Hive**):

- Índices y *stripes* pensados para el ecosistema Hive.
- Excelente compresión en tablas Hive; en Spark el default cultural es Parquet.

![Comparativa de propiedades](../assets/ut1/formatos-comparativa.png)

## Cómo decidir (criterio c)

| Situación | Formato razonable |
| --- | --- |
| Intercambio con un humano o una API | JSON / CSV |
| Bus (Kafka), esquema que cambia, escritura continua | **Avro** |
| Lago + Spark + “solo estas columnas” | **Parquet** |
| Tablas Hive muy grandes, lecturas tipo SQL | **ORC** (o Parquet si el estándar del equipo es ese) |
| Transacción fila a fila | Ni Parquet ni ORC como almacén OLTP |

Orden de tamaño que verás en prácticas (mismo recorte de ventas, cifras del temario original): CSV ~10 MiB → Avro ~7 → Avro+GZIP ~2 → Parquet ~2 → Parquet+GZIP ~1,6. Las cifras cambian con el dataset; el **orden de magnitud** no.

!!! tip "Serializar y deserializar"
    Pasar de objetos en memoria a bytes (y al revés) es el trabajo diario del pipeline. Elige un formato y **no** conviertas en cada capa “porque sí”: cada conversión cuesta CPU y puede perder tipos.
