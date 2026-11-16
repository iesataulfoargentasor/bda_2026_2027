---
title: "U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema"
tags:
  - Big Data
  - BDA
  - RA2
---

# U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema

¿Recordáis las **tres noches de Ana en Laredo**? En la UT1 seguisteis su reserva desde el mostrador hasta el informe de gerencia. Con Pentaho cruzasteis reservas y cobros, sumasteis lo cobrado por hotel y canal y dejasteis aparte las reservas pendientes de revisar. Finanzas sigue cerrando a las **23:00** y dirección sigue abriendo el informe a las **8:00 del día siguiente**. [El caso del grupo hotelero](../ut1/caso-hotel.md) · [La práctica de Pentaho](../ut1/tarea-clase.md)

## De dónde venimos y qué cambia

Imaginad que el informe sale con los importes correctos, pero llega a las 10:00. O que a medianoche se detiene el equipo que guardaba el histórico. **¿Cómo averiguaríais qué ha fallado y qué hace falta para llegar a las 8:00?** Ese es el paso al **[RA2](ra2.md)**. Ahora vais a gestionar el almacenamiento y a probar qué ocurre con los datos, el cálculo y el servicio cuando cambia una condición.

Empezad por recuperar vuestra propuesta para los **500 GB y un portátil**. Teníais 300 GB libres y la posibilidad de leer el histórico por bloques desde la red. ¿Qué medida os faltaba para saber si llegaríais a tiempo? Anotadla en vuestra hoja de decisiones y volved a ella cuando comparéis uno y dos trabajadores. [Enunciado y vídeo de la transición](../ut1/transicion-ut2.md) · [Primera sesión de la UT2](por-que-almacenamiento.md)

## Cómo se relacionan los apartados

- **Gerencia trabaja con el histórico (2.1–2.4).** Empezamos con una pregunta que podéis comprobar a mano. Si una fila de Laredo indica tres noches y otra indica dos, ¿cuánto deben aportar juntas aunque las lean equipos distintos? HDFS guarda el fichero, YARN asigna recursos y MapReduce reúne los resultados. Primero contrastáis lo que suma cada hotel y después medís cuánto tarda.
- **Recepción trabaja con una reserva (2.5–2.9).** Mientras gerencia consulta el cierre de ayer, una huésped pide añadir parking para hoy. ¿Qué dato necesitáis localizar? ¿Qué debería poder leer el siguiente recepcionista si se detiene el servidor que aceptó el cambio? En el laboratorio usaréis MongoDB para representar la reserva, modificarla y probar la recuperación. Después repetiréis las consultas desde Python.

En la **[práctica integradora](practica-integradora.md)** volvéis a Santander, Laredo, Comillas y Potes. Gerencia os encarga un cierre comprobado y recepción necesita seguir atendiendo. Elegís los sistemas y mostráis qué ocurre al repartir el cálculo, perder un miembro, añadir otro y consultar el histórico con una pregunta nueva.

## Cómo trabajar la unidad

Seguid la **ruta de estudio** de cada apartado. Como en la UT1, los conceptos esenciales y las prácticas guiadas forman el recorrido común. Las ampliaciones se exigen solo si el profesor lo anuncia. Conservad en vuestra hoja de decisiones el **problema, la entrada, el periodo, el resultado esperado y la comprobación**. En la UT2 añadid **qué recurso habéis cambiado y qué habéis observado**. Si dos ejecuciones sobre la misma entrada dan totales distintos, averiguad por qué antes de comparar los tiempos.

Hay dos observaciones comunes que podéis realizar con vuestro equipo o seguir en una demostración docente. En 2.4 compararéis uno y dos trabajadores. En 2.8 observaréis cómo se incorpora un segundo *shard* al clúster y se traslada a él un rango de datos. En ambos casos cada alumno interpreta los resultados. La instalación individual del laboratorio de particionado es opcional. [Comparación en 2.4](computacion-distribuida.md#evidencia-comun-del-criterio-b-comparar-uno-y-dos-trabajadores) · [Reparto en 2.8](replicas-shards.md#evidencia-comun-del-criterio-e-observar-la-ampliacion) · [Evidencias comunes del RA2](ra2.md#evidencias-minimas-comunes-de-b-y-e)

Los requisitos de terminal, Docker y Python se indican al empezar los talleres. Las entregas evaluables se concretan en Moodle. Cada apartado termina con diez preguntas de repaso y la unidad tiene un cuestionario de 54, con explicación por pregunta. [Entorno Hadoop](ecosistema.md) · [Entorno MongoDB](mongodb.md) · [Autoevaluación](autoevaluacion.md)

<span id="que-vais-a-trabajar"></span>
<span id="que-aprendereis-a-comprobar"></span>

## Mapa de apartados y criterios de evaluación

| Apartado | RA2 | Pregunta que debéis poder contestar |
| --- | --- | --- |
| [2.1 Por qué un almacén masivo](por-que-almacenamiento.md) | **a)** | ¿Qué mediríais si el histórico cabe en disco pero el cierre llega tarde? |
| [2.2 Ecosistema Hadoop](ecosistema.md) | **a, b, e** | ¿Quién guarda el CSV, quién asigna recursos y quién suma las noches? |
| [2.3 HDFS](hdfs.md) | **a, c, d, e** | ¿Dónde están los bloques del fichero y cuántas copias podéis localizar? |
| [2.4 Computación distribuida](computacion-distribuida.md) | **b)** | ¿Se mantiene el total por hotel cuando cambia el número de trabajadores? ¿Qué ocurre con el tiempo? |
| [2.5 Familias NoSQL](nosql.md) | **a, c, d, e** | ¿Qué modelo elegiríais para recuperar una reserva con sus extras? |
| [2.6 MongoDB](mongodb.md) | **a, d** | ¿Cómo comprobaríais que una consulta encuentra las reservas pedidas y que un cambio afecta a la prevista? |
| [2.7 Modelado documental](modelado.md) | **d)** | Si un hotel cambia de nombre, ¿qué nombre debe seguir mostrando una reserva antigua? |
| [2.8 Réplicas y particiones](replicas-shards.md) | **c, e** | ¿Cuándo vuelve a aceptar cambios recepción tras perder el primario? ¿Dónde quedan los datos al añadir un shard? |
| [2.9 MongoDB y Python](pymongo.md) | **c, d** y apoyo a **b** | ¿Obtiene el programa el mismo parte que la consulta manual? |
| [Práctica integradora](practica-integradora.md) | **a–e** | ¿Con qué pruebas defenderíais ante el hotel vuestra solución para el cierre y el mostrador? |

## Prácticas y comprobaciones

| Dónde trabajáis | Entrada | Referencia para comprobar el resultado |
| --- | --- | --- |
| Hadoop, 2.2–2.4 | CSV de 20 reservas de cinco hoteles, incluido Noja | **62 noches reservadas** entre todos. El CSV contiene el precio de la reserva. Para calcular cobros haría falta la fuente de pagos. |
| MongoDB y Python, 2.6 y 2.9 | 15 reservas y 6 opiniones. En las reservas aparecen seis hoteles, incluido Reinosa. | **46 noches reservadas** en la base original. Los ejercicios de escritura se hacen en una copia. |
| Práctica integradora | Histórico ficticio de cerca de 1 GB de los cuatro hoteles del caso | Noches de reservas confirmadas, importe cobrado por hotel, cancelaciones por canal y lecturas de sensores. El fichero de totales de la plantilla permite contrastar cada cifra. |

Cada fila usa sus propias entradas. El ejemplo de Ana os ayuda a recordar qué significa una reserva. Para comprobar el resultado de un taller, usad los registros de ese taller. Un porcentaje de ocupación requeriría además conocer las habitaciones ocupadas y las disponibles en el periodo.

En el entorno básico de Hadoop hay un nodo de datos y uno de ejecución. Podéis observar bloques y tareas. Para probar que una segunda copia permite recuperar un fichero hacen falta copias efectivas en nodos distintos. Si detenéis un contenedor, anotad qué proceso ha caído, qué operación habéis podido repetir y cuánto ha tardado en volver el servicio.
