---
title: Autoevaluación UT2
tags:
  - Big Data
  - BDA
  - RA2
---

# Autoevaluación de la UT2

Cincuenta y cuatro preguntas de **opción múltiple**, con cuatro opciones y **una correcta** sobre el RA2: por qué un almacén masivo, Hadoop, HDFS, MapReduce, familias NoSQL, MongoDB, modelado, réplicas y PyMongo.

No puntúan en Moodle. Al **Corregir test** verás la nota, la respuesta correcta y su explicación. Justifica la elección por el concepto o el resultado esperado, no por la extensión de la opción.

<div class="dwec-quiz" data-dwec-quiz data-src="../../assets/quizzes/ut2.json"></div>

!!! tip "Cómo usarlo"
    Responde las cincuenta y cuatro y corrige. El enlace *Repasar…* te lleva al apartado. Puedes reintentar.

## Antes de responder

Las preguntas combinan conceptos y situaciones de laboratorio. Distingue la **configuración básica** de un sistema de sus posibles ampliaciones: un DataNode no prueba tolerancia por réplica, una agregación local no prueba distribución y una sesión no equivale por sí sola a una transacción.

Lee los supuestos de cada caso: votantes configurados, copias efectivas, datos de entrada y entorno utilizado. Las 15 reservas de MongoDB no corresponden al CSV de 20 reservas del bloque Hadoop. Las escrituras de prueba se realizan en las bases de ejercicios, conservando los originales.

| Bloque | Qué debes distinguir |
| --- | --- |
| **2.1–2.4: almacenamiento y Hadoop** | Capacidad y rendimiento; bloques y tareas; almacenamiento y ejecución; finalización técnica y resultados comprobados. |
| **2.5–2.7: NoSQL, MongoDB y modelado** | Modelo y formato; campo opcional y dato válido; filtro y proyección; referencia y copia histórica; validación y migración. |
| **2.8–2.9: distribución y aplicación** | Réplica y partición; mayoría y datos actualizados; confirmación y timeout; sesión y transacción; elección de primario y caída del proceso. |

## Cómo revisar los errores

1. Responde y anota por qué eliges cada opción, antes de corregir.
2. Lee la explicación incluso si acertaste: comprueba que tu razonamiento coincide.
3. Utiliza «Repasar» para volver al apartado y localiza un ejemplo que lo demuestre.
4. Repite una pequeña prueba cuando sea posible, conservando los datos originales.
5. Explica qué confusión representa cada distractor, por ejemplo atribuir al NameNode el contenido de los bloques o interpretar mayoría como aplicación en todos los secundarios.

Si fallas bloques o rutas, revisa 2.2–2.4. Si confundes replicación, consistencia y particiones, vuelve a 2.5 y 2.8. Para filtros, arrays, cursores y transacciones, contrasta 2.6, 2.7 y 2.9.

El cuestionario comprueba comprensión, pero no sustituye las evidencias de ejecución, interpretación de resultados y pruebas de fallo de las prácticas. Las actividades evaluables y sus condiciones se concretan en Moodle.
