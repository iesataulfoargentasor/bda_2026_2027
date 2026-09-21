---
title: "U.T. 1. Gestión de soluciones de almacenamiento"
tags:
  - Big Data
  - BDA
  - RA1
---

# U.T. 1. Gestión de soluciones de almacenamiento

El título sigue el **[RA1](ra1.md){target="_blank" rel="noopener"}**: *gestiona soluciones a problemas propuestos, utilizando sistemas de almacenamiento y herramientas asociadas al centro de datos*. No es un tour genérico por “qué es Big Data”: diseñáis el almacén, ingerís, formateáis, procesáis y presentáis.

Antes de 1.1, leed **[el caso: grupo hotelero de Cantabria](caso-hotel.md){target="_blank" rel="noopener"}** (Santander, Laredo, Comillas, Potes). Recepción **opera** ahora; gerencia **informa** a las **8:00** con el cierre de **ayer** (finanzas cierra a las **23:00**). Toda la unidad y la UT2 reutilizan esa cadena.

Leed cada apartado **en orden**. En todos hay un ejemplo y una pregunta del estilo “¿qué elegiríais y por qué?”. Las siglas (ACID, OLTP, ETL…) se introducen **después** del ejemplo, no se dan por sabidas. Si podéis explicárselo a un compañero sin mirar la tabla, el apartado está asimilado.

La [tarea de clase](tarea-clase.md){target="_blank" rel="noopener"} aplica eso a 500 GB con un portátil. Al final de **cada** 1.1–1.8 hay **diez** preguntas (Comprobar respuesta); al cierre, [diez de toda la UT1](autoevaluacion.md){target="_blank" rel="noopener"} (un solo Corregir test). Ninguna sustituye a Moodle.

## Qué vais a trabajar

| Apartado | Criterio | Qué os lleváis |
| --- | --- | --- |
| [El caso: grupo hotelero](caso-hotel.md){target="_blank" rel="noopener"} | — | La cadena, los cuatro hoteles y los dos relojes (23:00 / 8:00) |
| [1.1 Por qué Big Data y las 5 Vs](por-que-big-data.md){target="_blank" rel="noopener"} | **a)** | Un evento (reserva, sensor, cobro) tiene que acabar en una decisión. Un hotel de playa no es un albergue de montaña. |
| [1.2 Clústeres](clusters.md){target="_blank" rel="noopener"} | **a)** | El PMS de Laredo cabe en un servidor; el job de madrugada de los cuatro, no. Si se funde un disco, el panel de las 8 no puede caerse. |
| [1.3 Almacenamiento](almacenamiento.md){target="_blank" rel="noopener"} | **a)** | El cobro es ACID en el PMS. El histórico de gerencia va a un almacén (o a un mart). JSON y fotos, al lago. |
| [1.4 Procesamiento](procesamiento.md){target="_blank" rel="noopener"} | **a)** / **d)** | Recepción **opera** (OLTP). Gerencia **informa** (lote de las 8). El semáforo es otro reloj. |
| [1.5 Arquitectura y ecosistema](arquitectura.md){target="_blank" rel="noopener"} | **a)** / **e)** | Panel de las 8 y semáforo: **dos tubos** (Lambda) o **una cola** (Kappa). El cuadro de mando es una capa; aquí no se pinta. |
| [1.6 Ingesta de datos](ingesta.md){target="_blank" rel="noopener"} | **b)** | Llevar PMS, cobros y sensores al lago o al almacén. El panel de las 8 es el **destino**; no se pinta en Hola ETL. |
| [1.7 Formatos de datos](formatos.md){target="_blank" rel="noopener"} | **c)** | Dirección solo mira tres números; el CSV gordo arrastra doce columnas. |
| [1.8 Pentaho](pentaho.md){target="_blank" rel="noopener"} | **d)** / **e)** | El mismo cruce reservas ⋈ cobros, agregado por hotel y canal. Kitchen de noche; gerencia abre el **CSV**, no Spoon. |
| [Tarea para practicar en clase](tarea-clase.md){target="_blank" rel="noopener"} | RA1 + **RA2** | 500 GB del histórico del hotel: concurrente, paralelo, distribuido |
| [Autoevaluación](autoevaluacion.md){target="_blank" rel="noopener"} | — | Diez de **toda** la unidad (Corregir test). Las diez de cada apartado están al final de 1.1–1.8. No puntúa en Moodle. |
