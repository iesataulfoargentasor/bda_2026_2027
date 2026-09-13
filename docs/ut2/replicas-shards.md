---
title: 2.8 Réplicas y particiones
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.8. Réplicas y particiones

Aquí se **prueba** el criterio **c)** (un nodo se apaga y el dato sigue) y se **ve** el **e)** (añades un *shard* o un secundario y el sistema **crece**).

## Conjunto de réplicas (Mongo)

Un **replica set** es un grupo de `mongod` que guardan el **mismo** dataset.

| Pieza | Oficio |
| --- | --- |
| **Primario** | Recibe las **escrituras** |
| **Secundarios** | Copian el **oplog** (diario de operaciones) y pueden servir lecturas |
| **Árbitro** | Solo **vota**; no guarda datos (útil para tener número impar barato) |

El cliente apunta al **conjunto**, no a una IP suelta. Si el primario muere, los que quedan **eligen** otro (mayoría). Por eso se recomienda **3** nodos que votan (o 2 + árbitro, con matices).

**Probar tolerancia (c):** en el lab, con permiso, `db.shutdownServer()` en el primario y comprobar que `rs.status()` muestra un primario nuevo y que `insertOne` **sigue** funcionando. Eso es el criterio, no un dibujo.

Lecturas: `readPreference` (`primary`, `secondaryPreferred`…). Escrituras: `writeConcern` (`w: 1` vs `w: "majority"`). *Majority* = más seguro, un poco más lento. Encaja con [CAP](../ut1/almacenamiento.md): no puedes tener “siempre escrito en todos” y “siempre disponible” si se parte la red.

## Particionar (*sharding*)

Cuando **no cabe** o las escrituras saturan un solo replica set, partes la colección.

| Pieza | Oficio |
| --- | --- |
| **Shard** | Un replica set con **un trozo** de los documentos |
| **Config** | Metadatos: qué rango vive en qué shard |
| **mongos** | *Router*: la app habla con él |

La **shard key** decide el trozo (`hotel`, `id_reserva`…). Una clave que manda **todo** a Laredo es un *hotspot*. Una clave que **reparte** (hash de `id_reserva`) escala mejor las escrituras.

Habilitar (idea; los hosts los da el aula):

```javascript
sh.enableSharding("hotel")
sh.shardCollection("hotel.reservas", { id_reserva: "hashed" })
```

**Crecer (e):** añades un shard, el equilibrador **mueve chunks**. La aplicación **no** cambia de URI si ya hablaba con `mongos`.

No montéis un clúster partido para 500 documentos. El criterio e) se **visualiza** en el diagrama y, si el lab lo tiene, en `sh.status()`.

!!! tip "HDFS y Mongo, misma idea"
    Bloque ×3 en DataNodes ≈ documento ×N en secundarios. Añadir DataNode ≈ añadir shard. El RA2 quiere que **veáis** esa rima, no que memoricéis puertos.
