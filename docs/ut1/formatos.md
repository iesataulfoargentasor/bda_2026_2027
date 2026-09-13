---
title: 1.7 Formatos de datos
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.7. Formatos de datos

El criterio **c)** pide **elegir el formato adecuado para el almacenamiento**. El mismo dataset en CSV o en Parquet cambia:

- el tiempo de la consulta,
- el **coste** en cloud (a menudo pagas por lo *escaneado*),
- si Spark o Hadoop pueden **partir** el fichero entre nodos.

No es “cuál es más moderno”. Es “qué operación voy a hacer mil veces”.

## Qué se le pide a un formato (para entender los binarios)

Un formato “bueno” en Big Data suele cumplir:

- **Independiente del lenguaje.** Lo escribe Java y lo lee Python.
- **Expresivo.** Anidados, nulos, tipos (un entero no es un texto `"10"`).
- **Eficiente.** Pocos bytes y poca CPU al leer.
- **Evolucionable.** Añadir un campo sin reescribir el histórico entero.
- **Partible** (*splittable*) y **comprimible.** Si el fichero es un bloque único que no se puede cortar, **un** nodo lo lee entero y el clúster no sirve.

“Partible” es la propiedad que más se olvida: un JSON con un array de 10 millones de objetos entre `[` y `]` **no** se trocea bien. Diez millones de **líneas** JSONL, sí.

## Texto frente a binario

| | Texto (CSV, JSON, XML) | Binario (Avro, Parquet, ORC) |
| --- | --- | --- |
| Abrirlo con el Bloc de notas | Sí | No (hace falta herramienta o librería) |
| Tamaño | Mayor | Menor, sobre todo con compresión |
| Esquema | Implícito o a medias | Suele viajar **con** el fichero |
| Uso típico | Intercambio, APIs, que un humano lo mire | Lago y analítica a escala |

**CSV.** Universal y simple. No tipa bien (`01` ¿texto o número?), se rompe con comas y saltos dentro de un campo, y para sumar *una* columna sueles leer **todas**. Perfecto para entregar un extracto a un compañero; flojo como almacén del lago.

**JSON.** Expresivo (objetos anidados). Un documento único enorme es mala idea en el clúster. **JSON Lines (JSONL)** — **un objeto por línea** — encaja en lotes:

```json
{"nombre": "Carlos", "altura": 180, "edad": 44}
{"nombre": "Juan", "altura": 175, "edad": null}
```

`null` es JSON. `None` es **Python**. Si mezclas los dos, el parser revienta y parece un error de Big Data cuando es un error de sintaxis.

**XML.** Sigue en administraciones y facturas. Más verboso que JSON; las mismas precauciones de tamaño y de “¿se puede partir?”.

## Filas frente a columnas

![Filas frente a columnas](../assets/ut1/filas-columnas.png)

Imagina una tabla `Nombre | Altura | Edad` con un millón de personas.

**Por filas** (CSV, JSON, Avro): guardas `Ana, 170, 30` juntos. Leer *a Ana entera* es barato. Sumar *solo* las edades obliga a saltar por nombre y altura una y otra vez.

**Por columnas** (Parquet, ORC): un sitio (o un grupo de páginas) tiene las alturas, otro las edades. Sumar edades lee **una** columna. Reconstruir a Ana obliga a cruzar trozos. Actualizar *una* fila es caro: hay que descomprimir, tocar y volver a comprimir.

| Orientado a **filas** | Orientado a **columnas** |
| --- | --- |
| Cada registro junto | Cada columna junta |
| Escribir / leer **filas enteras** es barato | Leer **tres columnas de un millón** es barato |
| Compresión peor (tipos mezclados en la misma racha) | Mejor compresión (valores del mismo tipo seguidos) |
| Actualizar una fila, más natural | Actualizar una fila: operación pesada |

Las bases **OLTP** (caja, reserva) guardan en **filas**. La analítica masiva (OLAP, data lake) prefiere **columnar**.

Un orden de magnitud que verás citado: 1 TB en CSV puede quedar en torno a **130 GB** en Parquet. En Athena, BigQuery y similares **pagas por dato escaneado**. Si el informe usa 3 columnas de 80, el columnar no es estética: es la factura.

!!! example "Agregar"
    Agregar es resumir: sumas, medias, recuentos. “Ventas de Alemania” no necesita el nombre de cada cliente. Columnar + filtrar particiones = menos bytes leídos.

## Avro, Parquet y ORC

Tres binarios que debes **saber elegir**, no dibujar de memoria.

![Cabecera y bloques Avro](../assets/ut1/avro.png)

**Avro** — orientado a **filas**, esquema (a menudo en JSON) **dentro** del fichero.

- Escribir muchos registros seguidos y **cambiar el esquema** (añadir un campo opcional) es su fuerte.
- Muy usado en **Kafka** y en la capa de ingesta: el mensaje lleva cómo interpretarlo.
- Con Snappy o GZIP ocupa bastante menos que el texto.

**Parquet** — **columnar**, admite estructuras **anidadas**.

- El default cultural de **Spark** y de muchos lakes.
- Ideal si casi siempre haces `SELECT col1, col2` sobre ficheros gordos.

![ORC: stripes e índices](../assets/ut1/orc.png)

**ORC** — **columnar**, nacido en **Hive**.

- *Stripes* e índices pensados para SQL sobre Hadoop.
- Muy buena compresión en tablas Hive. Si el equipo “es Spark”, verás más Parquet; no es que ORC sea peor, es el **ecosistema**.

![Comparativa de propiedades](../assets/ut1/formatos-comparativa.png)

## Cómo decidir (criterio c)

| Situación | Formato razonable | Por qué |
| --- | --- | --- |
| Intercambio con un humano o una API | JSON / CSV | Se lee y se depura |
| Bus (Kafka), esquema que cambia, escritura continua | **Avro** | Filas + esquema + evolución |
| Lago + Spark + “solo estas columnas” | **Parquet** | Menos escaneo |
| Tablas Hive muy grandes, lecturas tipo SQL | **ORC** (o Parquet si ese es el estándar del equipo) | Encaje con Hive |
| Transacción fila a fila (TPV) | Ni Parquet ni ORC como almacén OLTP | Actualizar una fila es caro |

Orden de tamaño del temario original (mismo recorte de ventas; tus cifras cambiarán):

`CSV ~10 MiB → Avro ~7 → Avro+GZIP ~2 → Parquet ~2 → Parquet+GZIP ~1,6`

Lo que importa no es memorizar 1,6: es que **el orden de magnitud** cae al pasar a binario columnar comprimido.

!!! tip "Serializar y deserializar"
    Serializar = objetos en memoria → bytes en disco o en la red.  
    Deserializar = lo contrario.  
    Cada conversión cuesta CPU y puede **perder tipos**. Elige un formato en la frontera (API → Avro, lago → Parquet) y no conviertas en cada capa “porque sí”.
