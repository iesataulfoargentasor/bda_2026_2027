---
title: 1.7 Formatos de datos
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.7. Formatos de datos

El criterio **c)** es este: **en qué forma dejas el dato** para que el siguiente paso no se ahogue. No es una moda. Es una decisión de diseño, igual que elegir lago o warehouse.

## Un caso para no perderse

Un grupo hotelero de Cantabria guarda cada reserva con doce campos (canal, régimen, comentarios, DNI cifrado…). Dirección solo pregunta, cada lunes: *ocupación e importe medio por hotel*. Tres números. Si el fichero es un CSV de 80 GB, el motor **lee las doce columnas** para calcular tres. En cloud, a menudo **pagas por lo que escaneas**, no solo por lo que guardas.

Esa es la pregunta del apartado: ¿el dato viaja **fila a fila** (bien para cobrar en recepción) o **campo a campo** (bien para el informe)? ¿Hace falta que un humano lo abra, o que Spark lo **trocee** entre nodos?

Las prácticas de esta página **no dependen de un CSV ajeno**. Generas el dataset en el propio cuaderno (Jupyter o un [Colab](https://colab.research.google.com/) en blanco). Esquema Avro de reserva: [reserva.avsc](../assets/practicas/reserva.avsc).

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
n = 200_000
hoteles = ["Santander", "Laredo", "Comillas", "Potes", "Noja"]
df = pd.DataFrame({
    "id_reserva": np.arange(n, dtype="int32"),
    "entrada": pd.date_range("2024-01-01", periods=n, freq="min").astype(str),
    "hotel": rng.choice(hoteles, n),
    "noches": rng.integers(1, 8, n, dtype="int32"),
    "importe": rng.uniform(48, 420, n).round(2),
    "canal": rng.choice(["web", "ota", "recepcion"], n),
})
df.to_csv("reservas.csv", index=False)
```

Con `n = 200_000` ya notas diferencias de tamaño y de tiempo. Sube a un millón si la máquina lo aguanta.

## Qué tiene que cumplir el formato

Para que un clúster (Hadoop, Spark) o un almacén en la nube pueda **repartir** el trabajo, el fichero tiene que dejarse **cortar en trozos**. Un JSON con un array de diez millones de objetos entre `[` y `]` es un solo bloque: **un** nodo se lo come entero.

Además suele pedirse:

| Exigencia | En castellano |
| --- | --- |
| Independiente del lenguaje | Lo escribe Java y lo lee Python |
| Expresivo | Nulos de verdad, anidados, un número no es el texto `"10"` |
| Compacto | Pocos bytes y poca CPU al leer |
| Que pueda crecer | Añadir un campo sin reescribir cinco años de histórico |
| Autónomo | El fichero lleva cómo interpretarlo (el esquema) |
| Comprimible | Snappy, gzip, zstd… a cambio de CPU |

Dos familias, no dos religiones:

| | Lo abre el Bloc de notas | Lo come el lago |
| --- | --- | --- |
| Ejemplos | CSV, JSON, XML | Avro, Parquet, ORC |
| Tamaño | Grande | Menor |
| Esquema | A medias o en la cabeza | Suele ir **dentro** del fichero |
| Uso | API, entrega a un compañero | Analítica a escala |

**CSV.** Universal. `01` ¿texto o número? Una coma dentro del campo lo rompe. Para sumar *importe* sueles arrastrar *canal* y *comentarios*.

**JSON / JSONL.** El JSON “de libro” (un objeto enorme) no se parte bien. **JSON Lines** = **una reserva por línea**:

```json
{"id_reserva": 1, "hotel": "Laredo", "noches": 3, "importe": 186.5}
{"id_reserva": 2, "hotel": "Potes", "noches": 2, "importe": null}
```

`null` es JSON. `None` es **Python**. Mezclarlos tumba el parser.

**XML.** Sigue en facturas y administraciones. Más verboso; misma duda: ¿se puede trocear?

## Una reserva junta o un campo junto

Imagina mil reservas `hotel | noches | importe`.

**Todo el registro junto** (CSV, JSON, Avro): leer la reserva 17 es barato. Sumar *solo* importes obliga a saltar hotel y noches mil veces. **Añadir** reservas al final es natural. Encaja en recepción: picas *esta* reserva.

**Cada campo en su sitio** (Parquet, ORC): los importes van juntos. El informe del lunes lee **una** racha. Reconstruir la reserva 17 cruza trozos. Cambiar *una* fila duele (descomprimir, tocar, volver a pegar). Por eso se **parte** por fecha o por hotel. Encaja en el cuadro de mando; **no** como almacén de la caja ([operar frente a analizar](procesamiento.md)).

!!! example "El lunes no necesita el DNI"
    Agregar es resumir. “Importe medio en Laredo” no lee comentarios. Columnar + partición `hotel=Laredo` = menos disco, menos factura.

En servicios tipo Athena o BigQuery el orden de magnitud que verás citado es: **1 TB** de texto plano puede quedar cerca de **un octavo** en columnar comprimido. La cifra exacta cambia; la idea no: **elegir mal el formato en la [carga](ingesta.md) se paga cada consulta**.

## Comprimir no es gratis

El algoritmo busca **repeticiones** (`Laredo, Laredo, Laredo…`) y las recodifica. Viaja menos por la red. A cambio, la CPU **aprieta y destapa**. Sobre 100 GB, “media” deja unos 50 GB y “alta” unos 40. En Big Data suele ganar el que es **rápido**, no el que más aprieta.

| Códec | Velocidad | Ahorro | Típico en |
| --- | --- | --- | --- |
| Gzip / deflate | Media | Medio | Avro, Parquet |
| Bzip2 | Lenta | Alto | Archivado |
| Snappy | Alta | Medio | Avro, Parquet, ORC |
| Zstandard (zstd) | Alta | Alto | Parquet reciente |

```python
df.to_parquet("reservas_zstd.parquet", compression="zstd")
```

```bash
pip install python-snappy   # si usas Snappy con Avro
```

No memorices megas de un recorte ajeno. **Mide el tuyo** al final del taller.

## Avro: el mensaje que se explica solo

[Avro](https://avro.apache.org/) guarda **por filas**, en binario. El esquema (JSON) viaja en la **cabecera**. Quien lee sabe cómo se escribió. Encaja cuando **escribes mucho**, el esquema **cambia** y el destino es un bus ([Kafka](ingesta.md)). Guía: [Getting started (Python)](https://avro.apache.org/docs/1.11.1/getting-started-python/).

Tipos simples: `null`, `boolean`, `int`, `long`, `float`, `double`, `bytes`, `string`.  
Compuestos: `record`, `enum`, `array`, `map`, `union`, `fixed`.

El paquete viejo `avro-python3` está muerto. Instala `avro` (o **fastavro** si el volumen duele: [GitHub](https://github.com/fastavro/fastavro)).

```bash
pip install avro fastavro
```

### Taller 1 — Una reserva con hueco

Descarga [reserva.avsc](../assets/practicas/reserva.avsc). La segunda reserva no trae importe: el esquema admite nulo.

```python
import copy
import json

import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

schema = avro.schema.parse(open("reserva.avsc", "rb").read())

with open("reservas.avro", "wb") as f:
    w = DataFileWriter(f, DatumWriter(), schema)
    w.append({"id_reserva": 1, "hotel": "Laredo", "noches": 3, "importe": 186.5})
    w.append({"id_reserva": 2, "hotel": "Potes", "noches": 2})
    w.close()

with open("reservas.avro", "rb") as f:
    r = DataFileReader(f, DatumReader())
    meta = copy.deepcopy(r.meta)
    print(json.loads(meta["avro.schema"]))
    print(list(r))
    r.close()
```

En pantalla verás `importe: None`: eso es Python. En el fichero el nulo es Avro.

### Taller 2 — Lo mismo, más rápido (fastavro)

```python
import json
import fastavro

with open("reserva.avsc", "rb") as f:
    schema = fastavro.parse_schema(json.load(f))

filas = [
    {"id_reserva": 1, "hotel": "Laredo", "noches": 3, "importe": 186.5},
    {"id_reserva": 2, "hotel": "Potes", "noches": 2},
]
with open("reservas_fa.avro", "wb") as f:
    fastavro.writer(f, schema, filas)
```

### Taller 3 — Del DataFrame al Avro

Usa el `df` del generador (o fíltralo: solo `hotel == "Laredo"`).

```python
from fastavro import parse_schema, writer

schema = parse_schema({
    "name": "Reserva",
    "namespace": "bda.ut1",
    "type": "record",
    "fields": [
        {"name": "id_reserva", "type": "int"},
        {"name": "hotel", "type": "string"},
        {"name": "noches", "type": "int"},
        {"name": "importe", "type": "float"},
        {"name": "canal", "type": "string"},
    ],
})
laredo = df[df["hotel"] == "Laredo"][["id_reserva", "hotel", "noches", "importe", "canal"]]
with open("laredo.avro", "wb") as f:
    writer(f, schema, laredo.to_dict("records"), codec="deflate")
```

Si algún día lo escribes en HDFS, cambia el host por el de **vuestro** lab; el patrón es el de la librería `hdfs` (`InsecureClient` + `AvroWriter`). No copies un nombre de máquina de otro ciclo.

## Arrow: el dato *en la RAM*

[Avro / Parquet / ORC](https://arrow.apache.org/) viven en **disco**. **Arrow** describe columnas **en memoria** para que Python, R o Java las compartan sin copiarlas (*zero-copy*) y el procesador calcule en bloque. Docs: [PyArrow](https://arrow.apache.org/docs/python/).

```bash
pip install pyarrow
```

```python
import pyarrow as pa

schema = pa.schema([
    ("hotel", pa.string()),
    ("noches", pa.int32()),
    ("importe", pa.float32()),
])
tabla = pa.Table.from_pydict(
    {"hotel": ["Laredo", "Potes"], "noches": [3, 2], "importe": [186.5, None]},
    schema=schema,
)
print(tabla)
```

pandas 2 puede leer el CSV con motor Arrow (`dtype_backend="pyarrow"`): textos y nulos suelen ir mejor que con NumPy.

**Feather** (Arrow IPC) es el fichero **entre dos celdas** del mismo pipeline: rapidísimo, no es el archivo de 2020–2026.

```python
import pyarrow.feather as feather

feather.write_feather(df, "reservas.feather")
otro = feather.read_feather("reservas.feather")
```

!!! tip "Dos sitios, dos ficheros"
    Feather = “se lo paso al script de al lado”. Parquet = “lo dejo en el lago para Spark o Athena”.

## Parquet: el lago del informe

[Parquet](https://parquet.apache.org/) es **columnar**, lleva el esquema consigo y parte en *row groups*. El informe que pide `hotel` e `importe` no arrastra `canal`. pandas: `to_parquet` / `read_parquet`.

### Taller 4 — Tabla Arrow → Parquet

```python
import pyarrow.parquet as pq

pq.write_table(tabla, "reservas.parquet")
print(pq.read_table("reservas.parquet"))
```

### Taller 5 — JSONL → Parquet (la L de un [ETL](ingesta.md))

`reservas.jsonl`:

```json
{"hotel": "Laredo", "noches": 3, "importe": 186.5}
{"hotel": "Potes", "noches": 2}
```

```python
import pyarrow.parquet as pq
from pyarrow import json as pajson

pq.write_table(pajson.read_json("reservas.jsonl"), "reservas_desde_json.parquet")
```

### Taller 6 — El generador, a Parquet

```python
df.to_parquet("reservas.parquet")
solo_laredo = pd.read_parquet("reservas.parquet")
solo_laredo = solo_laredo[solo_laredo["hotel"] == "Laredo"]
```

En HDFS, si el clúster define `fs.defaultFS`: `df.to_parquet("hdfs://TU-NODO:9000/reservas.parquet")`.

### Preguntar sin cargarlo: DuckDB

[DuckDB](https://duckdb.org/) es SQL **dentro** del cuaderno (como SQLite, pensado para resúmenes). No traga el Parquet a RAM.

```bash
pip install duckdb
```

```python
import duckdb

print(duckdb.sql(
    "SELECT hotel, AVG(importe) AS media, COUNT(*) AS n "
    "FROM 'reservas.parquet' GROUP BY hotel ORDER BY media DESC"
))
```

Sobre el DataFrame que ya tienes:

```python
print(duckdb.sql(
    "SELECT canal, SUM(importe) AS total FROM df GROUP BY canal"
).df())
```

Si particionas por año: `FROM 'reservas/*.parquet'`. Por dentro habla Arrow: pasar a pandas es casi sin copia.

## ORC: cuando el ecosistema es Hive

[ORC](https://orc.apache.org/) (*Optimized Row Columnar*) nació para **Hive**. Tiras (*stripes*) con mín/máx para **no leer** lo que no puede cumplir el filtro. Compresión habitual `zlib`. pandas `to_orc` (desde 1.5) sale **sin** comprimir si no lo pides.

```python
df.to_orc("reservas.orc")
df.to_orc("reservas_zlib.orc", engine_kwargs={"compression": "zlib"})
```

```python
import pyarrow.orc as orc

orc.write_table(pa.Table.from_pandas(df, preserve_index=False), "reservas_pa.orc")
```

Si el equipo “es Spark”, verás más Parquet. No es que ORC sea peor: es **dónde vive el SQL**.

## Cuando el lago también tiene que *actualizar*

Un `.parquet` suelto no te da “borra esta reserva” ni “cómo estaba el domingo”. [Delta Lake](https://delta.io/), [Iceberg](https://iceberg.apache.org/) y [Hudi](https://hudi.apache.org/) son **Parquet (u ORC) + un diario**: no se edita el fichero viejo; se escribe uno nuevo y se anota.

Eso permite viajar en el tiempo, [ACID](almacenamiento.md) sobre el lago, cambiar columnas y compactar ficheros pequeños. En esta UT basta la idea. En Spark lo veréis como `format("delta")`.

```python
# Cuando lleguéis a Spark, sobre el mismo df de reservas
# df.write.format("delta").save("/ruta/reservas_delta")
```

## Cómo elegir (tarjeta para el examen)

| Situación | Formato | Por qué |
| --- | --- | --- |
| Te lo tiene que leer un humano o una API | CSV / JSON | Se depura |
| Kafka, campos nuevos el mes que viene | **Avro** | Fila + esquema que evoluciona |
| Entre dos celdas del mismo cuaderno | **Feather** | Velocidad |
| Lago + “solo hotel e importe” | **Parquet** | Menos escaneo |
| Tablas Hive | **ORC** | Encaje Hive |
| Explorar en el portátil | **DuckDB** (motor) | SQL sin 500 GB en RAM |
| Picar la reserva en recepción | Ni Parquet ni ORC como almacén | Una fila se actualiza caro |
| Borrar/versionar en el lago | Delta / Iceberg / Hudi | Diario encima |

- Muchas **escrituras** de registros completos → filas (Avro).
- **Lecturas** de tres campos de un millón → columnas.
- Esquema inquieto → Avro. Anidado y subcampos → Parquet.
- Hive → ORC. Spark → Parquet. Cola → Avro.

| | Escribir | Leer | Ocupa |
| --- | --- | --- | --- |
| CSV | Lento | Lento | Mucho |
| Feather | Muy rápido | Muy rápido | Medio |
| Parquet + Snappy | Rápido | Rápido | Poco |
| Avro | Rápido | Rápido | Medio |
| ORC | Medio | Medio | Poco |

!!! tip "Serializar"
    Memoria → bytes (y al revés). Cada conversión puede **perder el tipo**. Elige formato en la frontera y no traduzcas en cada capa.

## Taller medido (lo que se examina)

Abre un cuaderno **en blanco**. Genera el `df` (`n ≥ 200_000`). Cronometra y anota tamaños (`os.path.getsize`) de:

1. `reservas.csv`
2. `reservas.parquet` y `reservas_zstd.parquet`
3. `reservas.orc`
4. `laredo.avro` (solo un hotel, tres o cuatro columnas)
5. `reservas.feather` — compara **tiempo de lectura** frente al CSV

Luego, **sin** cargar el Parquet en pandas:

- importe medio por `hotel` (DuckDB);
- recuento por `canal`;
- misma media **solo con las columnas** `hotel` e `importe` (¿baja el tiempo?).

```python
import os
import time

t0 = time.perf_counter()
df.to_parquet("reservas.parquet")
print("escritura s:", round(time.perf_counter() - t0, 3))
print("bytes:", os.path.getsize("reservas.parquet"))
```

Lo que tienes que poder decir en voz alta: por qué el Parquet ocupó menos que el CSV, por qué Feather se leyó antes y por qué Avro sigue teniendo sentido si el canal de reservas **añade un campo** en abril.

La entrega, si la hay, es Moodle. No hace falta ningún dataset de otro centro ni compartir el cuaderno fuera.
