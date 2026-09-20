---
title: 1.6 Ingesta de datos
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.6. Ingesta de datos

Este apartado es el criterio **b)** del [RA1](ra1.md): cómo **entran** los datos en el sistema. Todavía no hace falta saber Kafka, Spark ni Parquet. Sí hace falta entender el problema con un ejemplo y, después, ponerle nombre a cada idea.

Si este paso falla, el modelo y el cuadro de mando trabajan sobre arena: la cifra queda bien presentada y es mentira.

El índice de la página sigue el mismo hilo que se usa en ingeniería de datos: primero qué es ingerir, luego el pipeline, después ETL y ELT, un taller corto y, al final, la ingesta por dentro y cómo elegir.

!!! tip "Vídeo para estudiar (7 min)"
    Resumen hablado del tema, con las mismas figuras de esta página. **No** sustituye los apuntes ni Moodle.

    <video controls preload="metadata" playsinline style="width:100%;max-width:960px;border-radius:4px;">
      <source src="../../assets/ut1/ingesta-estudio.mp4" type="video/mp4">
    </video>

    Si no se reproduce en el navegador: [descarga el MP4](../assets/ut1/ingesta-estudio.mp4).

??? note "Transcripción"
    **Qué es ingerir.** Coger datos que ya existen (PMS, pasarela, sensores) y llevarlos a otro sitio. Gerencia quiere a las 8 ocupación e importe cobrado por hotel.

    **Hacia atrás.** Destino → transformación → origen. El lago guarda el bruto; el almacén de informes, el dato limpio.

    **Pipeline.** Recoger, colchón, procesar, panel de las 8. No es un producto. OLTP opera; OLAP informa; se copia el hecho.

    **Pipeline ≠ ETL.** Toda ETL es pipeline; no todo pipeline es ETL.

    **Push / pull / poll.** Quién inicia. Conviven en el mismo hotel.

    **ETL.** Extraer (ligera), transformar (no fabricar noches), cargar (índices, partición, transacción). Snapshot el día 1; incremental el martes.

    **ELT.** Extraer → cargar bruto → transformar. Convive con ETL.

    **Hola ETL.** Taller de las tres letras (web + cobro). No es el panel de las 8. pandas ≠ JSONL de DuckDB. En 1.8, Spoon agrega.

    **Formato de la L.** JSON para ver; Parquet para el lago. `to_parquet` pide pyarrow y el `cruce` de pandas.

    **Cola.** Semáforo de recepción, no el panel de las 8. Búfer ≠ contrapresión.

    **Capas.** Ingesta abajo. Lago y almacén conviven.

    **Examen (b).** Origen, quién inicia, reloj, ETL o ELT, destino, formato, por qué no el de al lado. Un logo solo no puntúa.


## Introducción

**Ingerir datos** es el proceso de coger información que ya existe en varios sitios —un fichero, una base de datos, una web, un sensor— y llevarla a **otro** sistema, donde se podrá guardar o procesar.

El contexto es el **[caso del grupo hotelero](caso-hotel.md)** (Santander, Laredo, Comillas, Potes). Resumen para no perderse:

- Recepción pica las reservas en el **programa de reservas** del hotel (en la jerga, PMS: *Property Management System*).
- La pasarela de pago sabe qué estancias se han cobrado.
- En las habitaciones hay sensores de ocupación.
- Dirección quiere, cada mañana a las 8, **ocupación e importe cobrado por hotel**.

Esos datos **ya existen**. No están, de entrada, en el sitio donde gerencia los mira. Llevarlos de un sitio al otro es ingesta.

![Ingesta de datos en el hotel: reservas, cobros y sensores hacia el lago; el panel es otro paso](../assets/ut1/ingesta-hotel.png)

Hasta que el dato no entra, el resto de la [arquitectura](arquitectura.md) está vacía. Un buen proceso de ingesta tiene que ser:

- **Flexible:** mañana aparece otra fuente (una OTA —web tipo Booking que vende habitaciones—, un Excel de un hotel nuevo) y no tiras el diseño.
- **Ágil:** si gerencia cambia la pregunta, no tardas tres meses en volver a meter los datos.

La productividad del equipo depende más de esto que del logo de la herramienta.

Finanzas cierra el día a las 23:00. Los sensores publican cada medio minuto. Recepción no puede parar.

Antes de elegir un programa, diseñas **hacia atrás**:

1. ¿Qué tiene que ver gerencia a las 8? (destino)
2. ¿Hay que cruzar reservas con cobros, quitar canceladas, unificar el nombre del canal? (transformación)
3. ¿El dato vive en el programa de reservas, en la pasarela, en una carpeta FTP (un sitio en red donde se dejan ficheros) o en los sensores? (origen)

Sin esa pregunta de negocio, unificar veinte fuentes es un proyecto largo que no sabes cuándo termina.

El sitio típico al que llega lo ingerido **en bruto** es el **lago de datos** (*data lake*). El **almacén de informes** (*data warehouse*) es otro sitio: ahí el dato ya va limpio, pensado para el panel. En [1.3](almacenamiento.md) se distinguen; aquí basta: la ingesta suele aterrizar primero en el lago.

## Pipeline de datos

Un **pipeline** (tubería) es una forma de organizar el trabajo en **fases**. No es un producto que compras. Describe los pasos y, si hace falta, las tecnologías entre un origen y un destino.

En lo más simple: recoger, guardar, procesar y **dejar algo útil**.

![Fases de un pipeline de datos](../assets/ut1/pipeline.png)

Aunque a menudo se intercambian los términos, **pipeline** y **ETL** no son lo mismo:

- Toda ETL es un pipeline (mueve datos en fases).
- **No** todo pipeline es una ETL. Un sensor que deja un mensaje en una cola y un filtro que tira duplicados también es tubería, aunque no hagas un cruce ni una carga a un almacén de informes.

### Fases del pipeline

Sumar importes de mil reservas es caro para la máquina. Si lanzas ese cálculo **sobre el programa que cobra**, el mostrador espera: el cliente también.

Por eso se **copia** el hecho a otro sitio:

- El sistema que opera el día a día (picar la reserva, cobrar) se llama **OLTP** (*Online Transaction Processing*). Ejemplo: el programa de recepción.
- El sistema que analiza e informa (el panel de las 8) se llama **OLAP** (*Online Analytical Processing*). Ejemplo: el almacén de informes de gerencia.

No son dos marcas. Son dos oficios. El pipeline los separa para que uno no tumbe al otro.

![OLTP opera en recepción; OLAP informa a gerencia: el hecho se copia](../assets/ut1/oltp-olap.png)

```mermaid
flowchart LR
  origen[Programa de reservas y pasarela] --> recoger[1 Recoger]
  recoger --> buffer[2 Guardar un colchón]
  buffer --> procesar[3 Procesar]
  procesar --> panel[4 Panel de las 8]
```

1. **Recoger.** Copias el hecho fuera de recepción: un fichero, una consulta a la base de datos, un mensaje.
2. **Guardar un colchón.** Si el panel va lento, el dato no se pierde. Puede ser una carpeta, una zona bruta o una cola de mensajes.
3. **Procesar.** Filtras, cruzas, sumas. Aquí se limpia de verdad.
4. **Dejar algo útil.** El panel, un Excel, una base de informes.

Un mismo **job** (trabajo programado: “a las 02:00, lanza esta tubería”) que “lo hace todo” parece más simple el día 1. El martes que el programa de reservas añade una columna, se rompe recoger, cruzar y pintar a la vez.

Las fuentes no hablan igual. Un canal llega como `web` y otro como `WEB`. Un número llega como texto `"10"`. Hay huecos.

Dejar el dato **listo** para usarlo se llama **data wrangling** (preparación o limpieza de datos). No es un programa: es el oficio de pasar del bruto al dato que ya tiene sentido.

### Pipeline iterativo

Este proceso de recoger, guardar, procesar y analizar **se itera**. Gerencia pregunta: “¿cancelan más los del viernes?”. Si ese campo no está, vuelves al origen, ingestes otra vez e integras. No es un acto único el día 1.

Sobre una hipótesis de negocio se comprueba lo ya almacenado. Si falta información, se recogen datos nuevos, pasan por todo el pipeline y se integran con lo existente. Si en analítica no sale lo esperado, se vuelve a la ingesta. Así, hasta producir el resultado que el hotel necesita.

## ETL

Una **ETL** es un proceso que lleva información de un punto A a un punto B en tres fases. Las siglas vienen del inglés:

1. **E** — *Extract* (extraer)
2. **T** — *Transform* (transformar)
3. **L** — *Load* (cargar)

Se puede hacer con un script, con Python o con una herramienta visual. En Big Data la herramienta tiene que ser **flexible** (varios formatos), **tolerante a fallos** (si cae a mitad, que se sepa) y capaz de **conectarse** a muchos orígenes.

Unificar veinte fuentes **gasta** el proyecto. La veracidad del dato se cuida aquí: si entra basura, el panel miente.

![Esquema ETL](../assets/ut1/etl.png)

### Extracción

Recopilas los datos del origen y los llevas a una zona de trabajo, sin cambiar todavía el programa de recepción.

Orígenes típicos:

- **CSV:** fichero de texto en tabla, columnas separadas por comas (o punto y coma). Excel lo abre.
- **Tabla SQL:** datos en filas y columnas dentro de un gestor ([PostgreSQL](https://www.postgresql.org/), [MySQL](https://www.mysql.com/), [SQL Server](https://www.microsoft.com/sql-server/)…).
- **API / REST:** pides datos por HTTP (el mismo protocolo del navegador) y sueles recibir **JSON** (texto con llaves `{ }` que un programa lee fácil).
- Un mensaje de un bus (Kafka u otra cola).

Dos reglas:

1. Tiene que ser **ligera**. Recepción casi no se entera.
2. **No** se modifica el dato operativo. Si colapsa el programa de reservas, la empresa pierde dinero *cobrando*.

Compruebas que el lote **trae lo que dice traer** (columnas, tipos). Si no, se **aparta**: un job “en verde” con filas cojas envenena el panel.

Hay tres formas de iniciar el movimiento. No son tres productos.

![Push, pull y poll: quién inicia el movimiento del dato](../assets/ut1/push-pull-poll.png)

| | **Push** (empujar) | **Pull** (tirar) | **Poll** (preguntar) |
| --- | --- | --- | --- |
| Quién inicia | El **origen** envía | El **destino** va a buscar | El destino **mira** de vez en cuando; si hay cambio, tira |
| En el hotel | Cada alta de reserva se publica al momento | A las 02:00 lees la tabla de ocupaciones | Cada 15 min listas la carpeta FTP; solo bajas si cambió la fecha |
| Encaja | Evento, sensor, aviso automático (*webhook*: el origen llama a una URL tuya cuando pasa algo) | Lote nocturno, leer una base **SQL** (el lenguaje de las bases de datos en tablas) | Carpetas, buzones, **API** (un “mostrador” por internet que, si preguntas bien, te devuelve datos) |
| Riesgo | Te inundan, o el origen no sabe adónde empujar | Tiras en hora punta y tumbas la recepción | Preguntas poco = te enteras tarde; preguntas mucho = molestas |

No hay uno “más Big Data”. En la misma empresa conviven. El *push* encaja con el flujo continuo; *pull* y *poll*, con el trabajo por lotes.

Más adelante hay un catálogo con nombre y para qué sirve cada herramienta. Primero clava **quién da el primer paso**.

### Transformación

Dejas formato y contenido que el destino entiende. En el hotel suele ser:

- Cambiar codificación o mayúsculas (`WEB` → `web`).
- Quitar duplicados de `id_reserva`.
- Cruzar reservas con cobros.
- Agregar importe por hotel.
- Generar un identificador estable (`hotel-fecha`).
- Calcular un indicador (ocupación %).
- Quedarte solo con las filas que el informe necesita.

**Sí:** mejorar calidad, integrar, normalizar, crear una clave que no existía en origen.  
**No:** fabricar noches que nadie picó, borrar el canal porque “estorbaba”, ni una regla que un día sí y otro no.

En continuo, una transformación pesada (cruzar veinte fuentes) **no** va en el mismo milisegundo que el sensor. A veces la T gorda espera al lote.

### Carga

Escribes en el destino, **adaptándote** a cómo ese destino espera recibir datos: una sentencia SQL masiva, un fichero que el almacén lee, una carpeta en la nube.

Cada destino tiene su vía rápida. Tres palancas que, si las ignoras, tiran una carga grande:

| Palanca | Si la ignoras |
| --- | --- |
| **Índices** (atajos de búsqueda, como el índice de un libro) | Reconstruirlos fila a fila en millones de reservas tira la carga |
| **Partición** (guardar en “cajones”: por fecha o por hotel) | Si partes mal, el panel barre todo |
| **Tamaño de la transacción** (cuántas filas confirmas de golpe) | Confirmar diez millones de golpe puede tumbar el destino; confirmar de una en una, eternizar la carga |

Cien filas de práctica **no** demuestran la carga.

Tampoco es lo mismo el tamaño el día 1 y el martes. La **primera carga** (*snapshot*) es una foto de todo: tres años de reservas. El job del martes es **incremental**: solo lo nuevo o lo que cambió. Mezclarlas es un error caro. Eso también cambia cuánto **extraes**: no pides tres años cada noche.

El **formato** de lo que escribes (CSV, JSON, Parquet…) es parte de esta L: lo vemos justo después del [Hola ETL](#hola-etl), cuando ya tienes un `cruce`. El catálogo completo está en [1.7](formatos.md).

## ELT

**ELT** cambia las letras: extraer → **cargar** → transformar.

Los datos se dejan primero **aún sin limpiar**. El sitio típico es el [lago](almacenamiento.md). En la nube a veces es un almacén **elástico** ([Snowflake](https://www.snowflake.com/), BigQuery…), que sí puede tragar bruto y transformar después. El *data warehouse* clásico de [1.3](almacenamiento.md) —pasillos fijos, columnas acordadas— suele querer el dato **ya limpio**: ahí encaja ETL, no ELT.

La transformación la hace después el destino: SQL, un notebook, o [**Apache Spark**](https://spark.apache.org/) (un motor que reparte el cálculo entre varios ordenadores; [**PySpark**](https://spark.apache.org/docs/latest/api/python/) es Spark usado desde Python).

| | **ETL** | **ELT** |
| --- | --- | --- |
| Orden | Extraer → **transformar** → cargar | Extraer → **cargar** → transformar |
| Dónde se limpia | Un motor en medio (script, [Pentaho](pentaho.md), [Talend](https://www.talend.com/)) | El lago o un almacén **elástico** en la nube |
| Cuándo | El destino **no** debe tragar basura | El destino aguanta bruto y hay **varios** consumidores |
| Ver el crudo | Más tarde | Antes |
| Si gerencia cambia la pregunta | Retocas la T **antes** de recargar | Consulta nueva **si** esas columnas ya estaban en el bruto |

ELT no es “ETL al revés para quedar moderno”. Cambia **quién** trabaja y **cuándo** se ve el dato:

![ETL frente a ELT: cambia cuándo se limpia el dato](../assets/ut1/etl-vs-elt.png)

- El ingeniero deja el bruto **pronto**. Finanzas y ciencia de datos pueden mirarlo antes del cruce perfecto.
- La limpieza la puede hacer quien conoce el negocio, no solo el equipo de tuberías.

El mercado en la nube empuja ELT (el almacén es potente). **ETL sigue** cuando el destino es rígido, o cuando en aula usas Pentaho. En una cadena hotelera real **conviven**: el cierre de facturación suele ser ETL; el lago de ocupación, ELT.

## Herramientas ETL

No hace falta una herramienta con las letras “ETL” en el nombre: un script también extrae, transforma y carga. Cuando el volumen y las fuentes crecen, conviene un programa que ya traiga conectores, planificación y registro de errores.

En Big Data no vale “cualquier copiar y pegar”. Tiene que:

- **Conectar** con muchos sitios y formatos: Excel, bases transaccionales (las del día a día), XML, CSV, JSON, HDFS, Hive, S3, peticiones HTTP / REST, APIs de terceros, logs…
- **Planificar** el trabajo: cada noche (*batch*), cuando llega un fichero (evento) o en continuo (*streaming*).
- **Transformar** a tres niveles:
    - simples: tipos, textos, codificaciones, un cálculo;
    - intermedias: sumar por hotel, *lookup* (buscar un código en otra tabla, p. ej. el nombre del canal);
    - complejas: un modelo de IA o código de otro lenguaje (eso se sale de esta UT).
- **Dejar rastro y gestionar errores:** qué corrió, qué falló, y qué hacer entonces. Sin eso, el job “en verde” es teatro.

([Hadoop](https://hadoop.apache.org/) es el ecosistema clásico de Big Data: varios PCs compartiendo disco y cálculo. [HDFS](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html) es su sistema de ficheros: una carpeta enorme repartida. [Hive](https://hive.apache.org/) permite consultar esos ficheros con SQL. [S3](https://aws.amazon.com/s3/) es el almacén de objetos de Amazon: carpetas en la nube. XML es otro formato de texto etiquetado, más viejo que JSON. Un *log* es el diario de lo que hace un programa. HTTP / REST son la forma habitual de pedir datos a una API por internet.)

Son programas (muchos con pantalla) para diseñar el flujo sin escribirlo todo a mano:

| Herramienta | Qué es, en una frase | En esta aula |
| --- | --- | --- |
| **[Pentaho Data Integration (PDI)](https://www.hitachivantara.com/en-us/products/pentaho-plus-platform.html)** | Suite de ETL visual. Código en [GitHub](https://github.com/pentaho/pentaho-kettle). **Spoon** es el editor; **Pan** y **Kitchen** ejecutan transformaciones y jobs. | La practicáis en [1.8](pentaho.md) |
| **[Talend Open Studio](https://www.talend.com/)** | Otra ETL visual, muy usada en empresas | La oiréis; no la montamos aquí |
| **[Informatica Data Integration](https://www.informatica.com/)** | Suite comercial grande, típica en corporaciones | Nombre de catálogo |
| **[Oracle Data Integrator (ODI)](https://www.oracle.com/integration/data-integrator/)** | ETL del ecosistema Oracle | Nombre de catálogo |
| **[MuleSoft](https://www.mulesoft.com/)** | Más bien integración de aplicaciones (APIs), no solo ficheros | Nombre de catálogo |

Las empresas no eligen “solo Pentaho” o “solo Python”. Mezclan:

- la **suite visual** para conectores y planificación;
- **[Python](https://www.python.org/)** para lo nuevo, lo no estructurado o lo que la pantalla no cubre:
    - **[pandas](https://pandas.pydata.org/):** librería para trabajar con tablas en memoria (`DataFrame`). Es el Excel de Python.
    - **[PySpark](https://spark.apache.org/docs/latest/api/python/):** el mismo oficio, pero el cálculo se reparte en un **clúster** (varios ordenadores trabajando como uno).
    - **[DuckDB](https://duckdb.org/):** base analítica *embebida* (no hay servidor que instalar): SQL directo sobre CSV o Parquet en tu disco. Documentación: [duckdb.org/docs](https://duckdb.org/docs/).
- **[Apache Airflow](https://airflow.apache.org/):** un **orquestador**. No transforma el dato: dispara pasos (“primero extrae, luego cruza, luego carga”) y avisa si uno falla. No lo montáis en esta UT; sí sabéis para qué existe.

Sin planificación y sin registro de errores, da igual la herramienta.

## Hola ETL

Este taller enseña las **tres letras**, no pinta el panel de ocupación de las 8. El objetivo es más pequeño: reservas del canal `web` **con cobro**, y una etiqueta `hotel (web)`. En [1.8](pentaho.md) el mismo cruce se vuelve informe agregado por hotel y canal.

Necesitas un cuaderno de Python:

- **[Jupyter](https://jupyter.org/):** programa en tu PC que mezcla texto y código, celda a celda.
- **[Google Colab](https://colab.research.google.com/):** lo mismo, pero en el navegador, sin instalar nada.

**[pandas](https://pandas.pydata.org/)** es la librería de Python para tablas. Un `DataFrame` es una hoja: filas y columnas con nombre. **[NumPy](https://numpy.org/)** (`numpy`) genera números al azar para fabricar el ejemplo.

En [1.7](formatos.md) generarás **otro** `reservas.csv` (más filas, campo `entrada`, **sin** cobros). Estos dos ficheros no se reutilizan allí.

- `reservas.csv`: quién reservó, en qué hotel, por qué canal, noches e importe.
- `cobros.csv`: qué reservas **ya** están cobradas y por qué medio. No todas las reservas tienen fila. Eso es real.

- **E** = leer los dos ficheros.
- **T** = filtrar, cruzar por `id_reserva` y crear la etiqueta. Un *join* (cruce) une filas que comparten una clave.
- **L** = escribir un **JSON** (texto estructurado) para verlo en clase.

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
n = 8_000
hoteles = ["Santander", "Laredo", "Comillas", "Potes"]
reservas = pd.DataFrame({
    "id_reserva": np.arange(n, dtype="int32"),
    "hotel": rng.choice(hoteles, n),
    "canal": rng.choice(["web", "ota", "recepcion"], n),
    "noches": rng.integers(1, 8, n, dtype="int32"),
    "importe": rng.uniform(48, 420, n).round(2),
})
# ~70 % de las reservas tienen cobro
mask = rng.random(n) < 0.7
cobros = pd.DataFrame({
    "id_reserva": reservas.loc[mask, "id_reserva"].to_numpy(),
    "medio": rng.choice(["tarjeta", "efectivo", "bizum"], mask.sum()),
    "cobrado": reservas.loc[mask, "importe"].to_numpy(),
})
reservas.to_csv("reservas.csv", index=False)
cobros.to_csv("cobros.csv", index=False)
```

### pandas

Leemos CSV, filtramos, cruzamos y escribimos JSON. `merge(..., how="inner")` es un **inner join**: solo las reservas que **sí** tienen cobro. Un `left` (*left join*) dejaría reservas web sin `medio`: útil para ver impagados; no es el objetivo de este taller.

```python
# E
df_r = pd.read_csv("reservas.csv")
df_c = pd.read_csv("cobros.csv")

# T
web = df_r[df_r["canal"] == "web"]
cruce = web.merge(df_c, on="id_reserva", how="inner")
cruce["etiqueta"] = cruce["hotel"] + " (web)"

# L
cruce.to_json("web_cobrado.json", orient="records", force_ascii=False)
```

### Hola DuckDB

**[DuckDB](https://duckdb.org/)** es una base de datos **analítica** y **embebida** (sitio oficial: [duckdb.org](https://duckdb.org/); código: [github.com/duckdb/duckdb](https://github.com/duckdb/duckdb)):

- Analítica: está pensada para leer mucho y agregar (sumar por hotel), no para que recepción pique una reserva.
- Embebida: no instalas un servidor. Es una librería (`pip install duckdb`). Corre **dentro** de Python, en tu proceso.
- Habla **SQL** directo sobre ficheros locales (CSV, Parquet, JSON) **sin** cargarlos antes en PostgreSQL. Por dentro es **columnar**: guarda por columnas, así que “importe por hotel” no tiene que leer las doce columnas.

Para ETL, eso significa: extraes (lees el CSV como tabla), transformas (un `SELECT` con `JOIN` y `WHERE`) y cargas (`COPY` a otro fichero).

Instalación: `pip install duckdb` (guía: [duckdb.org/docs/installation](https://duckdb.org/docs/installation/)).

Mismas tres letras que pandas, idioma SQL:

```python
import duckdb

duckdb.sql("""
COPY (
    SELECT
        r.id_reserva,
        r.hotel,
        r.importe,
        c.medio,
        r.hotel || ' (web)' AS etiqueta
    FROM read_csv('reservas.csv', header=true) AS r
    INNER JOIN read_csv('cobros.csv', header=true) AS c
        USING (id_reserva)
    WHERE r.canal = 'web'
) TO 'web_cobrado_ddb.json' (FORMAT JSON)
""")
```

No compares los dos JSON como si fueran el mismo fichero:

- pandas (`orient="records"`) escribe un **array** `[ {...}, {...} ]`.
- DuckDB (`FORMAT JSON`) suele escribir **JSONL**: una reserva por línea.

Para **verlos** en clase valen los dos. Para el lago, el formato de la L no es este JSON: es Parquet (siguiente apartado). En [1.8](pentaho.md) verás el **mismo cruce** en Spoon, pero el cliente pide un informe agregado, no este JSON.

### La L: formato de la carga

Escribir “un fichero” no basta. El siguiente paso tiene que **partir** el archivo, comprimirlo y consultarlo sin arruinarte. El catálogo completo está en [1.7](formatos.md). Aquí solo la decisión de la **L**, ahora que ya tienes un `cruce`:

- **CSV / JSON:** texto que un humano abre. JSONL es JSON **una reserva por línea** (se puede partir; un único array `[...]` enorme, no).
- **[Avro](https://avro.apache.org/):** cada fila viaja con su **esquema** (de qué tipo es cada campo). Típico en colas: mañana añaden un campo y el consumidor no se rompe del todo.
- **[Parquet](https://parquet.apache.org/):** formato **columnar** (guarda la columna `importe` junta). El informe de las 8 lee hotel e importe y **no** carga las doce columnas. Muy usado en lagos y en Spark.
- **[ORC](https://orc.apache.org/):** parecido a Parquet; nació en el mundo Hive.
- **[Feather / Arrow](https://arrow.apache.org/):** pensado para pasar tablas **rápido** entre procesos Python/R. No es el archivo de “guardar tres años”.
- **[Snappy](https://google.github.io/snappy/)** (y gzip, zstd): **códecs** de compresión. Ocupan menos y viajan menos; cuestan CPU.

| Destino de esta carga | Formato habitual | Por qué, en una frase |
| --- | --- | --- |
| Que lo abra un compañero | CSV / JSON | Se depura |
| Cola de mensajes; mañana añaden un campo | Avro | Cada fila lleva su esquema |
| Lago / informe de las 8 | Parquet | Lee hotel e importe, no las doce columnas |
| El script de al lado, ahora | Feather | Rápido; no es archivo de años |
| Tablas Hive | ORC (o Parquet si el equipo usa Spark) | Encaje con esa pila |
| El programa de recepción | Ni Parquet ni ORC como almacén | Actualizar una fila es caro |

Si el cruce pesara y el destino fuera el lago, usa el `cruce` del **pandas** de arriba (`pip install pyarrow`):

```python
cruce.to_parquet("web_cobrado.parquet")
```

Si solo corriste DuckDB, no existe `cruce`. Entonces:

```python
duckdb.sql("""
COPY (
    SELECT r.id_reserva, r.hotel, r.importe, c.medio
    FROM read_csv('reservas.csv', header=true) AS r
    INNER JOIN read_csv('cobros.csv', header=true) AS c
        USING (id_reserva)
    WHERE r.canal = 'web'
) TO 'web_cobrado.parquet' (FORMAT PARQUET)
""")
```

Comprimir ocupa menos y viaja menos; cuesta CPU. En volumen suele ganar un códec **rápido** (por ejemplo Snappy).

!!! tip "Antes de dar el procedimiento por cerrado"
    ¿El destino **escribe** muchos registros o **lee** tres columnas? ¿Se puede **partir** el fichero? El detalle de cada formato, en [1.7](formatos.md).

## La ingesta por dentro

La ingesta extrae los datos desde la fuente donde se crean y los carga en un destino o zona temporal. Un pipeline sencillo puede aplicar una transformación ligera (filtrar, enriquecer) **antes** de escribir. El cruce gordo y las sumas para el informe viven en un pipeline **siguiente**. No es pereza: es no bloquear la puerta.

La ingesta es la **primera** capa de la [arquitectura](arquitectura.md). Suele ser la más pesada: muchas fuentes, ritmos distintos. El día 1 **priorizas** (no todas importan), **validas** cada lote aparte y **enrutas**.

| Orígenes habituales | Destinos habituales |
| --- | --- |
| Una cola que ya recogió sensores (p. ej. [Kafka](https://kafka.apache.org/)) | Otra cola |
| Una tabla **SQL**, a menudo por **[JDBC](https://docs.oracle.com/javase/tutorial/jdbc/overview/index.html)** (el “enchufe” estándar de Java/muchas ETL para hablar con la base) | SQL o **NoSQL** (bases no solo en tablas: documentos, clave-valor… p. ej. **[MongoDB](https://www.mongodb.com/)**) |
| Una API REST que devuelve JSON | El lago: carpeta en **[HDFS](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)** (Hadoop) o **[S3](https://aws.amazon.com/s3/)** (Amazon) |
| Una carpeta de ficheros | Una **plataforma de datos**: **[Snowflake](https://www.snowflake.com/)** o **[Databricks](https://www.databricks.com/)** son almacenes/analítica en la nube; no los montáis aquí |

Cuatro preguntas que recuerdan a las [5 V](por-que-big-data.md), aplicadas al *cómo entra*:

| Pregunta | En el hotel |
| --- | --- |
| ¿A qué ritmo llega? | Sensor cada 30 s frente a cierre a las 23:00 |
| ¿Cuántos GB/día, y si abrís otro hotel? | Tamaño y crecimiento |
| ¿Lote, trozo o continuo? | Finanzas frente a recepción |
| ¿Tabla, JSON, imagen del DNI? | Formato (el DNI, a menudo, **no** se ingiere) |

Un CSV de canales y un sensor cada 30 segundos **no** van por el mismo tubo.

Si el sensor de habitación no puede esperar al informe de las 8, hace falta **desacoplar** al que produce el dato del que lo consume: cada uno trabaja a su ritmo. El **panel de las 8** sigue siendo un lote nocturno. La cola es para el **semáforo** de recepción, no para ese panel.

Una **cola de mensajes** es un buzón intermedio. No es una base de datos de informes: solo guarda avisos un rato.

![Productor, cola y semáforo de recepción: si el semáforo va lento, la cola aguanta](../assets/ut1/cola-mensajes.png)

- Un **productor** deja el evento (la habitación se ocupó).
- Un **consumidor** lo recoge cuando puede (el semáforo de recepción, un script).
- Si el consumidor va lento, la cola **aguanta** un rato: es un **búfer**.
- Si además el sistema **frena al productor** para que no siga empujando, eso es *contrapresión* (*back pressure*). No son lo mismo: el búfer absorbe; la contrapresión pide que se afloje.

En muchas colas clásicas, al recoger el mensaje **desaparece**. En sistemas repartidos en varios ordenadores (varios PCs colaborando) el orden entre canales no está garantizado: hay que contar con que un nodo falle.

Herramientas de este oficio (las verás con más detalle en el catálogo de más abajo):

- **Apache Kafka:** un “bus” de mensajes. Sitio oficial: [kafka.apache.org](https://kafka.apache.org/). Muchos productores publican en un canal (*topic*, como un tablón con nombre: `reservas.altas`) y muchos consumidores se suscriben. El mensaje no tiene por qué desaparecer al leerlo.
- **RabbitMQ:** una cola más clásica ([rabbitmq.com](https://www.rabbitmq.com/)): el productor deja el recado, el consumidor lo recoge y, en general, se borra.
- En la nube hay equivalentes: [**Kinesis**](https://aws.amazon.com/kinesis/) (Amazon), [**Event Hubs**](https://azure.microsoft.com/products/event-hubs/) (Azure), [**Pub/Sub**](https://cloud.google.com/pubsub) (Google).

En voz alta: “desacoplar al sensor del semáforo de recepción” → familia **mensajería**, no el volcado nocturno del panel de las 8.

### Batch vs Streaming

El movimiento de datos entre orígenes y destinos puede ser:

| | **Lote** (*batch*) | **Micro-lote** | **Continuo** (*streaming*) |
| --- | --- | --- | --- |
| Cuándo | Cada X horas o al llegar un fichero | Cada pocos minutos, un bloque pequeño | En cuanto aparece el dato |
| Retraso | Horas; a menudo da igual | Compromiso | Segundos o menos |
| Encaja | Cierre de finanzas, volcado nocturno | Panel “casi en vivo” | Sensor, clic, log |

**Síncrono:** esperas a que el destino confirme que lo ha recibido. **Asíncrono:** sueltas el mensaje y sigues trabajando.

- **Batch:** el proceso se ejecuta de forma periódica a partir de datos estáticos. Encaja con grandes volúmenes cuando la latencia (minutos u horas) no es lo más importante. Ejemplos de familia: [Sqoop](https://sqoop.apache.org/), un script Python, un job de Spark o de Pentaho.
- **Streaming:** los datos se leen, se tocan y se cargan en cuanto llegan. La latencia es crítica. Ejemplos de familia: [Kafka](https://kafka.apache.org/), [NiFi](https://nifi.apache.org/), Spark Streaming.

### Arquitectura

Si te basas en la arquitectura por capas, la ingesta es la de **abajo**: **lleva** el dato desde las fuentes; las fuentes no *son* la capa. El dibujo de esta página es el **resumen de cuatro pisos**. El edificio completo (ocho capas, con colección, consulta, seguridad y monitorización) está en [1.5](arquitectura.md). Los números de aquí **no** son los de allí: aquí el 4 es el panel; allí el 4 es el job.

![La ingesta es la capa de abajo: el dato sube hacia el panel](../assets/ut1/capas-ingesta.png)

Es el paso más pesado, por tiempo y por recursos. Es normal ingerir desde decenas de fuentes, a velocidades distintas y en formatos distintos. Por eso, el día 1:

1. **Priorizas** las fuentes (no todas importan igual).
2. **Validas** cada lote o fichero por separado.
3. **Enrutas** cada elemento a su destino correcto.

## Herramientas de Ingesta de datos

Citas la **familia**. El producto concreto cambia de año. No memorices logos; sí debes poder decir *para qué sirve* cada una si te la nombran.

Las herramientas de ingesta para ecosistemas Big Data se agrupan así:

- **[Apache Sqoop](https://sqoop.apache.org/):** puente **SQL ↔ Hadoop**. Copia tablas enteras (o incrementales) hacia HDFS/Hive/**[HBase](https://hbase.apache.org/)** (base NoSQL sobre Hadoop) y al revés. Se usa sobre todo por **comandos**. El proyecto está en mantenimiento: la *idea* (volcado nocturno *pull*) sigue; el binario concreto, no siempre.
- **[Apache Flume](https://flume.apache.org/):** tubería de **logs y eventos** hacia HDFS o HBase, en flujo. Encaja con clics o sensores, no con “toda la tabla de reservas”.
- **[Apache NiFi](https://nifi.apache.org/):** pantalla con **cajas y flechas** (un grafo). Cargas de un origen, pasas por procesos y vuelcas a otro. Vale lote y flujo.
- **[Logstash](https://www.elastic.co/logstash)** (Elastic): nació para meter logs en **[Elasticsearch](https://www.elastic.co/elasticsearch)** (un motor de búsqueda de documentos/texto, no una base de reservas). Hoy admite muchas entradas y salidas, también nube.
- **[AWS Glue](https://aws.amazon.com/glue/):** ETL **gestionada** en Amazon: no instalas servidor; lo lanzas desde la consola. Descubre esquemas. **[Athena](https://aws.amazon.com/athena/)** no es Glue: es SQL sobre ficheros en S3; usa el **catálogo** de Glue para saber qué tablas hay.

Por otro lado hay sistemas de mensajería con funciones propias de ingesta **asíncrona**:

- **[Kafka](https://kafka.apache.org/):** publicador/suscriptor, pensado para mucho volumen.
- **[RabbitMQ](https://www.rabbitmq.com/):** cola clásica productor-consumidor.
- **[Kinesis](https://aws.amazon.com/kinesis/) / [Event Hubs](https://azure.microsoft.com/products/event-hubs/) / [Pub/Sub](https://cloud.google.com/pubsub):** lo mismo en AWS, Azure y Google.

Finalmente, hay conectores que facilitan llevar **SaaS** (software que usas por internet: el PMS en la nube, el CRM, la pasarela) hacia el lago, sin programar cada API:

- **[Fivetran](https://www.fivetran.com/):** plataforma comercial con cientos de conectores; mueve datos casi “enchufar y listo”.
- **[Airbyte](https://airbyte.com/):** la misma idea, con versión **open source** ([GitHub](https://github.com/airbytehq/airbyte)) y otra gestionada en cloud.

| Necesidad | Familia | Ejemplos |
| --- | --- | --- |
| Tabla SQL grande, de noche, hacia el lago | Puente por lotes (*pull*) | Sqoop, job Spark, Pentaho |
| Logs o clics que tienen que verse ya | Flujo (*push*) | Flume, Kafka + consumidor, NiFi |
| Varias fuentes y un grafo en pantalla | ETL visual | NiFi, [Pentaho](pentaho.md) |
| Logs hacia un buscador | Tubería de logs | Logstash |
| ETL gestionado en un proveedor | Servicio cloud | Glue (AWS) |
| El productor no espera al consumidor | Mensajería | Kafka, RabbitMQ, Kinesis, Event Hubs, Pub/Sub |
| Cientos de aplicaciones hacia el lago | Conectores ELT | Airbyte, Fivetran |

## Consideraciones

En un supuesto de aula o de examen, clava **estas** decisiones y justifícalas. Las preguntas de cada bloque son las que usa la [actividad 9](#actividades).

### Origen y formato

- ¿Cuál es el origen: PMS, pasarela, carpeta FTP, sensores, API de una OTA?
- ¿Hay que **cruzar** dos sistemas (reservas + cobros)?
- ¿Estructurado (tabla), JSON o una imagen del DNI?
- ¿Qué volumen diario, y si abrís otro hotel?
- ¿Pueden aparecer fuentes nuevas mañana?

### Reloj / latencia

- ¿Quién inicia: push, pull o poll?
- ¿El dato que llega tarde sigue valiendo? El cierre de ayer sí; el semáforo de habitación libre, no.
- ¿Lote, micro-lote o continuo?
- ¿Síncrono (esperas confirmación) o asíncrono (sueltas y sigues)?
- Si llega tarde, ¿hasta cuándo se considera válido?

### Actualizaciones

El martes el programa de reservas añade `motivo_cancelacion`:

- **¿Quién te avisa?** Si nadie, el job sigue “bien” y el campo nuevo se pierde.
- **¿Guardas historial o pitas encima?** Un *update* borra cómo estaba la reserva el lunes. Borrar e insertar, o versionar, dejan rastro.
- **¿Reprocesas?** Si gerencia cambia el indicador, a veces basta una consulta nueva sobre el bruto (ELT). A veces hay que **volver a ingerir**. Reusar lo ya cargado evita tragarte otra vez tres años de SQL.

Si transformaste al vuelo y tiraste el original, el cambio de pregunta te obliga a pedir otra extracción. Eso duele.

### Transformaciones

- ¿ETL o ELT? ¿El destino traga bruto (lago / almacén elástico) o exige limpio (warehouse clásico de [1.3](almacenamiento.md))?
- ¿Hace falta transformar **al recoger**, o puede esperar al procesar?
- En continuo, ¿una T pesada (ocupación %, cruce de veinte fuentes) cabe en el mismo milisegundo que el sensor?

### Destino

- ¿Una carpeta “tonta” o un almacén con SQL? ¿Uno o varios destinos?
- ¿Mismo formato que el origen o [formato de la L](#la-l-formato-de-la-carga) (Parquet, Avro, JSONL…)?
- ¿Cómo se va a consultar: por hotel, por fecha, al azar?

### Calidad y personas

- ¿Apartas el lote roto o lo cargas “en verde”?
- ¿Sabes de dónde salió esta cifra (linaje)?
- ¿Hay valores imposibles (`noches = -1`)?
- ¿El DNI se enmascara o **no entra**?
- ¿Quién ve el campo, y en qué estado (bruto, limpio, agregado)?

!!! example "Tres supuestos del grupo hotelero"
    1. “A las 02:00, la tabla de reservas → el lago.” → lote *pull*, no una cola.  
    2. “El semáforo de habitación libre en recepción, en pocos segundos.” → flujo + cola.  
    3. “Reservas web ya cobradas → fichero para ver en clase.” → [Hola ETL](#hola-etl). El informe agregado por hotel y canal es el [taller 2 de Pentaho](pentaho.md).

!!! success "Criterio b) en un examen"
    Origen + push/pull/poll + reloj + ETL o ELT + destino + formato de la carga + **por qué no** el de al lado. Un nombre de producto solo no puntúa.

## Referencias

- El mismo criterio, con otro hilo (productos y fabricantes) y otro taller pandas/DuckDB, está en los apuntes de Aitor Medrano: [Ingesta de datos. Pipeline y ETL](https://aitor-medrano.github.io/iabd/de/etl.html). Aquí el caso es el grupo hotelero; allí, el catálogo. Las letras E–T–L no cambian.
- [DuckDB](https://duckdb.org/) · [pandas](https://pandas.pydata.org/) · [Apache Kafka](https://kafka.apache.org/) · [Apache NiFi](https://nifi.apache.org/) · [Apache Airflow](https://airflow.apache.org/)
- [Pentaho Data Integration](https://www.hitachivantara.com/en-us/products/pentaho-plus-platform.html) (código: [pentaho-kettle](https://github.com/pentaho/pentaho-kettle))

## Actividades

No sustituye a Moodle. Comprueba que lo sostienes en voz alta.

1. Gerencia quiere el panel de las 8. ¿Qué decides **primero**: la herramienta o la pregunta de negocio? Di las tres marchas atrás (destino → transformación → origen).
2. Una cola solo guarda altas de reserva, sin limpiar ni cruzar. ¿Es un pipeline? ¿Es una ETL? ¿Por qué?
3. El almacén de finanzas **no** admite filas sucias. El lago de ocupación **sí** guarda el bruto. ¿ETL, ELT o los dos? ¿Dónde duele si cambian el indicador?
4. Con `reservas.csv` y `cobros.csv`: importe **cobrado** por hotel **solo** en canal `recepcion` (pandas y DuckDB). Cuenta también cuántas reservas de ese canal **aún no** tienen cobro (pista: un *left join* o un anti-join; el Hola ETL usaba *inner*).
5. Misma transformación del punto 4, **tres cargas**: JSON (verlo), Parquet (lago) y CSV. Anota tamaños y di cuándo usarías cada una. Recuerda: el JSON de pandas (array) no es el JSONL de DuckDB.
6. Dos procedimientos en el mismo hotel: (a) sensores cada 30 s para el semáforo de recepción; (b) cierre de cobros a las 23:00 para finanzas. Para cada uno: quién inicia, reloj, ETL/ELT, destino y formato. No mezcles los dos en un solo job.
7. El programa de reservas añade `motivo_cancelacion`. El job de las 02:00 sigue en verde. ¿Qué falló? ¿ETL o ELT te salva mejor un indicador nuevo de cancelaciones?
8. Misma transformación del punto 4, pero ahora **agrega**: por hotel, número de reservas cobradas y suma de `cobrado`. pandas y DuckDB. El resultado, un CSV. ¿Esa agregación la harías al recoger o al procesar? ¿Por qué?
9. La cadena lanza una app de fidelización y quiere reacción en redes las primeras 48 h. Del apartado [Consideraciones](#consideraciones), responde **al menos tres preguntas** de [Origen y formato](#origen-y-formato), **tres** de [Reloj / latencia](#reloj-latencia) y **tres** de [Calidad y personas](#calidad-y-personas). Nombra la **familia** de ingesta, no hace falta un producto.
