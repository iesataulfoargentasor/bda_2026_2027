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
| **c)** | Se ha probado la tolerancia a fallos de los sistemas. | [2.3](hdfs.md) prepara la comprobación de copias. En [2.8](replicas-shards.md) se detiene el primario de MongoDB y se comprueba la recuperación. |
| **d)** | Se ha determinado que se pueden almacenar tantos datos como se desee y decidir cómo utilizarlos más tarde. | [2.3](hdfs.md) y [2.5](nosql.md) introducen la conservación y el esquema. En [2.6](mongodb.md), [2.7](modelado.md) y [2.9](pymongo.md) se reutilizan y consultan datos con estructuras diferentes. |
| **e)** | Se ha visualizado que el sistema puede crecer fácilmente añadiendo módulos. | [2.2](ecosistema.md), [2.3](hdfs.md) y [2.5](nosql.md) presentan las opciones. En [2.8](replicas-shards.md) se observa la incorporación de un shard y el movimiento de datos. |

La [práctica integradora](practica-integradora.md) vuelve a recorrer los cinco criterios con un conjunto ficticio propio. En Moodle se entregan la URL del repositorio y el commit; el detalle está en ese apartado.

## Qué cambia respecto a la UT1

En la [UT1](../ut1/ra1.md) diseñasteis la solución y validasteis el informe que recibiría gerencia. En la [tarea de los 500 GB](../ut1/transicion-ut2.md) propusisteis qué recursos harían falta si crecía el histórico. En el RA2 ponéis a prueba esas decisiones. Para defender una conclusión, identificad el dato de partida, el cambio que habéis hecho y el resultado que habéis observado.

## Evidencias que conectan teoría y práctica

| Criterio | Qué recuperáis de la UT1 | Qué debéis poder mostrar en la UT2 |
| --- | --- | --- |
| **a)** | Elegisteis dónde guardar originales y dónde preparar el informe. | Medid cuánto ocupa la entrada y qué operación necesita cada usuario. Justificad el almacén según esos datos y el plazo. |
| **b)** | Contrastasteis las sumas de Pentaho antes de publicar el CSV. | Comparad el mismo agregado con uno y dos trabajadores. Mostrad dónde se ejecutaron las tareas, los subtotales por hotel y los tiempos. |
| **c)** | Probasteis qué pasaba si faltaba una entrada del cierre. | Detened un miembro del conjunto de réplicas. Registrad cuándo podéis volver a leer la reserva anterior y confirmar una nueva. |
| **d)** | Conservasteis los originales y el significado de sus campos. | Usad el histórico para responder a otra pregunta y contrastad la respuesta sobre el mismo conjunto. Indicad qué campos, unidades y periodo habéis usado. |
| **e)** | Propusisteis cuándo convendría ampliar el equipo del hotel. | Comparad la ubicación de los datos antes y después de añadir un módulo. Explicad qué se ha repartido y comprobad que las noches siguen sumando lo mismo. |

### Evidencias mínimas comunes de b) y e)

| Criterio | Experiencia común | Entrega individual |
| --- | --- | --- |
| **b)** | Comparación A/B de 2.4: mismo agregado y entrada, uno y dos trabajadores; tareas observadas, calentamiento y tres ejecuciones medidas por configuración. | Identificación de datos, versiones y recursos; tareas y nodos; tiempos y medianas; totales contrastados; explicación de la mejora o ausencia de ella y límites físicos. |
| **e)** | Demostración o ejecución de 2.8: registro del primer y segundo shard, ubicación de datos y movimiento de un rango con conservación comprobada. | Shards registrados antes y después; recurso incorporado; ubicaciones; comprobación de documentos, tipos y noches; distinción entre capacidad, reparto y rendimiento. |

Estas observaciones forman parte del recorrido común. La instalación individual del laboratorio de particionado sigue siendo opcional; si no se realiza, el docente lo demuestra y facilita los registros para que cada alumno los interprete. Lo mismo se aplica a b) cuando el equipo no admite dos trabajadores. El profesor concreta en Moodle sesión, formato y entrega; no sustituye una prueba por cifras inventadas. Si una incidencia impide observarla, se reprograma y se identifica como pendiente.

Si detenéis un proceso y el servicio se recupera, podéis explicar cómo respondió a ese fallo en vuestro equipo. La pérdida del ordenador completo exigiría una prueba con máquinas independientes. Para repasar el alcance de cada experimento, volved a la [autoevaluación](autoevaluacion.md).
