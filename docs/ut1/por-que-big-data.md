---
title: 1.1 Por qué Big Data y las 5 Vs
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.1. Por qué Big Data y las 5 Vs

Los sistemas clásicos (un servidor, una base relacional, un lote nocturno) funcionan mientras el dato cabe, llega a un ritmo previsible y tiene un esquema fijo. Cuando eso se rompe, aparecen las metodologías de **macrodatos** / **Big Data**.

No hay una ley que diga “a partir de X terabytes ya es Big Data”. El criterio práctico es: **el sistema tradicional no escala** en volumen, velocidad o variedad (o el coste de hacerlo en vertical es inasumible).

## De los eventos al valor

Antes de las herramientas, conviene el recorrido que luego verás en las capas de la arquitectura:

| Escalón | Qué es | Ejemplo |
| --- | --- | --- |
| **Evento** | Algo ocurre en el mundo | Un sensor de una estación, un pago con tarjeta, un clic en la web |
| **Dato** | El evento queda registrado | Fila en una tabla, JSON, imagen, log |
| **Información** | Datos organizados | Pagos del día en una tabla; fotos en carpetas por fecha |
| **Conocimiento** | Modelos o reglas con sentido | “Este patrón de gasto predice impago” |
| **Sabiduría** | Saber *cuándo* aplicar ese conocimiento | Usar el modelo solo en el contexto para el que se validó |
| **Valor** | La decisión mejora el resultado | Menos fraude, menos stock parado, un diagnóstico más rápido |

Las tecnologías de Big Data **capturan, integran, almacenan y procesan**. Extraer valor (modelos, predicciones) lo hacen la **minería de datos**, la **ciencia de datos** y la **IA**, apoyándose en esa infraestructura. No son sinónimos: la ciencia de datos no “es solo minería en Big Data”; es un oficio más amplio (pregunta, calidad, modelo, comunicación). En este módulo nos quedamos en la **infraestructura y el flujo** que esas disciplinas necesitan.

## Las 5 Vs

Sirven para **diagnosticar** un problema, no para memorizar una lista. Si varias Vs fallan a la vez, casi seguro necesitas un diseño de Big Data.

### Volumen

Cantidad de bytes. Hoy se habla con naturalidad de **terabytes** y **petabytes**; los centros grandes llegan a **exabytes**.

| Nombre (SI) | Símbolo | Bytes (aprox.) |
| --- | --- | --- |
| Kilobyte | kB | 10³ |
| Megabyte | MB | 10⁶ |
| Gigabyte | GB | 10⁹ |
| Terabyte | TB | 10¹² |
| Petabyte | PB | 10¹⁵ |
| Exabyte | EB | 10¹⁸ |
| Zettabyte | ZB | 10²¹ |

En informática también existen KiB, MiB, GiB (potencias de 2: 1 KiB = 1024 bytes). Un fabricante de discos suele anunciar GB en base 10; el sistema operativo a menudo muestra GiB: por eso “el disco de 1 TB no llega a 1000 GB en el explorador”.

**De dónde sale el volumen:** transacciones, logs, redes sociales, sensores e IoT, historiales clínicos, genómica, satélites, Open Data, CCTV, RFID, industria.

!!! example "Orden de magnitud"
    Si guardas 4 bytes al día (un peso) por cada persona del planeta (~8·10⁹) durante un año, ocupas del orden de **12 TB**. Eso es *un* atributo. Multiplica por historiales, imágenes o vídeo y entiendes por qué un único disco (o un único servidor) no es el plan.

### Velocidad

No basta con que quepa: los datos **siguen llegando**. El reto es capturarlos, integrarlos con lo que ya tienes y, si el negocio lo pide, reaccionar **antes de que dejen de servir**.

De ahí el procesamiento **en streaming** y las colas (Kafka, etc.). Dimensionar el disco no resuelve un atasco en la ingesta.

### Variedad

Tres familias que conviven en el mismo proyecto:

| Tipo | Qué es | Ejemplo |
| --- | --- | --- |
| **Estructurado** | Esquema fijo (filas y columnas) | Tabla SQL de facturas |
| **Semiestructurado** | Hay marcas o claves, el esquema puede variar | JSON, XML, logs con campos opcionales |
| **No estructurado** | No hay esquema tabular útil de entrada | PDF, foto, audio, vídeo, texto libre |

Un data warehouse clásico espera estructurado. Un **data lake** acepta el dato “como llega” y retrasa el esquema (*schema-on-read*).

### Veracidad

¿Te puedes fiar? Duplicados, sensores descalibrados, sesgos, bots, campos vacíos, relojes mal puestos. A más volumen, más basura si no hay **calidad y gobierno** (linaje, metadatos, reglas de limpieza).

Un modelo sobre datos sucios toma **peores** decisiones, no más rápidas.

### Valor

Es la V que justifica el gasto. Almacenar por almacenar no es Big Data: es un archivo caro. El valor aparece cuando una decisión (precio, ruta, alerta, diagnóstico) **mejora** respecto a no usar esos datos.

## Qué conseguimos (si el diseño es bueno)

- Integrar fuentes que antes vivían en silos.
- Replicar y distribuir para **no parar** si cae un nodo.
- Procesar en paralelo lo que una máquina no termina a tiempo.
- Alimentar minería / IA y **cuadros de mando** para quien decide (criterio **e)** del RA1).

!!! failure "Errores frecuentes"
    - “Tenemos Big Data porque usamos Hadoop” (la herramienta no define el problema).
    - “Todo a tiempo real” (el principio SCV, en [1.4](procesamiento.md), te dirá por qué no).
    - Confundir **MB** de marketing con lo que cabe de verdad en RAM.

## Para el criterio a)

Antes de elegir Mongo, Parquet o Pentaho, debes **caracterizar** el problema: ¿qué Vs duelen?, ¿el dato es de negocio transaccional o analítico?, ¿hace falta histórico en bruto? Eso es diseñar la solución de almacenamiento, no instalar software.
