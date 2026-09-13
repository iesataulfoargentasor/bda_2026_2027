---
title: Tarea para practicar en clase
tags:
  - Big Data
  - BDA
  - RA1
  - RA2
---

# Tarea para practicar en clase

Antes de abrir Spark o Dask, hay que **saber qué tipo de ejecución** estás pidiendo y **por qué el portátil no es un clúster**. Esta sesión une lo de [1.2 Clústeres](clusters.md) y [1.4 Procesamiento](procesamiento.md) con los criterios del **RA2** (almacenamiento masivo, cómputo distribuido, tolerancia a fallos, crecer añadiendo recursos).

No se entrega en Moodle salvo que el profesor lo indique. Se trabaja **en clase** (individual o por parejas) y se comenta al final.

## Parte 0. Concurrente, paralela y distribuida

Tres palabras que en el pasillo se usan como sinónimos. No lo son. Si las mezclas, luego no sabrás si te basta el i7 del portátil o hace falta un clúster.

| Tipo | Dónde se ejecuta | ¿Al mismo tiempo de verdad? | Ejemplo mental |
| --- | --- | --- | --- |
| **Paralela** | Varios **núcleos** de **una** máquina | Sí: varios fogones a la vez | Varios cocineros en **la misma** cocina |
| **Distribuida** | **Varias máquinas** en red | Sí, en general (más red y fallos) | Varios **restaurantes** coordinados |
| **Concurrente** | Una o varias máquinas | **No necesariamente** | Un cocinero que **cambia rápido** de sartén |

- **Concurrente:** el sistema *entremezcla* tareas. Con un solo núcleo es el cambio de contexto de [1.4](procesamiento.md): parece simultáneo, el silicio se turna.
- **Paralela:** dos núcleos (o más) trabajan **a la vez** sobre trozos independientes. En el portátil: 10 núcleos / 20 hilos.
- **Distribuida:** el dato y el cálculo **no caben o no deben** vivir en un solo chasis. Aparecen red, réplicas y nodos que se caen.

!!! tip "Para la tarea de los 500 GB"
    Leer el fichero **por trozos en un solo proceso** es secuencial (a veces concurrente con la red).  
    Repartir trozos entre los 10 núcleos es **paralelo local**.  
    Mandar el job a Hadoop/Spark/Databricks es **distribuido**.  
    Las tres pueden aparecer en la misma recomendación a la empresa; no elijas “la palabra más moderna”.

### Herramientas Python que verás (no hace falta instalarlas hoy)

| | **Ray** | **Dask** | **PySpark** |
| --- | --- | --- | --- |
| Enfoque | Cómputo distribuido genérico, ML, RL | Paralelo y distribuido “estilo Pandas” | Big Data y análisis en el ecosistema Spark |
| Escala | Del portátil al clúster, muy flexible | Del portátil al clúster | Clústeres grandes |
| Facilidad | API relativamente sencilla; muy usada en ML | Cómoda si vienes de Pandas/NumPy | Más curva: hay que pensar en Spark |
| Encaja con | TensorFlow, PyTorch | Pandas, scikit-learn | Hadoop, Hive, Spark |
| Tolerancia a fallos | Alta (modelo de actores) | Alta | Muy alta (RDD/DataFrame resilientes) |
| Ideal para | ML distribuido, simulaciones | ETL, análisis, pipelines de ML | Volumen masivo “de libro” |
| Pega | Menos “clásico” que Spark en Big Data de empresa | No siempre es lo más eficiente al *muy* gran escala | Infraestructura más pesada |

Para profundizar (cuando el profesor lo indique):

- Tutorial Berkeley (Dask, *future* en R y un poco de Ray): [Flexible parallel processing](https://computing.stat.berkeley.edu/tutorial-dask-future/)
- Plan ETL con **Ray** (Colab): [cuaderno](https://colab.research.google.com/drive/1Hfk8uMndNU6bQIVBNVXsPjiJMlu7xdju?usp=sharing)
- Plan ETL con **Dask** (Colab): [cuaderno](https://colab.research.google.com/drive/1hFZ2G6I6pfz5RSv8OKt28QOJ5v7xfVGb?usp=sharing)
- Estudio del profesor: 500 GB con Dask (Colab): [cuaderno](https://colab.research.google.com/drive/1DWyILxlyHpWqjcC9EItymv30OESSmaCE?usp=sharing)
- Demo en GitHub (Dask, origen remoto → S3, desde un portátil): [josedavidmi/demo_dask_500gb-](https://github.com/josedavidmi/demo_dask_500gb-)

## El caso: 500 GB y solo un portátil

Eres técnico de datos. Te piden **procesar un fichero de 500 GB** (JSON, CSV o log) que está:

- en un **repositorio interno** (URL de la empresa), o
- en una **carpeta compartida** de la red corporativa.

El fichero viene de una **exportación de base de datos** o de **logs de una tienda online**.

**Operación** (elige **una**): media, desviación típica, o normalizar un campo numérico.

**Destino del resultado** (elige **uno**): *bucket* **S3**, **MongoDB Atlas**, o **Azure** (Blob / Data Lake). El resultado de una media ocupa **casi nada**; no lo confundas con copiar los 500 GB.

**Tu única máquina (el portátil):**

| Recurso | Dato | Qué implica |
| --- | --- | --- |
| Disco | 1 TB, **70 % ocupado** → ~**300 GB libres** | 500 GB **no caben** enteros |
| RAM | **32 GB** | Un `read_csv` / DataFrame de 500 GB **no cabe** |
| CPU | i7, **10 núcleos / 20 hilos** | Hay paralelismo *local*, no un clúster |
| GPU | RTX 4060, 6 GB | ¿Ayuda a *esta* media o no? |

## Qué tienes que entregar (en clase)

Responde por escrito (o en un pad compartido) a **todas** las preguntas. No hace falta código que compile; sí un razonamiento que se pueda defender en voz alta.

### 1. Limitaciones del portátil

Explica por qué **no** es buena idea:

1. Descargar los 500 GB al disco local, y
2. Cargar **todo** en memoria (por ejemplo, un DataFrame de Pandas).

Habla al menos de: **espacio en disco**, **RAM**, **E/S de disco** y **red** (bajar 500 GB por la wifi del aula no es “un rato”).

!!! example "Pista, no la respuesta"
    Libres ≈ 300 GB < 500 GB. Pandas quiere el dataset **entero** (y suele ocupar *más* RAM que el fichero en disco). Aunque el disco llegara, la RAM no. Y copiar 500 GB es un cuello de **red y disco**, no de la RTX.

### 2. Opción 1 — Local secuencial (por trozos)

¿Se puede calcular la media / desviación / normalización **sin** guardar el fichero entero ni cargarlo en RAM?

Describe, a alto nivel, un plan en Python:

- Lectura **línea a línea** o por **bloques** (*chunks*, *streaming*).
- Cálculo **incremental** (una pasada: vas actualizando suma y recuento; la media es `suma/n` al final).
- Escribes **solo** el resultado (unos bytes) hacia S3 / Atlas / Azure.

Relaciónalo con **concurrente / secuencial**: un solo proceso que lee y actualiza contadores.

### 3. Opción 2 — Local **paralela**

¿Cómo aprovechas los **10 núcleos / 20 hilos**?

Comenta una vía: Spark **en modo local**, **Dask**, `multiprocessing`…

Qué **mejora** respecto a la opción 1 (varios trozos a la vez) y qué **sigue igual** (el disco no ha crecido, la red sigue siendo tuya, si se apaga el portátil el job muere).

### 4. Opción 3 — Distribuido / nube

La empresa tiene o puede contratar un clúster Hadoop/Spark (propio o en nube) o un servicio gestionado (Databricks, EMR, Synapse, BigQuery…).

Explica, en general:

1. **Dónde** dejas el fichero (HDFS, S3, Blob, Data Lake…) — “llevar el cálculo al dato”, no el dato al portátil.
2. **Cómo** lanzas el cálculo (job Spark, SQL sobre el almacén…).
3. Por qué encaja: **volumen**, **tiempo**, **tolerancia a fallos**, **crecimiento** (añadir nodos = [escalado horizontal](clusters.md)).

### 5. Opción 4 — Cargar y consultar

Valora cargar el fichero (o **particionarlo**) en MongoDB Atlas o en un warehouse / *lakehouse* (Athena, BigQuery, Snowflake…) y hacer la media con una **consulta**.

¿Cuándo tiene sentido frente a Spark/Hadoop? Ventajas e inconvenientes: **modelo de datos**, **coste** (¡dato escaneado!), **curva de aprendizaje**.

### 6. ¿Y la GPU?

¿La RTX 4060 **cambia de verdad** este problema (una estadística sobre un campo de un log/CSV)?

Di en qué tareas de datos **sí** suele ayudar (entrenar un modelo, álgebra pesada) y por qué aquí el cuello puede ser **leer bytes de red/disco**, no multiplicar matrices.

### 7. Elección final

Recomienda **una opción o una combinación** a la empresa.

Justifícala con los criterios del **RA2**:

| Criterio RA2 (idea) | Cómo se nota en tu respuesta |
| --- | --- |
| Importancia del **almacenamiento** | ¿Dónde vive el fichero? ¿Por qué no en el portátil? |
| Modelo de **computación distribuida** | ¿Quién ejecuta el cálculo? |
| **Tolerancia a fallos** | ¿Qué pasa si se cuelga una máquina a mitad? |
| Guardar **mucho** y decidir después | ¿El bruto sigue accesible o lo tiraste? |
| **Crecer** añadiendo recursos | ¿Mañana son 5 TB? ¿Escala en vertical o en horizontal? |

## Cómo lo hacemos en el aula

1. 10 minutos: lee la Parte 0 y el enunciado. Aclara dudas de vocabulario.
2. 25–35 minutos: responde 1–7 (parejas bienvenidas).
3. 10 minutos: puesta en común. El profesor puede contrastar con el [cuaderno Dask de 500 GB](https://colab.research.google.com/drive/1DWyILxlyHpWqjcC9EItymv30OESSmaCE?usp=sharing) o la [demo de GitHub](https://github.com/josedavidmi/demo_dask_500gb-).

!!! success "Qué se espera"
    No un clúster montado hoy. Sí una recomendación **argumentada**: qué no hacer con el portátil, qué aporta lo paralelo local, cuándo pasar a distribuido y dónde acaba el resultado (S3, Atlas o Azure).

## Relación con el módulo

Es una **actividad inicial del RA2** (almacenamiento masivo y cómputo distribuido), colocada al final de la UT1 porque ya tienes el vocabulario de [1.2](clusters.md) y [1.4](procesamiento.md). No abre temas que no hayáis visto: solo te obliga a **elegir y justificar**.

La entrega formal, si la hay, se indica en Moodle.
