---
title: 1.2 Clústeres de computadoras
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.2. Clústeres de computadoras

Un **clúster** es un conjunto de ordenadores (**nodos** o servidores) unidos por red que resuelven trabajo **como si fueran uno**. En Big Data es la pieza que permite dejar de depender de “el servidor más gordo que podamos pagar”.

Hoy se construyen sobre **commodity hardware** (máquinas normales) más un *framework* de computación distribuida, no solo sobre mainframes caros.

## Qué ganas

| Propiedad | En la práctica |
| --- | --- |
| **Alto rendimiento** | Parte el trabajo en subtareas y las ejecuta a la vez en varios nodos. |
| **Alta disponibilidad** | Si un nodo cae (luz, disco, red), otro replica o asume el servicio. |
| **Equilibrio de carga** | No mandas todo al mismo nodo: miras tamaño del trabajo, carga y potencia. |
| **Escalabilidad** | Añades nodos cuando crece el dato; no hace falta acertar el tamaño el día 1. |

## Escalado vertical y horizontal

| | Vertical (*scale-up*) | Horizontal (*scale-out*) |
| --- | --- | --- |
| Qué haces | Más CPU, RAM o disco **en la misma máquina** | **Más máquinas** en el clúster |
| Límite | El mejor hardware del catálogo (y su precio) | Red, coordinación y presupuesto de nodos |
| Típico en | Un SGBD relacional en un solo servidor | Hadoop, almacenes distribuidos, muchas NoSQL |

!!! warning "No se llama *scale-in*"
    El material antiguo llamaba *scale-in* al vertical. En la jerga habitual, **scale-up** es vertical y **scale-out** es horizontal. *Scale-in* suele significar **quitar** nodos (reducir el clúster). En clase usamos vertical / horizontal.

El vertical **no te da escalabilidad real** en Big Data: siempre hay un techo. El horizontal es el que encaja con volumen creciente.

## Cuándo un clúster no hace magia

Si la tarea **no se puede partir** (cada paso depende del resultado del anterior), añadir nodos no acorta el tiempo de forma lineal. Eso se detalla en [procesamiento paralelo](procesamiento.md). El clúster brilla cuando hay **independencia** entre trozos (sumar bloques, mapear ficheros, consultas que se reparte el motor).

## Relación con el RA1

Diseñar el almacenamiento masivo implica decidir: ¿un servidor ACID o un clúster que replica y reparte? Esa decisión condiciona ingesta, formato y cómo presentarás el resultado si un nodo falla a mitad de un job.
