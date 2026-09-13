---
title: 2.2 Ecosistema Hadoop
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.2. Ecosistema Hadoop

[Apache Hadoop](https://hadoop.apache.org/) no es “un programa”. Es un **proyecto** (núcleo + piezas) para guardar y procesar datos en un [clúster](../ut1/clusters.md) de máquinas normales (*commodity*: servidores x86, no un mainframe). El criterio **e)** se ve aquí: **añades un módulo** (Hive, Spark, un *datanode*) y el sistema **crece** sin reescribir el hotel.

Hoy se trabaja sobre Hadoop **3.x**. Aún veréis jobs escritos para la 2.

## Cuatro piezas del núcleo

| Pieza | Oficio |
| --- | --- |
| **Hadoop Common** | Utilidades compartidas |
| **[HDFS](hdfs.md)** | Sistema de **ficheros** repartido |
| **YARN** | **Reparte CPU y RAM** entre jobs (*Yet Another Resource Negotiator*) |
| **MapReduce** | Modelo de programación: **mapear** y **reducir** (detalle en [2.4](computacion-distribuida.md)) |

Para el científico de datos, el clúster **parece** una carpeta enorme. Por debajo hay miles de discos.

Hadoop se diseña para:

- **Confianza:** varias copias del dato; si un nodo muere, se relanza la tarea.
- **Fallos como norma:** el hardware *commodity* se rompe; el software lo espera (criterio **c)**).
- **Escala horizontal:** de 1 a miles de máquinas, cada una con **disco y CPU locales**.
- **Portabilidad:** Linux de aula, cloud (EMR, HDInsight, Dataproc…).

!!! example "Llevar el cálculo al dato"
    No arrastras 8 TB de reservas al programa. El programa **viaja** al nodo que ya tiene el bloque. Eso es *data-local computing* y es la razón de que el almacén y el cómputo **convivan**.

## Quién es quién en el armario

| Rol | Qué hace | Hardware (orden de magnitud, no hay que memorizar GB) |
| --- | --- | --- |
| **Maestro** | Coordina (NameNode, ResourceManager…) | Más RAM y CPU; menos “montaña” de discos |
| **Worker** | Guarda bloques y ejecuta tareas | Muchos discos (a menudo **sin RAID**, *JBOD*), CPU razonable |
| **Edge / borde** | Puente con el exterior (clientes, Hue, SSH) | Interfaz; no es el almacén masivo |

*Commodity* **no** es el PC de casa: es hardware **no especializado**, barato de reponer. Cada *worker* nuevo suma **capacidad y rendimiento** (criterio **e)**).

## Módulos que se enchufan (el ecosistema)

El RA2 habla del **amplio ecosistema**. No certificáis todos. Sí sabéis **para qué** se cita cada uno.

| Módulo | Para qué lo citarías |
| --- | --- |
| **Hive** | SQL (*HiveQL*) sobre ficheros de HDFS |
| **HBase** | NoSQL **columnar** encima de HDFS (tablas enormes) |
| **Pig** | Lenguaje *Pig Latin* que acaba en MapReduce |
| **Sqoop** | Puente **SQL ↔ HDFS** (ya en [ingesta](../ut1/ingesta.md)) |
| **Flume** | Logs y flujos hacia HDFS |
| **ZooKeeper** | Coordinación (quién es el líder, configuración) |
| **Spark** | Cómputo **en memoria**; más rápido que MapReduce en jobs iterativos (IA). Puede vivir **sin** Hadoop |
| **Ambari** | Instalar y vigilar el clúster |

Distribuciones “ya montadas”: **Cloudera**, **Amazon EMR**, **Azure HDInsight**, **Google Dataproc**. En aula: la VM o el laboratorio que diga el profesor.

El criterio **e)** en una frase: *el núcleo no cambia; añades Hive cuando quieres SQL, Spark cuando el job itera, un datanode cuando no cabe el año*.

!!! warning "Montar el clúster a mano"
    Es posible y pedagógico. En empresa suele ganar el **cloud** o una distribución. MapReduce **duele** en algoritmos que dan muchas vueltas (entrenamiento). Ahí entra Spark; lo veréis más adelante. Aquí basta el modelo y YARN.

## Relación con el RA2

- **a)** Hadoop existe para **depositar y procesar** volumen en el mismo sitio.
- **e)** El “ecosistema” **es** la forma de crecer por módulos.
- **b)** El poder de procesamiento lo compruebas cuando un job MapReduce/YARN parte el fichero de reservas (apartado siguiente + [2.4](computacion-distribuida.md)).
