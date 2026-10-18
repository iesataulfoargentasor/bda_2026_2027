---
title: "Transición a la UT2: 500 GB y un portátil"
tags:
  - Big Data
  - BDA
  - RA1
  - RA2
---

# Transición a la UT2: 500 GB y un portátil

Después de completar la [práctica integradora con Pentaho](tarea-clase.md), planteamos una nueva situación: el histórico crece y debemos revisar si los recursos y el procedimiento siguen cumpliendo el plazo. Esta actividad es de razonamiento; no requiere descargar 500 GB ni construir un clúster.

Esta sesión une [1.2 Clústeres](clusters.md){target="_blank" rel="noopener"} y [1.4 Procesamiento](procesamiento.md){target="_blank" rel="noopener"} con el **RA2**: guardar mucho, calcular en varias máquinas, aguantar que una se caiga y crecer **añadiendo** recursos. Hoy **no** instaláis Spark ni Dask. Sí tenéis que saber **qué tipo de ejecución** estáis pidiendo y **por qué el portátil no es un clúster**.

No se entrega en Moodle salvo que el profesor lo indique. Se trabaja **en clase** (individual o por parejas) y se comenta al final.

!!! info "Cómo se lee esta página"
    Primero el **caso** (500 GB del [grupo hotelero](caso-hotel.md){target="_blank" rel="noopener"}, un portátil). Luego un **repaso** de concurrente / paralelo / distribuido (ya lo visteis en el 1.4). Después **siete preguntas**. El resultado tiene que servir para el **panel de las 8** (cierre de **ayer**).

## Vídeo: del informe del hotel a los 500 GB

Esta guía continúa la historia de la práctica de Pentaho: el histórico crece y debemos comparar cómo procesarlo dentro del plazo. Explica los límites del portátil, la lectura por bloques, el paralelismo local, la distribución y las preguntas que debéis responder para justificar vuestra propuesta. **Duración: 10 minutos y 55 segundos.**

<video controls playsinline preload="metadata" poster="../../assets/ut1/transicion-500gb-portada.jpg" aria-label="Transición a la UT2: cómo abordar la tarea de los 500 GB" style="width: 100%; max-width: 960px; height: auto; border-radius: 12px;">
  <source src="../../assets/ut1/transicion-500gb.mp4" type="video/mp4">
  Tu navegador no permite reproducir este vídeo. Puedes descargarlo en el enlace siguiente.
</video>

El vídeo incluye subtítulos visibles y narración con voz sintética en español. Complementa el enunciado: la actividad pide una propuesta razonada, sin descargar 500 GB ni instalar un clúster.

[Descargar el vídeo](../assets/ut1/transicion-500gb.mp4) · [Leer la transcripción](../assets/ut1/transicion-500gb.txt) · [Descargar los subtítulos](../assets/ut1/transicion-500gb.es.srt)

## El caso: 500 GB y un portátil

Sois técnicos de la cadena. Debéis procesar un histórico de **500 GB** (CSV, JSON o logs de reservas y cobros) de Santander, Laredo, Comillas y Potes. Elegid la operación indicada por el profesor: una media produce un resumen pequeño; normalizar un campo a escala 0–1 produce un conjunto de datos transformado que puede seguir siendo grande. El informe de las 8 utilizará el resultado del cierre acordado. No se modifica el PMS.

El fichero está en la **red de la empresa** (una URL interna o una carpeta compartida), no en vuestro disco.

**Operación** (elegid **una**): media, desviación típica, o *normalizar* un campo (dejarlo en una escala comparable, p. ej. 0–1).

**Destino del resultado** (elegid **uno**, el que diga el profesor): cubo **S3**, **Azure** (Blob / Data Lake) o **carpeta del aula**. Si ya usáis MongoDB Atlas, vale. El resultado de una media ocupa **casi nada**; no lo confundáis con mover los 500 GB.

**Vuestra única máquina (el portátil):**

| Recurso | Dato | Qué implica |
| --- | --- | --- |
| Disco | 1 TB, **70 % ocupado** → ~**300 GB libres** | 500 GB **no caben** enteros |
| RAM | **32 GB** | Un `read_csv` / DataFrame de 500 GB **no cabe** |
| CPU | CPU hipotética, **10 núcleos / 20 hilos** | Hay paralelismo *local*, no un clúster |
| GPU | GPU hipotética de 6 GB | ¿Ayuda a *esta* media o no? |

```mermaid
flowchart TD
 H[Histórico: 500 GB] --> B[Lectura por bloques desde el origen]
 B --> M[Media: acumular suma y recuento]
 B --> N[Normalización: calcular límites y transformar filas]
 M --> S[Resumen pequeño]
 N --> D[Dataset transformado: puede seguir siendo grande]
 S --> V[Validar y guardar en destino acordado]
 D --> V
 H --> R[Medir red, disco, RAM y tiempo antes de elegir recursos]
```

No cabe una copia completa en 300 GB libres ni un DataFrame completo en 32 GB de RAM. Leer remotamente por bloques sí puede ser viable, si cumple el plazo.

## Concurrente, paralelo y distribuido (repaso)

Tres palabras que en el pasillo se usan como sinónimos. **No** lo son. El detalle está en el [1.4](procesamiento.md){target="_blank" rel="noopener"}; aquí basta para no mezclar el i7 con un clúster.

```mermaid
flowchart TD
 T[Organización del cálculo] --> U[Una máquina]
 T --> V[Varias máquinas que se comunican: distribuido]
 U --> S[Un recurso alterna tareas: concurrencia sin paralelismo]
 U --> P[Varios recursos a la vez: paralelo local]
 V --> D[Nodos calculando a la vez: distribuido y paralelo]
 V --> E[Nodos esperando dependencias: sin paralelismo en esa fase]
```

Son dos preguntas distintas: dónde se ejecuta y si hay simultaneidad. La concurrencia permite que varias tareas progresen durante un intervalo.

| Tipo | Dónde corre | En esta tarea |
| --- | --- | --- |
| **Secuencial por bloques** | Un proceso actualiza el cálculo bloque a bloque | Leéis el fichero **por trozos** y actualizáis suma y recuento |
| **Paralelo local** | Varios **núcleos** de **una** máquina | Los **10 núcleos** del portátil; si se apaga, muere el job |
| **Distribuido** | **Varias máquinas** en red | El cálculo va **al dato**; réplicas si se funde un disco; acabar **antes de las 8** |

**Spark en modo local sigue siendo el portátil:** varios núcleos, **una** máquina. No lo presentéis como la opción 3.

```mermaid
flowchart TD
 O[Operación y plazo acordados] --> S[Local secuencial: bloques sucesivos]
 O --> P[Local paralelo: varios recursos del portátil]
 O --> D[Distribuido: varios nodos conectados]
 S --> M[Medir tiempo, memoria, red y recuperación]
 P --> M
 D --> M
 M --> E[Elegir la alternativa suficiente y justificar costes]
```

Las tres opciones se comparan con la misma operación y plazo. Distribuido también puede ser paralelo; Spark en modo local sigue usando una sola máquina.

!!! tip "Las tres pueden convivir"
    Comparad alternativas con medidas: explorar una muestra, leer el histórico remoto por bloques o repartir el cálculo. El procesamiento local completo puede ser viable si cumple el plazo y los recursos; distribuido requiere justificar su coste y coordinación. Evitar una copia local completa no evita transferir bytes cuando se lee por red.

## Qué tenéis que entregar (en clase)

Responded por escrito (o en un pad) a **todas** las preguntas. No hace falta código que compile; sí un razonamiento que se pueda defender en voz alta.

### 1. Limitaciones del portátil

Explicad por qué **no** es buena idea:

1. Descargar los 500 GB al disco local, y
2. Cargar **todo** en memoria (por ejemplo, un DataFrame de Pandas).

Hablad al menos de: **espacio en disco**, **RAM**, **entrada/salida de disco** (leer y escribir es lento) y **red** (bajar 500 GB por la wifi del aula no es “un rato”).

!!! example "Pista, no la respuesta"
    Libres ≈ 300 GB < 500 GB. Una lectura completa con pandas intenta crear todo el DataFrame, que puede ocupar más RAM que el fichero. La lectura por bloques permite otro planteamiento. Aunque el disco llegara, la RAM no. Y copiar 500 GB es un cuello de **red y disco**, no de la GPU.

### 2. Opción 1 — Local secuencial (por trozos)

La lectura por bloques evita mantener todo el archivo en memoria. El tamaño del bloque debe dejar espacio para los datos convertidos y las operaciones intermedias. Si el archivo está en red, sigue siendo necesario transferir sus bytes al proceso lector, aunque no se guarden permanentemente en el disco local.

Para la **media**, basta mantener suma y recuento de valores válidos. Para la **desviación típica**, se necesita un algoritmo incremental estable y aclarar si se calcula la desviación poblacional o muestral. Para **normalizar cada valor a 0–1**, normalmente se necesitan dos pasadas: una para obtener mínimo y máximo y otra para transformar. Si máximo y mínimo coinciden, debe definirse cómo tratar ese caso.

La normalización de cada registro produce una salida del tamaño del conjunto transformado, no un único número. Si se pide solo mínimo y máximo, la salida sí es pequeña. Indicad expresamente cuál de los dos resultados vais a entregar.

¿Se puede calcular la media / desviación / normalización **sin** guardar el fichero entero ni cargarlo en RAM?

Describid, a alto nivel, un plan en Python:

- Lectura **línea a línea** o por **bloques** (*chunks*: trozos que caben en RAM).
- Cálculo **incremental** (una pasada: vais actualizando suma y recuento; la media es `suma/n` al final).
- Escribís la estadística resumida o el conjunto normalizado, según la operación elegida. Estimad también el tamaño de esa salida.

Relacionadlo con **secuencial**: un solo proceso que lee y actualiza contadores.

### 3. Opción 2 — Local **paralela**

El plan debe limitar cuántos bloques están en memoria simultáneamente. Diez procesos con bloques grandes pueden agotar los 32 GB aunque cada bloque, por separado, quepa. Además, varias lecturas pueden competir por la misma conexión de red. Comparad la tasa de lectura antes y después de aumentar trabajadores.

¿Cómo aprovecháis los **10 núcleos / 20 hilos**?

Comentad una vía: Spark **en modo local**, **Dask** o `multiprocessing`. Hoy no hace falta instalarlas: el oficio es el diseño.

Qué **mejora** respecto a la opción 1 (varios trozos a la vez) y qué **sigue igual** (el disco no ha crecido, la red sigue siendo vuestra, si se apaga el portátil el job muere). Si el panel dependiera de ese portátil, habría que justificar disponibilidad, recuperación y plazo; una máquina de alumno no ofrece esas garantías por el mero hecho de ejecutar el cálculo.

### 4. Opción 3 — Distribuido

Explicad cómo se combinan los resultados parciales. Para una media, cada trabajador devuelve suma y recuento y el coordinador divide las sumas globales. Guardar solo medias locales pierde la ponderación por tamaño.

El diseño también debe indicar dónde se ejecuta cada tarea, cómo se identifica una partición terminada y qué ocurre si se repite. Tener varios nodos no garantiza tolerancia a fallos si la única copia del origen o el coordinador sigue siendo un punto único de fallo.

La empresa puede usar un clúster (Hadoop/Spark, propio o en nube) o el servicio que indique el profesor.

Explicad, en general:

1. **Dónde** dejáis el fichero (HDFS, S3, Blob…) — “llevar el cálculo al dato”, no el dato al portátil.
2. **Cómo** lanzáis el cálculo (un *job*: trabajo programado; de madrugada, para tener el número **antes de las 8**).
3. Por qué encaja: **volumen**, **tiempo**, **tolerancia a fallos** (si se dispone de réplicas y recuperación probada, puede continuarse ante ciertos fallos: [1.2](clusters.md){target="_blank" rel="noopener"}), **crecimiento** (añadir nodos = [escalado horizontal](clusters.md){target="_blank" rel="noopener"}).

### 5. Opción 4 — Cargar y consultar

Valorad cargar el fichero (o **particionarlo**) en un almacén de informes / *lakehouse* o, si el aula lo usa, MongoDB, y hacer la media con una **consulta**.

¿Cuándo tiene sentido frente a un job Spark? Ventajas e inconvenientes: **modelo de datos**, **coste** (¡a menudo pagáis por lo **escaneado**!, [1.7](formatos.md){target="_blank" rel="noopener"}), **curva de aprendizaje**.

### 6. ¿Y la GPU?

¿La GPU **cambia de verdad** este problema (una estadística sobre un campo de un CSV/JSON de reservas)?

Decid en qué tareas de datos **sí** suele ayudar (entrenar un modelo, álgebra pesada) y por qué aquí el cuello puede ser **leer bytes de red/disco**, no multiplicar matrices.

### 7. Elección final

Presentad una recomendación con supuestos verificables: formato y ubicación del origen, ancho de banda disponible, plazo, frecuencia de repetición y tamaño de la salida. Una media puntual puede justificar un plan distinto de un informe que debe regenerarse cada mañana.

Incluid una estimación mínima de lectura: `tiempo = bytes / bytes por segundo`. A 100 MB/s sostenidos, leer 500 GB decimales exige al menos 5.000 segundos —unos 83 minutos—, sin contar interpretación ni cálculo. La cifra no predice el tiempo real; sirve para descartar promesas incompatibles con el límite de entrada/salida.

Recomendad **una opción o una combinación** a gerencia.

Justificadla con los criterios del **RA2**:

| Criterio RA2 (idea) | Cómo se nota en vuestra respuesta |
| --- | --- |
| Importancia del **almacenamiento** | ¿Dónde vive el fichero? ¿Por qué no en el portátil? |
| Modelo de **computación distribuida** | ¿Quién ejecuta el cálculo? ¿Acaba antes de las 8? |
| **Tolerancia a fallos** | ¿Qué pasa si se cuelga una máquina a mitad? |
| Guardar **mucho** y decidir después | ¿El bruto sigue accesible o lo tirasteis? |
| **Crecer** añadiendo recursos | ¿Mañana son 5 TB? ¿Una máquina más gorda o más nodos? |

## Cómo lo hacemos en el aula

1. 10 minutos: leed el caso y el repaso. Aclarad dudas de vocabulario.
2. 25–35 minutos: responded 1–7 (parejas bienvenidas).
3. 10 minutos: puesta en común. El profesor puede contrastar con el [cuaderno Dask de 500 GB](https://colab.research.google.com/drive/1DWyILxlyHpWqjcC9EItymv30OESSmaCE?usp=sharing){target="_blank" rel="noopener"} o la [demo de GitHub](https://github.com/josedavidmi/demo_dask_500gb-){target="_blank" rel="noopener"}.

!!! success "Qué se espera"
    No un clúster montado hoy. Sí una recomendación **argumentada**: qué no hacer con el portátil, qué aporta lo paralelo local, cuándo pasar a distribuido (job de madrugada, panel de las 8) y dónde acaba el **resultado** y cuánto ocupa.

## Relación con el módulo

Es el **puente hacia el RA2** (almacenamiento masivo y cómputo distribuido), colocada al final de la UT1 porque ya tenéis el vocabulario de [1.2](clusters.md){target="_blank" rel="noopener"} y [1.4](procesamiento.md){target="_blank" rel="noopener"}. Os obliga a **elegir y justificar**. El laboratorio de HDFS y Spark es la UT2.

La entrega formal, si la hay, se indica en Moodle.

## Para profundizar (si el profesor lo indica)

No es de esta sesión. Si os piden probar código, Dask se parece a Pandas; PySpark es el de libro en clústeres grandes; Ray aparece más en ML. Hoy no hace falta instalarlas.

| | **Dask** | **PySpark** | **Ray** |
| --- | --- | --- | --- |
| Encaje | Paralelo y distribuido “estilo Pandas” | Volumen masivo en el ecosistema Spark | Cómputo distribuido genérico |
| Hoy | Solo si el profesor abre el cuaderno | No lo programáis aún ([1.4](procesamiento.md){target="_blank" rel="noopener"}) | Fuera de esta tarea |

- Tutorial Berkeley (Dask y un poco de Ray): [Flexible parallel processing](https://computing.stat.berkeley.edu/tutorial-dask-future/){target="_blank" rel="noopener"}
- Plan ETL con **Dask** (Colab): [cuaderno](https://colab.research.google.com/drive/1hFZ2G6I6pfz5RSv8OKt28QOJ5v7xfVGb?usp=sharing){target="_blank" rel="noopener"}
- Plan ETL con **Ray** (Colab): [cuaderno](https://colab.research.google.com/drive/1Hfk8uMndNU6bQIVBNVXsPjiJMlu7xdju?usp=sharing){target="_blank" rel="noopener"}
- Estudio del profesor: 500 GB con Dask (Colab): [cuaderno](https://colab.research.google.com/drive/1DWyILxlyHpWqjcC9EItymv30OESSmaCE?usp=sharing){target="_blank" rel="noopener"}
- Demo en GitHub (Dask, origen remoto → S3, desde un portátil): [josedavidmi/demo_dask_500gb-](https://github.com/josedavidmi/demo_dask_500gb-){target="_blank" rel="noopener"}
