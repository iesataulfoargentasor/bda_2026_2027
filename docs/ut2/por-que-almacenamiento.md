---
title: 2.1 Por qué un almacén masivo
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.1. Por qué un almacén masivo

El criterio **a)** pide esto: entender **por qué** hace falta un sistema pensado para **depositar** y **procesar** grandes cantidades de **cualquier tipo** de dato, **rápido**. No es “comprar un disco más gordo”.

## El hotel el martes por la mañana

Sigue el [grupo hotelero de Cantabria](../ut1/caso-hotel.md). El job de la noche tiene que acabar **antes de las 8**.

Recepción pica reservas (JSON). Los sensores de habitación sueltan una línea cada 30 s. Marketing quiere las fotos de las reformas. Finanzas cierra cobros. Todo eso **cabe** en un portátil el día 1. A los seis meses, el CSV de logs ya no abre en Excel y el informe de ocupación tarda la noche.

Tres exigencias del RA2, en castellano:

1. **Depositar mucho.** No eliges de antemano “solo tablas de 20 columnas”. Entra texto, JSON, imagen, Parquet.
2. **Procesar en el sitio.** Mover 8 TB por la red hacia un programa es más lento que **llevar el cálculo al nodo que ya tiene el bloque**.
3. **Rápido a escala.** “Rápido” no es el clic del cajero (eso sigue en [OLTP](../ut1/procesamiento.md)). Es acabar el job de la noche **antes de las 8**.

Eso es la **importancia** del almacén masivo: sin él, el resto del ecosistema (Spark, Hive, Mongo, el panel) trabaja sobre un embudo.

## Cualquier tipo (variedad)

En la [UT1](../ut1/por-que-big-data.md) las 5 V ya decían que el dato no es solo la fila SQL. Aquí lo **guardas de verdad**:

| Qué llega | Dónde encaja de primeras |
| --- | --- |
| CSV / Parquet de reservas | [HDFS](hdfs.md) (lago de ficheros) |
| JSON de sensores, anidado | HDFS (bruto) o [MongoDB](mongodb.md) (consultas) |
| Foto de la habitación | HDFS (objeto grande); metadatos en Mongo |
| Grafo “quién recomendó a quién” | Familia [NoSQL de grafos](nosql.md) |
| Caché de sesión del motor de reservas | Clave-valor (Redis o similar) |

El relacional **sigue** para cobrar. El almacén masivo es el sitio donde **juntas** lo que la caja no puede masticar.

## Rápido = cálculo junto al dato

Si copias 500 GB al portátil para contar noches por hotel, el cuello es el **USB o la red**, no la CPU. El modelo de Hadoop (y de muchas NoSQL) es:

- el fichero **ya está partido** en trozos en varias máquinas;
- cada máquina **cuenta su trozo**;
- al final **juntas** los parciales.

Eso es el criterio **b)** visto desde la puerta: el almacén no es un armario muerto; **está pensado para que el procesamiento se siente encima**. El detalle está en [2.4](computacion-distribuida.md).

## Sin un solo punto que lo tumbe todo

Un NAS de un disco es barato y **frágil**. El almacén masivo **asume** que los discos mueren (criterio **c)**). Por eso **replica** bloques o documentos. Lo verás en HDFS (factor 3) y en el *replica set* de Mongo.

## Guardar ahora, decidir el uso después

El criterio **d)** es el lago: escribes el JSON de 2024 **sin** haber inventado el informe de 2026. Mañana Hive o Spark leen solo `hotel` e `importe`. Eso se llama a menudo **esquema al leer** (*schema-on-read*): no tiras el bruto porque hoy no sepas la pregunta.

!!! success "Lo que tienes que poder decir"
    “Importa porque **cabe cualquier cosa**, se **procesa donde está**, **sobrevive** a un disco y **crece** sin cambiar el programa de reservas.”
