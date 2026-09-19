---
title: 1.5 Arquitectura y ecosistema
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.5. Arquitectura por capas y paisaje de herramientas

Un sistema Big Data no es “un programa que lo hace todo”. Si metes ingesta, limpieza, modelos y el PDF para gerencia en el mismo script, no puedes probar, ni sustituir una pieza, ni explicar el diseño (criterio **a)**).

Se parte en **capas** que se hablan entre sí. Cada capa tiene **una** responsabilidad. Así sabes dónde encajan la [ingesta](ingesta.md), el [formato](formatos.md), [Pentaho](pentaho.md) y el cuadro de mando.

## Un caso para no perderse

El hilo del módulo es el [grupo hotelero](caso-hotel.md). En esta página las capas se ven con **otro** negocio, para que no parezcan un invento solo de reservas.

Una comercializadora eléctrica (o un ayuntamiento con contadores) quiere:

- no perder lecturas de los equipos,
- detectar un consumo anómalo,
- y que dirección vea un panel el lunes.

Ese problema **no** se resuelve con una única base Access. Recorre las capas.

## Las capas (el dato entra abajo y el cliente mira arriba)

### 1. Ingesta

Entras a las fuentes que **ya existen**: la BD de facturación, una API del fabricante, un CSV que manda un contratista, un topic de sensores. Tú **no eliges** cómo habla el origen: te adaptas (SQL, HTTP, fichero, cola).

Si esta capa falla, el resto analiza el vacío.

### 2. Colección / integración

Unificas **formato y semántica**. El mismo cliente no puede llamarse `id_cliente` en un sitio y `customerId` en otro sin un criterio. Aquí nace (o se rompe) la calidad.

### 3. Almacenamiento

Lago, warehouse, HDFS, objeto en cloud… [distribuido](clusters.md) si el volumen lo pide. Aquí aplicas lo de [1.3](almacenamiento.md): ¿el negocio puede verse a medias o no? ¿lago o almacén de informes?

### 4. Procesamiento

Infraestructura **batch**, **streaming** o híbrida. *No* extrae valor ella sola: deja el dato **listo** (agregado, limpio, unido). Spark, un job de Pentaho o un script viven aquí.

### 5. Consulta y analítica

SQL, notebooks, modelos. Aquí sale **conocimiento**: “esta ruta de lecturas es anómala”.

### 6. Visualización

Informes y cuadros de mando para el **cliente final**. Es el criterio **e)**: fácil de interpretar. Un `.ktr` o un Parquet crudo **no** son esta capa.

### 7. Seguridad (transversal)

Atraviesa todas las anteriores: quién lee el NIF, cifrado, copias, amenazas internas (un práctico con más permisos de la cuenta) y externas.

### 8. Monitorización (transversal)

¿El job de anoche acabó? ¿El dato del panel es de hoy o de marzo? Auditoría y gobierno. Sin esto, el prototipo de clase funciona y el de producción **miente** sin que nadie lo sepa.

!!! warning "Las dos que se olvidan en el trabajo de clase"
    Seguridad y monitorización. El flujo “CSV → filtro → Excel” llega al 10. Las otras seis capas, si el caso es real, también existen aunque sean simples (una carpeta con permisos y un log de Pentaho).

## Cómo se lee un paisaje (*Big Data landscape*)

Si buscas esa expresión verás pósters con cientos de logos. **No los memorices.** Sitúa **la capa**:

| Capa | Ejemplos que verás en el ciclo | Pregunta que responde |
| --- | --- | --- |
| Ingesta / mensajería | Sqoop, Flume, NiFi, Kafka, Kinesis | ¿Cómo entra el dato? |
| Almacén | HDFS, S3, warehouses cloud, MongoDB, HBase | ¿Dónde reposa? |
| Proceso | MapReduce, Spark, Hive, Pig | ¿Quién transforma a escala? |
| Orquestación | Oozie, Airflow, **Kitchen** (Pentaho) | ¿En qué orden y qué pasa si falla? |
| Visualización | Power BI, Tableau, informes Pentaho | ¿Qué ve el cliente? |

**Hadoop** fue la plataforma pionera de **lotes** sobre HDFS (un sistema de ficheros **repartido**). **Spark** cubre lotes y streaming **en memoria** y convive con ese ecosistema. **Pentaho** se usa en este módulo para **ETL visual** y para **mostrar** el resultado sin programar el motor.

Los mapas cambian de año (nace una marca, muere otra). **Las capas no.**

## Big Data y cloud

El BOE cita cloud. Un *bucket* S3 o un Glue no cambian el razonamiento: sigues decidiendo las 5 V, dónde vive el dato, lote o stream y el formato. Cambia **quién** opera los discos y **cómo pagas**.

En varios servicios analíticos de nube pagas por **dato escaneado**, no solo por dato guardado. Por eso en [1.7](formatos.md) Parquet no es “un capricho moderno”: es menos euros y menos minutos.

!!! success "Al terminar 1.5"
    Coge un caso (contadores, reservas, tickets de caja) y dibuja las **ocho** capas. Pon **una** herramienta o responsabilidad en cada una y justifica la de almacenamiento. Si puedes explicarlo en voz alta a un compañero que no ha leído el tema, el apartado está entendido.
