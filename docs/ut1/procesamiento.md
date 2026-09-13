---
title: 1.4 Procesamiento
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.4. Procesamiento de datos

Almacenar no basta: el criterio **d)** pide **procesar** lo guardado. Aquí se decide *cómo* se parte el trabajo y *con qué prisa* debe salir el resultado.

## Paralelo (dentro de una máquina)

Un sistema operativo **reparte tiempo** entre procesos. Si solo hay un núcleo, la “multitarea” es **simulada**: el procesador salta cada pocos milisegundos.

**Multinúcleo:** varios núcleos físicos, cada uno una CPU.  
**Multihilo (SMT):** un núcleo comparte recursos entre hilos; 4 hilos ≠ 4 núcleos.

Una tarea es **paralelizable** si puedes trocearla y juntar resultados (sumar mil millones de números por bloques). No lo es si cada paso depende del anterior (el resultado par/impar decide si sumas o restas el siguiente).

## Distribuido (entre máquinas)

El procesamiento **distribuido** reparte subtareas a **nodos de un clúster**. Es paralelo *más* red, fallos parciales y datos que no están todos en la misma RAM.

MapReduce y Spark viven aquí: “lleva el cálculo al dato”, no al revés.

## Estrategias

| Estrategia | Sensible al tiempo | Volumen típico | Idea |
| --- | --- | --- | --- |
| **Por lotes (batch)** | No | Muy alto | Horas o de noche; todo el histórico |
| **Transaccional** | Sí (≪ 1 s) | Bajo por operación | Un `INSERT`/`UPDATE` de negocio |
| **Tiempo real / interactivo** | Sí | Medio-alto | Consulta analítica mientras miras el dashboard |
| **Streaming** | Sí, al ritmo de llegada | Ventana en memoria | Cada evento actualiza el estado |

!!! tip "Trampa de vocabulario"
    Una transacción *ocurre* en tiempo real, pero un **análisis** en tiempo real **no** es transaccional: no hay `COMMIT` de negocio, hay una consulta o una agregación.

## OLTP y OLAP

| | **OLTP** | **OLAP** |
| --- | --- | --- |
| Para qué | Operación del día (caja, reservas) | Análisis e inteligencia de negocio |
| Operaciones | Pocas filas: insertar, actualizar, borrar | Agregados, cruces, cubos |
| Modelo | Relacional, normalizado | Dimensional, a menudo desnormalizado |
| Tiempo | Milisegundos | Segundos (o menos si cabe en RAM) |
| Usuarios | Muchos concurrentes | Analistas, dirección |
| Relación | Produce los hechos | Lee (sobre todo) esos hechos ya integrados |

OLAP no sustituye a OLTP: **se alimenta** de él (vía ingesta). Mezclar ambos en la misma base “para no duplicar” suele acabar con bloqueos en caja o informes eternos.

## Principio SCV (procesamiento)

Parecido a CAP, pero **no habla de lecturas/escrituras**: habla de **analítica distribuida**. Como máximo dos de tres:

| Letra | Significa aquí |
| --- | --- |
| **S**peed | Poco tiempo desde que el dato está en el sistema analítico hasta el resultado |
| **C**onsistency | Precisión: usas **todos** los datos (no confundir con la C de CAP) |
| **V**olume | Puedes atacar conjuntos enormes |

En Big Data **V casi siempre está**. Entonces:

- **C + V** → lote sobre el 100 % de los datos (el informe de cierre).
- **S + V** → tiempo real sobre una **muestra** o una ventana (menos preciso).
- **S + C** → muy rápido y exacto, pero **no** sobre petabytes enteros.

!!! example "Pregunta de aula"
    ¿Analítica en tiempo real con *todos* los datos del lago? En general **no**: pediría S + C + V. O muestreamos (perdemos C) o esperamos al batch (perdemos S).
