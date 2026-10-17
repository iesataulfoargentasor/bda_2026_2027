---
title: "U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema"
tags:
  - Big Data
  - BDA
  - RA2
---

# U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema

El título sigue el **[RA2](ra2.md)**: *gestiona sistemas de almacenamiento y el amplio ecosistema alrededor de ellos, facilitando el procesamiento de grandes cantidades de datos, sin fallos y de forma rápida*.

En la [UT1](../ut1/index.md) elegías almacén, ingesta y formato. Aquí el grupo hotelero **ya tiene** terabytes: logs de reservas, JSON de sensores, fotos de habitación y cobros. En el escenario de la unidad, las mediciones muestran que la solución inicial no procesa el cierre dentro del plazo. Tener terabytes por sí solo no demuestra que una máquina sea insuficiente: hay que relacionar volumen, recursos y carga. Hace falta un **sistema** (HDFS, YARN, Mongo…) y el **ecosistema** que lo rodea (Hive, Spark, réplicas, *shards*).

Lee los apartados **en orden**. El hilo es el mismo **[grupo hotelero de Cantabria](../ut1/caso-hotel.md)**. Las siglas (HDFS, YARN, BSON, *oplog*…) llegan **después** del ejemplo. Si puedes explicar a un compañero *qué ganas al añadir un nodo* y *qué pasa si se apaga uno*, el apartado está asimilado.

## Qué vas a trabajar

| Apartado | Criterio | Qué te llevas |
| --- | --- | --- |
| [2.1 Por qué un almacén masivo](por-que-almacenamiento.md) | **a)** | Depositar *cualquier* tipo y procesarlo *en el sitio* |
| [2.2 Ecosistema Hadoop](ecosistema.md) | **a)** / **b)** / **e)** | Núcleo, ecosistema, YARN, instalación, primer job y Streaming |
| [2.3 HDFS](hdfs.md) | **a)** / **c)** / **d)** / **e)** | Bloques, réplica, lectura/escritura, `fsck`, snapshots y Python |
| [2.4 Computación distribuida](computacion-distribuida.md) | **b)** | MapReduce y YARN: el poder de partir el trabajo |
| [2.5 Familias NoSQL](nosql.md) | **a)** / **c)** / **d)** / **e)** | Familias, esquema dinámico, *shards*, réplica, CAP y BASE |
| [2.6 MongoDB](mongodb.md) | **a)** / **d)** | BSON, mongosh, consultas, cursores y updates |
| [2.7 Modelado documental](modelado.md) | **d)** | Carga, cardinalidad, patrones y validador (hotel) |
| [2.8 Réplicas y particiones](replicas-shards.md) | **c)** / **e)** | *Oplog*, votos, `hotelrs`, claves de partición y reparto por rangos o hash |
| [2.9 MongoDB y Python](pymongo.md) | **b)** / **d)** | PyMongo: cursores, agregados, cobros y un extra Flask |
| [Autoevaluación](autoevaluacion.md) | — | Preguntas de la unidad (no puntúa en Moodle) |

!!! info "Sobre el material"
    El temario se apoya en el ecosistema Hadoop/HDFS y en el bloque NoSQL/Mongo que se trabaja en el ciclo (instalación, *shell*, modelado, réplicas, PyMongo). El texto es de aula IES: otro caso, otros ficheros, mismos oficios. Las prácticas evaluables siguen en Moodle. En el laboratorio usad la máquina o el clúster que indique el profesor; no hace falta la VM de otro centro.

## Un recorrido con dos laboratorios

El primer bloque, **2.1–2.4**, sigue un fichero desde su almacenamiento en HDFS hasta un agregado MapReduce coordinado por YARN. El segundo, **2.5–2.9**, parte de las familias NoSQL, practica documentos en MongoDB y añade modelado, réplicas, particiones y acceso desde Python. Son dos formas de resolver necesidades del mismo hotel; no hace falta instalar MongoDB dentro de Hadoop.

| Laboratorio | Datos iniciales | Qué compruebas |
| --- | --- | --- |
| Hadoop | CSV de 20 reservas, 62 noches | Rutas, bloques, tareas y totales por hotel |
| MongoDB independiente | JSONL de 15 reservas y 6 opiniones | Filtros, arrays, cursores y agregados |
| `hotel_escrituras` | Copia de las colecciones anteriores | Altas, cambios y borrados sin alterar las consultas base |
| `hotelrs` | Documento de prueba identificado | Elección, lectura de secundarios y recuperación |
| Sharding, opcional | 15 reservas importadas en ese clúster | Distribución y movimiento sin perder resultados |
| `hotel_tx`, sobre replica set | Una plaza de parking | Confirmación conjunta o rechazo sin cambios parciales |

Los CSV y JSONL son **conjuntos diferentes**: no tienen por qué producir los mismos totales. Sigue el fichero indicado por cada práctica. Las instrucciones distinguen comandos del host, Bash del contenedor, shell MongoDB y Python.

## Qué preparar y qué entregar

Necesitas los fundamentos de UT1, manejo básico de terminal y Python. Para Docker, utiliza el entorno Linux del aula; consulta los requisitos concretos en 2.2 y 2.6. Antes de empezar, identifica qué servicios están encendidos: MongoDB independiente y el replica set utilizan el mismo puerto del host.

En cada práctica conserva **entrada, configuración, operación, resultado y explicación**. Una captura sin interpretación no permite saber si el resultado es correcto. Separa lo observado de lo esperado por diseño, especialmente si todo se ejecuta en un único ordenador. Termina con la [autoevaluación](autoevaluacion.md) y revisa los criterios del [RA2](ra2.md).
