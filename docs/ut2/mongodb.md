---
title: 2.6 MongoDB
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.6. MongoDB

[MongoDB](https://www.mongodb.com/) es la NoSQL **documental** del aula. Una **base** agrupa **colecciones**; una colección agrupa **documentos** BSON (JSON binario: tipos de fecha, binario, `ObjectId`…).

Analogía: base ≈ esquema SQL, colección ≈ tabla, documento ≈ fila… **pero** dos documentos de `reservas` **no** tienen por qué traer las mismas claves (criterio **d)**).

## Arranque (el que diga el aula)

Opciones habituales: instalador Community, **Docker** (`mongo` oficial) o **Atlas** (nube). Cliente:

- **`mongosh`:** shell.
- **Database Tools:** `mongodump` / `mongorestore`, `mongoimport` / `mongoexport`.
- **Compass:** ventana para ver documentos.
- Extensión de VS Code, si la usáis.

En clase: host y puerto del profesor. No copies URI de Atlas de otro ciclo.

```javascript
// mongosh
db.getSiblingDB("hotel")
db.reservas.insertOne({
  hotel: "Laredo",
  canal: "web",
  noches: 3,
  importe: 186.5,
  extras: ["parking"],
})
```

## ObjectId

Si no pones `_id`, Mongo inventa un **ObjectId** (marca de tiempo + máquina + contador). Puedes usar un `_id` tuyo (`id_reserva: 18442`) si te encaja el negocio.

## Consultar

```javascript
db.reservas.find({ hotel: "Laredo" })
db.reservas.find({ hotel: "Laredo" }, { canal: 1, importe: 1, _id: 0 })
db.reservas.find({ noches: { $gte: 4 } }).sort({ importe: -1 }).limit(10)
db.reservas.countDocuments({ canal: "web" })
```

| Idea | Operador / truco |
| --- | --- |
| Comparar | `$gt`, `$gte`, `$lt`, `$lte`, `$ne`, `$in` |
| Texto | `$regex` (caro si no hay índice) |
| Y / O | `{ $and: [ … ] }`, `{ $or: [ … ] }` |
| Anidado | `"cobro.medio": "tarjeta"` |
| Array | `{ extras: "parking" }`, `$elemMatch` |
| Fechas | guarda `Date`, no un string “bonito” si vas a filtrar rangos |
| Expresión | `$expr` para comparar dos campos del mismo documento |

El `find` devuelve un **cursor**: no carga un millón de documentos a la vez. `toArray()` en el *shell* sí puede.

```javascript
const c = db.reservas.find({ comarca: "Trasmiera" })
c.hasNext()
c.next()
```

## Cambiar y borrar

```javascript
db.reservas.updateOne(
  { hotel: "Laredo", canal: "web" },
  { $set: { canal: "ota" }, $inc: { noches: 1 } }
)
db.reservas.updateMany({ importe: { $lt: 0 } }, { $set: { importe: 0 } })
db.reservas.replaceOne({ _id: id }, { hotel: "Potes", noches: 2, importe: 90 })
db.reservas.deleteMany({ hotel: "prueba" })
```

`$set`, `$unset`, `$inc`, `$push`, `$addToSet`, `$pull` son el día a día. `$` posicional actualiza **el elemento del array** que encajó en la query.

Varias escrituras a la vez: `findOneAndUpdate` con `returnDocument: "after"` cuando necesitas el documento **ya** cambiado.

Fichero de aula: [reservas_mongo.jsonl](../assets/practicas/reservas_mongo.jsonl). Importar:

```text
mongoimport --db hotel --collection reservas --file reservas_mongo.jsonl
```

Un documento de ejemplo (una reserva por línea en el `.jsonl`):

```json
{"hotel":"Laredo","canal":"web","noches":3,"importe":186.5,"huespedes":[{"nombre":"Ana","tipo":"adulto"}]}
```

!!! tip "Criterio a)"
    Mongo **deposita** el JSON del motor de reservas **tal cual** (anidado) y **consulta** sin montar ocho tablas. El “rápido” es *para este modelo*; un agregado de 8 TB sigue siendo territorio [HDFS + Spark](computacion-distribuida.md).
