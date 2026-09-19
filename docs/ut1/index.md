---
title: "U.T. 1. Gestión de soluciones de almacenamiento"
tags:
  - Big Data
  - BDA
  - RA1
---

# U.T. 1. Gestión de soluciones de almacenamiento

El título sigue el **[RA1](ra1.md)**: *gestiona soluciones a problemas propuestos, utilizando sistemas de almacenamiento y herramientas asociadas al centro de datos*. No es un tour genérico por “qué es Big Data”; es diseñar el almacén, ingerir, formatear, procesar y presentar.

Una empresa puede empezar con un servidor y una base de datos relacional. Cuando los clientes, los sensores o los logs crecen, ese servidor deja de bastar: no cabe el volumen, no llega a tiempo la velocidad y los datos ya no caben en tablas uniformes.

**Big Data** no es “muchos Excel”. Es un conjunto de **métodos y tecnologías** para capturar, almacenar, procesar y presentar datos que **un sistema monomáquina tradicional no puede** tratar con garantías de tiempo, coste o variedad.

Esta unidad cubre el **[RA1](ra1.md)** del módulo: gestionar soluciones a problemas propuestos con sistemas de almacenamiento y herramientas del centro de datos.

Lee cada apartado **en orden**. En todos hay un caso (hotel, caja, sensores) y una pregunta del estilo “¿qué elegirías y por qué?”. Las siglas (ACID, OLTP, ETL…) se introducen **después** del ejemplo, no se dan por sabidas. Si puedes explicárselo a un compañero sin mirar la tabla, el apartado está asimilado. La [tarea de clase](tarea-clase.md) aplica eso a 500 GB con un portátil; la [autoevaluación](autoevaluacion.md) comprueba vocabulario. Ninguna sustituye a Moodle.

## Qué vas a trabajar

| Apartado | Criterio | Qué te llevas |
| --- | --- | --- |
| [1.1 Por qué Big Data y las 5 Vs](por-que-big-data.md) | **a)** | Reconocer cuándo un problema es (o no) Big Data |
| [1.2 Clústeres](clusters.md) | **a)** | Por qué se escala en horizontal y qué ganas (rendimiento, disponibilidad) |
| [1.3 Almacenamiento](almacenamiento.md) | **a)** | Relacional, NoSQL, almacén de informes, lago; y, desde cero, ACID, CAP y BASE |
| [1.4 Procesamiento](procesamiento.md) | **a)** / **d)** | Paralelo frente a distribuido, lotes, stream; operar el día a día frente a analizar |
| [1.5 Arquitectura y ecosistema](arquitectura.md) | **a)** | Capas (ingesta → visualización) y el “paisaje” de herramientas |
| [1.6 Ingesta de datos](ingesta.md) | **b)** | Introducción, pipeline, ETL/ELT, Hola ETL (pandas/DuckDB), herramientas y consideraciones |
| [1.7 Formatos de datos](formatos.md) | **c)** | Elegir formato (reservas de hotel): Avro, Parquet, ORC, Arrow, DuckDB |
| [1.8 Pentaho](pentaho.md) | **d)** / **e)** | PDI (Spoon/Pan/Kitchen): filtrar, unir, JSON, nube, jobs y BD del hotel |
| [Tarea para practicar en clase](tarea-clase.md) | RA1 + **RA2** | 500 GB con un portátil: concurrente, paralelo, distribuido |
| [Autoevaluación](autoevaluacion.md) | — | 25 preguntas de la unidad (no puntúa en Moodle) |

!!! info "Sobre el material original"
    Se mantiene el hilo pedagógico de los paquetes eXeLearning (*Introducción*, *Ingesta*, *Formatos*), de los apuntes de aula de ingesta y formatos, y del PDF *Pentaho*. El texto se ha unificado, se han corregido imprecisiones (escalado vertical, JSON, matices de ciencia de datos) y se ha alineado cada apartado con un criterio del RA1.

    El PDF de prácticas se puede descargar aquí: [Pentaho.pdf](../assets/originales/Pentaho.pdf).
