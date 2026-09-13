---
title: 1.8 Pentaho
tags:
  - Big Data
  - BDA
  - RA1
  - Pentaho
---

# 1.8. Pentaho: procesar y presentar

Hasta aquí has **caracterizado** el almacén, la ingesta y el formato. El criterio **d)** pide **procesar** los datos ya almacenados. El **e)** pide **presentarlos** al cliente de forma fácil de interpretar.

En el aula usamos **Pentaho Data Integration (PDI / Kettle)**, de la plataforma Pentaho (Hitachi Vantara). No sustituye a Spark en un clúster de petabytes. Sí te deja **ver** un ETL: extraer, filtrar, unir, agregar y cargar **sin programar el motor**.

PDF de prácticas (clics y capturas): [Pentaho.pdf](../assets/originales/Pentaho.pdf). Esta página explica **qué estás haciendo** en cada caso, para que el PDF no sea una receta ciega.

## Qué es PDI, en una frase

Es una herramienta de **metadatos**: tú dibujas *qué* debe ocurrir (leer este CSV, filtrar, escribir allí). El motor decide *cómo* mover las filas. Por eso un flujo se guarda en un XML (`.ktr` / `.kjb`) y se puede ejecutar igual en tu Windows y en un servidor sin pantalla.

## Kettle: tres piezas que se confunden

| Componente | Analogía | Para qué | Fichero |
| --- | --- | --- | --- |
| **Spoon** | El taller | Diseñar en gráfico (arrastrar pasos) | `.ktr` transformación, `.kjb` job |
| **Pan** | El obrero de *una* pieza | Ejecutar **una transformación** sin ventana | `.ktr` |
| **Kitchen** | El capataz | Ejecutar un **job**: varias transformaciones, abortar, comprobar un destino | `.kjb` |

Spoon es para **clase y diseño**. En producción (o en la entrega “como en empresa”) lanzas **Pan** o **Kitchen** desde terminal o desde un programador (cron). Si solo funciona “cuando yo pulso Play en Spoon”, el procedimiento no está cerrado.

!!! example "Regla para no mezclarlos"
    ¿Un solo flujo de pasos (leer → filtrar → escribir)? → transformación → **Pan**.  
    ¿“Primero esto; si falla, aborta; luego comprueba S3”? → job → **Kitchen**.

## Qué puedes hacer en Spoon (y cómo se nota el criterio d)

- **Orígenes:** CSV, Excel, XML, JSON, tablas SQL, APIs.
- **Transformar:** filtrar filas, quitar nulos, *Select values* (renombrar y tipar), *lookup*, *merge join*, agregar, fórmulas.
- **Destinos:** otro fichero, una tabla, S3, Azure…
- **Jobs:** si la carga a la nube falla, **abortar** para no dar por bueno un panel mentiroso.

Has **procesado** (d) cuando la salida **no es** la entrada: menos filas, columnas con nombre de negocio, un agregado, un JSON que otra app entiende.

## Del `.ktr` al cliente (criterio e)

El cliente (dirección, un compañero de marketing, el tutor de prácticas) **no** abre Spoon. “Fácil de interpretar” es:

- un CSV con **cabeceras claras** y solo las columnas pedidas,
- un JSON coherente para otra aplicación,
- una **tabla** que Power BI o un informe ya entienden,
- un **agregado** (ventas por fabricante, puntuación media) en lugar de 200 000 filas crudas.

Si entregas el Airbnb crudo, con nulos y columnas en inglés técnico, has movido bytes y **no** has presentado.

!!! tip "Prueba del cliente"
    Cierra Spoon. Abre el fichero de salida como lo abriría alguien del módulo de empresa: Excel, un visor JSON, una consulta SQL. Si tiene que preguntarte “¿qué es `host_listings_count`?”, el criterio **e)** no está cerrado.

## Mapa de los casos del PDF

El detalle de cada clic está en el PDF. Aquí va **qué competencia** entrenas.

| Caso | Qué haces, en cristiano | Criterio |
| --- | --- | --- |
| 0 | Comprobar que PDI arranca y ver la versión | Entorno |
| 1 | CSV → filtrar → ordenar → escribir; repetir con **Pan** | **d)** |
| 2 | Unir dos orígenes (*merge join*) y **agregar** | **d)** |
| 3 | Airbnb: elegir columnas, nulos, filtro avanzado, salida **JSON** | **d)** y **e)** |
| 4 | Fórmulas y dejar el resultado en **S3 / Azure** (cloud del BOE) | **d)** |
| 5 | Un **job** que orquesta, aborta si falla y se lanza con **Kitchen** | Procedimiento completo |
| 6 | Hablar con una **BD**: cargar, *lookup*, insertar, actualizar, *upsert* | **d)** con SGBD |

*Upsert* = “si la fila existe, actualiza; si no, inserta”. Es el patrón típico de una carga diaria que no debe duplicar la clave.

## Cómo atacar una práctica (método)

1. En un comentario o en el nombre del job, escribe **la pregunta del cliente** (“listado de estancias de más de 3 noches en Cantabria”).
2. Marca origen, la transformación **mínima** y el destino. Si no puedes decirlo en una frase, el flujo está sobrado o incompleto.
3. Ejecuta en Spoon y usa la **vista previa** de filas: ahí cazas el nulo y el tipo raro.
4. Vuelve a ejecutar con **Pan** o **Kitchen** (como se haría de madrugada).
5. Abre el artefacto **sin Spoon**.

## Errores que se repiten

- Confundir transformación y job (lanzar Kitchen sobre un `.ktr` o al revés).
- Filtrar en la cabeza y no en un paso: el resultado “sale bien una vez” y no es reproducible.
- Dejar rutas `C:\Users\tú\...` tapadas en el flujo: en el PC del aula revienta.
- Cumplir d) (el JSON se genera) y olvidar e) (nadie entiende las claves).

!!! warning "Versiones"
    Usa la versión de PDI que indique el aula. Los menús del PDF pueden cambiar de sitio; los **pasos** (CSV input, Filter rows, Sort rows, Text file output, Table output) se llaman igual.

!!! success "Al terminar la UT1"
    Ante un problema propuesto debes poder: caracterizar el almacén (a), elegir ingesta (b) y formato (c), **procesar** con PDI u otra herramienta del centro de datos (d) y **enseñar** un resultado que no requiera ser ingeniero para leerlo (e).
