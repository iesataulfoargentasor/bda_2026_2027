---
title: 2.5 Familias NoSQL
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.5. Familias NoSQL

**NoSQL** = *not only SQL*: no es “prohibido SQL”. Es **otra familia** cuando el relacional se queda corto en **volumen**, **variedad** o **escala horizontal**. Complementa a la caja ([ACID](../ut1/almacenamiento.md)); no la sustituye para cobrar.

El criterio **a)** aquí: estas bases **depositan** formas raras (JSON, grafos) y **responden rápido** a *su* tipo de pregunta. El **d)**: muchas permiten **guardar sin esquema rígido** y validar **al leer** o con reglas suaves.

## Por qué aparecen

El relacional pide el esquema **antes**. Si en abril el hotel añade `mascota` al JSON, en SQL sueles **migrar** la tabla. En documental **insertas** el campo nuevo en los documentos nuevos; los viejos siguen sin él.

Prioridad típica: **disponibilidad y escala** frente a “todas las réplicas coinciden *ya*” ([CAP / BASE](../ut1/almacenamiento.md)). Un *like* puede retrasarse un segundo; un cobro, no.

## Cuatro modelos (elige el problema)

| Familia | Unidad | Encaje en el hotel | Productos que verás citados |
| --- | --- | --- | --- |
| **Documento** | JSON/BSON anidado | Reserva con huéspedes y extras | MongoDB, CouchDB |
| **Clave-valor** | `clave → blob` | Sesión, caché de disponibilidad | Redis, DynamoDB, Riak |
| **Columnas** | Familia de columnas, filas enormes | Series de sensores, logs | Cassandra, HBase, Bigtable |
| **Grafo** | Nodos y aristas | “Quién recomendó el hotel a quién” | Neo4j, Neptune |

### Documento

Una **reserva** es un objeto: hotel, canal, lista de noches, a veces un cobro embebido. Consultas por campo (`hotel: Laredo`). Es el modelo que profundizamos en [2.6](mongodb.md).

### Clave-valor

`reserva:18442` → bytes. Rápido si **conoces la clave**. Mal sitio para “todas las de Trasmiera”. Redis a menudo tipa el valor (contador, lista).

### Columnas

Piensa en una hoja **muy ancha**: cada sensor es una columna que **aparece cuando hay medida**. Bien para *scan* de un periodo. HBase vive sobre [HDFS](hdfs.md).

### Grafo

Pregunta: *¿el huésped de Potes está a dos recomendaciones de un VIP?* Un `JOIN` SQL de 8 tablas duele; el grafo **camina** aristas (*traverse*).

## Partir y copiar (e y c)

**Particionar / *shard*:** cada nodo guarda un **trozo** (por rango de `id`, por lista, por *hash*). Motivos: no cabe, las escrituras saturan un solo disco, quieres otro nodo que atienda si uno está ocupado. No partes 200 filas “por moda”: el troceo **cuesta**.

**Replicar:** el **mismo** trozo en varias máquinas. No confundir: réplica = copia; *shard* = trozo. Lo seguro es **las dos cosas**.

- *Primario–secundario:* escribes en uno; los demás siguen. El primario es un punto débil si no hay elección automática.
- *Varios primarios / entre pares:* varios aceptan escritura; pueden **discrepar** un rato.

**Consistencia fuerte:** tras escribir, **toda** lectura ve el valor. Banca.  
**Eventual:** las copias se igualan *al rato*. Redes, *likes*, a veces stock no crítico.

Auto-*sharding*: la aplicación **no** reparte a mano. El motor lo hace. En SQL horizontal casero sueles romper transacciones y escribir pegamento.

## Implantar sin drama

Empieza pequeño (Community, un nodo). Pregunta: ¿crecimiento a 6 meses? ¿caída tolerable? ¿más lecturas o escrituras? ¿esquema fijo o inquieto? ¿hay comunidad y conector Python?

Limitaciones honestas: **poco estándar** entre productos, GUI desigual, menos perfiles baratos que de SQL.

!!! success "Criterio a) y d)"
    Importan porque **tragan variedad**, **escalan añadiendo nodos** y te dejan **guardar el JSON de hoy** aunque el informe de 2027 aún no exista.
