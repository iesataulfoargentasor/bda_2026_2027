---
title: RA2 y criterios de evaluación
tags:
  - BDA
  - RA2
---

# Resultado de aprendizaje 2 (RA2)

Esta unidad desarrolla el **RA2** del módulo *Big Data aplicado* (código **5075**), según el Real Decreto 279/2021 y el currículo de Cantabria establecido por la [Orden EDU/48/2024, anexo VI, página 148](https://boc.cantabria.es/boces/verAnuncioAction.do?idAnuBlob=410716#page=148).

## Enunciado

**RA 2:** Gestiona sistemas de almacenamiento y el amplio ecosistema alrededor de ellos, facilitando el procesamiento de grandes cantidades de datos, sin fallos y de forma rápida.

## Criterios de evaluación

| CE | Criterio (texto oficial) | Dónde se trabaja en la UT2 |
| --- | --- | --- |
| **a)** | Se ha determinado la importancia de los sistemas de almacenamiento para depositar y procesar grandes cantidades de cualquier tipo de datos rápidamente. | [2.1](por-que-almacenamiento.md), [2.2](ecosistema.md), [2.3](hdfs.md), [2.5](nosql.md) |
| **b)** | Se ha comprobado el poder de procesamiento de su modelo de computación distribuida. | [2.2](ecosistema.md) (MapReduce, YARN, primer job) y [2.4](computacion-distribuida.md) (medir el poder) |
| **c)** | Se ha probado la tolerancia a fallos de los sistemas. | [2.3 HDFS](hdfs.md) (réplica de bloques) y [2.8 Réplicas y shards](replicas-shards.md) |
| **d)** | Se ha determinado que se pueden almacenar tantos datos como se desee y decidir cómo utilizarlos más tarde. | [2.3](hdfs.md) (WORM, esquema al leer), [2.5](nosql.md) (esquema dinámico) y [2.7](modelado.md) |
| **e)** | Se ha visualizado que el sistema puede crecer fácilmente añadiendo módulos. | [2.2](ecosistema.md) (piezas Hadoop), [2.3](hdfs.md) (más *datanodes*), [2.5](nosql.md) (*auto-sharding*), [2.8](replicas-shards.md) |

La [práctica integradora](practica-integradora.md) vuelve a recorrer los cinco criterios con un conjunto ficticio propio. En Moodle se entregan la URL del repositorio y el commit; el detalle está en ese apartado.

## Qué cambia respecto a la UT1

En la [UT1](../ut1/ra1.md) **diseñabas** la solución (dónde guardar, cómo ingerir, en qué formato, cómo presentar). Aquí **gestionas el sistema** que aguanta el volumen: el clúster de ficheros, el modelo *map* / *reduce*, las familias NoSQL y cómo se **replican** y **parten**.

La [tarea de los 500 GB](../ut1/transicion-ut2.md) sirve de puente: hay que medir si el equipo y el procedimiento cumplen el plazo, y justificar cuándo conviene ampliar o distribuir recursos.

!!! note "Cómo se evalúa"
    Debes poder **justificar** la elección del sistema, **comprobar** el cálculo y su reparto, **probar** la recuperación ante un fallo definido y **observar** qué aporta una ampliación. Cada conclusión indicará configuración, datos y límites; no se promete conservar cualquier dato ante cualquier caída. Las entregas siguen en Moodle.

    Para practicar: [autoevaluación de la UT2](autoevaluacion.md).

## Evidencias que conectan teoría y práctica

| Criterio | Evidencia útil | Conclusión que debe evitarse |
| --- | --- | --- |
| a) | Relacionar formatos, volumen, consultas y plazo del cierre | «Muchos datos» sin medir ni explicar la carga |
| b) | Job, tareas observadas, resultado contrastado y tiempos comparables | Una agregación standalone demuestra distribución |
| c) | Estado inicial, fallo concreto, continuidad o interrupción y recuperación | Tres contenedores protegen frente a perder el ordenador |
| d) | Reutilizar datos conservados con metadatos y lectores compatibles | Capacidad literalmente infinita o ausencia de reglas |
| e) | Mostrar el recurso añadido y qué capacidad o función aporta | Añadir cualquier nodo duplica siempre el rendimiento |

### Evidencias mínimas comunes de b) y e)

| Criterio | Experiencia común | Entrega individual |
| --- | --- | --- |
| **b)** | Comparación A/B de 2.4: mismo agregado y entrada, uno y dos trabajadores; tareas observadas, calentamiento y tres ejecuciones medidas por configuración. | Identificación de datos, versiones y recursos; tareas y nodos; tiempos y medianas; totales contrastados; explicación de la mejora o ausencia de ella y límites físicos. |
| **e)** | Demostración o ejecución de 2.8: registro del primer y segundo shard, ubicación de datos y movimiento de un rango con conservación comprobada. | Shards registrados antes y después; recurso incorporado; ubicaciones; comprobación de documentos, tipos y noches; distinción entre capacidad, reparto y rendimiento. |

Estas observaciones forman parte del recorrido común. La instalación individual del laboratorio de particionado sigue siendo opcional; si no se realiza, el docente lo demuestra y facilita los registros para que cada alumno los interprete. Lo mismo se aplica a b) cuando el equipo no admite dos trabajadores. El profesor concreta en Moodle sesión, formato y entrega; no sustituye una prueba por cifras inventadas. Si una incidencia impide observarla, se reprograma y se identifica como pendiente.

El enunciado oficial se conserva arriba. Su aplicación práctica exige concretar recursos, fallos y límites: «sin fallos» no significa que el hardware nunca falle, sino diseñar y probar la respuesta del sistema a los fallos previstos.

La evaluación reúne explicación y observación. Si una ampliación adicional no puede ejecutarse, documenta esa limitación y el experimento necesario. Para las evidencias comunes de b) y e), completa la observación en la demostración docente; no presentes una predicción como un resultado medido.
