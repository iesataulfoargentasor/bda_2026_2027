---
title: "U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema"
tags:
  - Big Data
  - BDA
  - RA2
---

# U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema

El título sigue el **[RA2](ra2.md)**: *gestiona sistemas de almacenamiento y el amplio ecosistema alrededor de ellos, facilitando el procesamiento de grandes cantidades de datos, sin fallos y de forma rápida*.

En la [UT1](../ut1/index.md) elegías almacén, ingesta y formato. Aquí el grupo hotelero **ya tiene** terabytes: logs de reservas, JSON de sensores, fotos de habitación y cobros. Una sola máquina no los deposita **ni** los procesa a tiempo. Hace falta un **sistema** (HDFS, YARN, Mongo…) y el **ecosistema** que lo rodea (Hive, Spark, réplicas, *shards*).

Lee los apartados **en orden**. El hilo es el mismo hotel de Cantabria. Las siglas (HDFS, YARN, BSON, *oplog*…) llegan **después** del ejemplo. Si puedes explicar a un compañero *qué ganas al añadir un nodo* y *qué pasa si se apaga uno*, el apartado está asimilado.

## Qué vas a trabajar

| Apartado | Criterio | Qué te llevas |
| --- | --- | --- |
| [2.1 Por qué un almacén masivo](por-que-almacenamiento.md) | **a)** | Depositar *cualquier* tipo y procesarlo *en el sitio* |
| [2.2 Ecosistema Hadoop](ecosistema.md) | **a)** / **b)** / **e)** | Núcleo, ecosistema, YARN, instalación, primer job y Streaming |
| [2.3 HDFS](hdfs.md) | **a)** / **c)** / **d)** / **e)** | Bloques, réplica, lectura/escritura, `fsck`, snapshots y Python |
| [2.4 Computación distribuida](computacion-distribuida.md) | **b)** | MapReduce y YARN: el poder de partir el trabajo |
| [2.5 Familias NoSQL](nosql.md) | **a)** / **c)** / **d)** / **e)** | Familias, esquema dinámico, *shards*, réplica, CAP y BASE |
| [2.6 MongoDB](mongodb.md) | **a)** / **d)** | Documento, consultas y actualizaciones |
| [2.7 Modelado documental](modelado.md) | **d)** | Embeber o referenciar; decidir el uso *después* |
| [2.8 Réplicas y particiones](replicas-shards.md) | **c)** / **e)** | Caídas, votos y crecer con *shards* |
| [2.9 MongoDB y Python](pymongo.md) | **b)** / **d)** | PyMongo sobre el mismo hotel |
| [Autoevaluación](autoevaluacion.md) | — | Preguntas de la unidad (no puntúa en Moodle) |

!!! info "Sobre el material"
    El temario se apoya en el ecosistema Hadoop/HDFS y en el bloque NoSQL/Mongo que se trabaja en el ciclo (instalación, *shell*, modelado, réplicas, PyMongo). El texto es de aula IES: otro caso, otros ficheros, mismos oficios. Las prácticas evaluables siguen en Moodle. En el laboratorio usad la máquina o el clúster que indique el profesor; no hace falta la VM de otro centro.
