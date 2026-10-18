---
title: RA1 y criterios de evaluación
tags:
  - BDA
  - RA1
---

# Resultado de aprendizaje 1 (RA1)

Esta unidad desarrolla el **RA1** del módulo *Big Data aplicado* (código **5075**), según el Real Decreto 279/2021 y el currículo de Cantabria establecido en la [Orden EDU/48/2024, de 8 de octubre, anexo VI](https://boc.cantabria.es/boces/verAnuncioAction.do?idAnuBlob=410716). El RA1 y sus criterios se recogen en el bloque del módulo 5075 (BOC de 16 de octubre de 2024, páginas 31060–31062). Las 190 horas del currículo corresponden al módulo completo, no solo a esta unidad.

## Enunciado

**RA 1:** Gestiona soluciones a problemas propuestos, utilizando sistemas de almacenamiento y herramientas asociadas al centro de datos.

## Criterios de evaluación

| CE | Criterio (texto oficial) | Dónde se trabaja en la UT1 |
| --- | --- | --- |
| **a)** | Se ha caracterizado el proceso de diseño y construcción de soluciones en sistemas de almacenamiento de datos. | [1.1](por-que-big-data.md){target="_blank" rel="noopener"} a [1.5](arquitectura.md){target="_blank" rel="noopener"} |
| **b)** | Se han determinado los procedimientos y mecanismos para la ingestión de datos. | [1.6 Ingesta](ingesta.md){target="_blank" rel="noopener"} |
| **c)** | Se ha determinado el formato de datos adecuado para el almacenamiento. | [1.7 Formatos](formatos.md){target="_blank" rel="noopener"} |
| **d)** | Se han procesado los datos almacenados. | [1.4](procesamiento.md){target="_blank" rel="noopener"} y [1.8 Pentaho](pentaho.md){target="_blank" rel="noopener"} |
| **e)** | Se han presentado los resultados y las soluciones al cliente final en una forma fácil de interpretar. | [1.8 Pentaho](pentaho.md){target="_blank" rel="noopener"} (salidas, informes) y capa de visualización en [1.5](arquitectura.md){target="_blank" rel="noopener"} |

## Contenidos y evidencias del currículo

### Cómo demostrar el aprendizaje

La teoría permite justificar decisiones, pero no acredita por sí sola los criterios prácticos. La práctica integradora aporta ejecución y validación para d), y una explicación de los resultados para gerencia para e). El cuestionario es una comprobación conceptual, no sustituye esas evidencias.

La siguiente correspondencia es una orientación didáctica, no un criterio oficial adicional:

| Criterio | Evidencia que podéis explicar |
| --- | --- |
| a) Diseño | Diagrama con origen, almacenamiento, procesamiento y destino, acompañado de una justificación. |
| b) Ingesta | Procedimiento que indica qué se extrae, cuándo, cómo se valida y cómo se repite ante un fallo. |
| c) Formato | Comparación razonada según tipos, consultas, compatibilidad y medidas. |
| d) Procesamiento | Flujo ejecutado y resultados contrastados con la entrada. |
| e) Presentación | Salida con nombres claros, unidades, periodo y explicación para su consumidor. |

Un mismo taller puede aportar evidencias de varios criterios. Por ejemplo, generar un CSV demuestra procesamiento si aplica las reglas solicitadas; su mera existencia no demuestra que sea fácil de interpretar.

Del bloque *Gestión de soluciones con sistemas de almacenamiento y herramientas del centro de datos*:

- Almacenamiento de datos masivo.
- Procesamiento de datos.
- Analítica de Big Data en los ecosistemas de almacenamiento.
- Big Data y Cloud (aparece al elegir destinos: S3, Glue, almacenes gestionados). Primer contacto: [taller AWS Academy y S3](aws-academy-s3.md){target="_blank" rel="noopener"}.

El [RA2](../ut2/ra2.md){target="_blank" rel="noopener"} (UT2) entra en el **sistema** (HDFS, YARN, NoSQL). Aquí el foco es **entender el problema, diseñar el almacén, ingerir, formatear, procesar y mostrar**.

!!! note "Cómo se evalúa"
    Los criterios son el referente. En las prácticas se pide **identificar** la herramienta, **escribir** el flujo (Pentaho u otra), **ejecutarlo** y **comprobar** el resultado. Las entregas formales siguen en Moodle.

    Para practicar por tu cuenta: [autoevaluación de la UT1](autoevaluacion.md){target="_blank" rel="noopener"} (no sustituye a las pruebas del aula). Como cierre: [práctica integradora con Pentaho](tarea-clase.md), con evidencias de diseño, ingesta, formato, procesamiento y presentación. Después: [transición de los 500 GB](transicion-ut2.md), puente hacia el RA2.
