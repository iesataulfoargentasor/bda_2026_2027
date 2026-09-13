---
title: RA2 y criterios de evaluación
tags:
  - BDA
  - RA2
---

# Resultado de aprendizaje 2 (RA2)

Esta unidad desarrolla el **RA2** del módulo *Big Data aplicado* (código **5075**), según el Real Decreto 279/2021.

## Enunciado

**RA 2:** Gestiona sistemas de almacenamiento y el amplio ecosistema alrededor de ellos, facilitando el procesamiento de grandes cantidades de datos, sin fallos y de forma rápida.

## Criterios de evaluación

| CE | Criterio (texto oficial) | Dónde se trabaja en la UT2 |
| --- | --- | --- |
| **a)** | Se ha determinado la importancia de los sistemas de almacenamiento para depositar y procesar grandes cantidades de cualquier tipo de datos rápidamente. | [2.1](por-que-almacenamiento.md), [2.2](ecosistema.md), [2.3](hdfs.md), [2.5](nosql.md) |
| **b)** | Se ha comprobado el poder de procesamiento de su modelo de computación distribuida. | [2.4 Computación distribuida](computacion-distribuida.md) (MapReduce, YARN) |
| **c)** | Se ha probado la tolerancia a fallos de los sistemas. | [2.3 HDFS](hdfs.md) (réplica de bloques) y [2.8 Réplicas y shards](replicas-shards.md) |
| **d)** | Se ha determinado que se pueden almacenar tantos datos como se desee y decidir cómo utilizarlos más tarde. | [2.3](hdfs.md) (WORM, esquema al leer) y [2.7 Modelado](modelado.md) |
| **e)** | Se ha visualizado que el sistema puede crecer fácilmente añadiendo módulos. | [2.2](ecosistema.md) (piezas Hadoop), [2.3](hdfs.md) (más *datanodes*), [2.8](replicas-shards.md) (más *shards*) |

## Qué cambia respecto a la UT1

En la [UT1](../ut1/ra1.md) **diseñabas** la solución (dónde guardar, cómo ingerir, en qué formato, cómo presentar). Aquí **gestionas el sistema** que aguanta el volumen: el clúster de ficheros, el modelo *map* / *reduce*, las familias NoSQL y cómo se **replican** y **parten**.

La [tarea de los 500 GB](../ut1/tarea-clase.md) era el puente: un portátil no basta; hace falta un almacén que crezca **añadiendo máquinas**.

!!! note "Cómo se evalúa"
    Debes poder **decir** por qué HDFS o Mongo, **mostrar** (en el lab) que un nodo caído no pierde el dato, **lanzar** un job que parte el trabajo y **justificar** que mañana se añade un disco o un *shard* sin rediseñar el hotel. Las entregas siguen en Moodle.

    Para practicar: [autoevaluación de la UT2](autoevaluacion.md).
