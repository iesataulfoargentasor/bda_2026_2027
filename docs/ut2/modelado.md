---
title: 2.7 Modelado documental
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.7. Modelado documental

El criterio **d)** en Mongo no es “tirar JSON a lo loco”. Es: **guardas** lo que hay y **diseñas** para las preguntas de **hoy**, sabiendo que mañana puedes **añadir campos** sin parar el hotel una noche.

## Primero la carga, luego el dibujo

Antes de Compass, responde:

1. ¿Qué pantallas o informes existen? (ocupación por hotel, ficha de reserva)
2. ¿Más lecturas o más escrituras?
3. ¿Una reserva se lee **siempre** con sus huéspedes? → quizá **embeber**.
4. ¿Un hotel se actualiza en 40 000 reservas? → **referencia**, no copies el teléfono 40 000 veces.

Metodología corta: entidades → relaciones → **embeber o referenciar** → índices → (si hace falta) validador.

## Embeber o referenciar

**Embeber:** el cobro va **dentro** de la reserva. Un `find` y listo. Tope práctico: documentos hacia **16 MB**. Mal si el array **crece sin techo** (todas las incidencias de diez años).

**Referenciar:** `id_hotel` apunta a la colección `hoteles`. Dos lecturas o un `$lookup`. Bien si el hotel **cambia** el teléfono.

| Relación | En el hotel | Suele ir |
| --- | --- | --- |
| 1:1 | Reserva ↔ ficha de check-in breve | Embebido |
| 1:N pequeño | Reserva → 1–4 huéspedes | Embebido |
| 1:N grande | Hotel → decenas de miles de reservas | Referencia (`id_hotel` en la reserva) |
| N:M | Habitaciones ↔ servicios (spa, parking) | Array de ids o colección puente, según consultas |

Jerarquías (comarca → municipio → hotel): a veces un `path` o un array de ancestros; no copies el árbol relacional a ciegas.

## Patrones que sí merecen un nombre

No memorices veinte. Estos salen en aula:

| Patrón | Idea |
| --- | --- |
| **Atributo / polimórfico** | `tipo: "web" \| "ota"` y campos distintos según tipo |
| **Versionado de esquema** | Campo `v: 2` para saber cómo leer documentos viejos |
| **Subconjunto** | En la reserva solo `hotel.nombre` y `hotel.comarca`; el teléfono vive en `hoteles` |
| **Calculado** | Guardas `importe_medio` si el informe lo pide **siempre** y el cálculo es caro |
| **Atípico** | El 1 % de reservas con 200 extras → colección aparte, no hinches el 99 % |

**Antipatrones:** un documento que es un **array infinito**; *joins* mentales de seis colecciones en cada pantalla; duplicar un dato que **cambia** cada día en 100 000 sitios.

## Validar sin volver al SQL rígido

Mongo puede **validar** al escribir (`validator` JSON Schema). Útil para que `noches` sea número. No lo pongas tan estricto que **prohiba** el campo nuevo de abril (chocaría con d).

```javascript
db.createCollection("reservas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["hotel", "noches"],
      properties: {
        hotel: { bsonType: "string" },
        noches: { bsonType: "int", minimum: 1 },
      },
    },
  },
})
```

Sobre una colección ya llena: `collMod`. `db.getCollectionInfos({ name: "reservas" })` enseña el validador.

!!! success "d) en voz alta"
    “Puedo **almacenar** la reserva de 2024 y en 2026 **añadir** `canal_detalle` solo a las nuevas. Las consultas viejas siguen. El modelo **sigue a las preguntas**, no al revés.”
