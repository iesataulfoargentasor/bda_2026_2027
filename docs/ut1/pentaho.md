---
title: 1.8 Pentaho
tags:
  - Big Data
  - BDA
  - RA1
  - Pentaho
---

# 1.8. Pentaho: procesar y presentar

Pentaho (Hitachi Vantara) es una plataforma de **integración y analítica**. En este módulo usamos sobre todo **Pentaho Data Integration (PDI / Kettle)** para **procesar** datos almacenados (criterio **d)**) y dejar un resultado que el cliente pueda **interpretar** (criterio **e)**): CSV limpio, JSON, tabla, fichero en la nube o la base de un informe.

No sustituye a Spark en un clúster de petabytes. Sí es la herramienta de aula para **ver** un ETL: extraer, filtrar, unir, agregar y cargar **sin programar el motor**.

PDF de prácticas (casos paso a paso): [Pentaho.pdf](../assets/originales/Pentaho.pdf).

## Kettle: tres piezas

| Componente | Para qué | Ficheros |
| --- | --- | --- |
| **Spoon** | Diseñar en gráfico (arrastrar pasos) | `.ktr` transformaciones, `.kjb` jobs |
| **Pan** | Ejecutar una **transformación** sin interfaz | `.ktr` |
| **Kitchen** | Ejecutar un **job** (orquesta varias transformaciones, abortar, comprobar destinos) | `.kjb` |

Spoon define **qué** hacer (metadatos del flujo). Pan y Kitchen son lo que pondrás en un programador (cron, servidor) cuando el diseño ya vale.

## Qué puedes hacer en Spoon

- Conectar orígenes: CSV, Excel, XML, JSON, bases SQL, APIs.
- Transformar: filtrar, limpiar nulos, *lookup*, *merge join*, agregar, fórmulas.
- Cargar destinos: fichero, tabla, S3, Azure…
- Encadenar **jobs**: si falla la carga a S3, abortar; si existe el objeto, seguir.

Eso cubre el criterio **d)** de forma observable: el dato de entrada y el de salida **no son el mismo**.

## De la transformación al cliente (criterio e)

“Fácil de interpretar” no es un `.ktr`. Es:

- Un CSV **con cabeceras claras** y solo las columnas que el negocio pidió.
- Un JSON coherente para otra aplicación.
- Una tabla en el warehouse que Power BI o un informe Pentaho ya entienden.
- Un agregado (ventas por fabricante, media de puntuación) **en lugar de** 200 000 filas crudas.

Si entregas el fichero de Airbnb sin filtrar nulos ni renombrar campos, has procesado a medias y **no** has presentado.

## Mapa de los casos del PDF

Úsalo como guía de laboratorio; el detalle de clics está en el PDF.

| Caso | Qué practicas | Criterio |
| --- | --- | --- |
| 0 | Comprobar la versión de PDI | Entorno |
| 1 | CSV → filtro → ordenar → escribir; ejecutar con **Pan** | **d)** |
| 2 | *Merge join* y agregación | **d)** |
| 3 | Airbnb: *Select values*, nulos, *Java Filter*, salida **JSON** | **d)** **e)** |
| 4 | Fórmulas y salida a **S3 / Azure** | **d)** cloud |
| 5 | **Job** + abortar + **Kitchen** | Orquestación |
| 6 | Tabla: carga, *lookup*, insert, update, upsert | **d)** con SGBD |

## Cómo atacar una práctica

1. Escribe en un comentario del job **qué pregunta** responde (el cliente).
2. Identifica origen, transformación mínima y destino.
3. Ejecuta en Spoon, revisa la vista previa de filas.
4. Vuelve a ejecutar con Pan o Kitchen (como en producción).
5. Abre el artefacto final **como lo abriría el cliente** (Excel, visor JSON, consulta SQL).

!!! warning "Licencia y versiones"
    Comunita PDI / Hitachi: usa la versión que indique el aula. Los capturadores de pantalla del PDF pueden diferir en menús; los **pasos** (CSV input, Filter, Sort, Text file output) se llaman igual.

!!! success "Al terminar la UT1"
    Debes poder, ante un problema propuesto: caracterizar el almacén, elegir ingesta y formato, **procesar** con PDI (u otra herramienta del centro de datos) y **enseñar** un resultado que no requiera ser ingeniero para leerlo.
