---
title: 2.1 Por qué un almacén masivo
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.1. Por qué un almacén masivo

!!! info "Ruta de estudio"
    **Esencial:** relacionar capacidad, rendimiento y continuidad con las necesidades del hotel; distinguir guardar datos, interpretarlos y procesarlos.

    **Práctica guiada:** justificar una mejora a partir del crecimiento del histórico y del tiempo disponible para el informe. En este apartado trabajamos con supuestos y cálculos sencillos; la instalación comienza en 2.2.

    **Ampliación:** comparar qué cambia al conservar varias copias del histórico. Su detalle adicional solo se exige si el profesor lo anuncia antes (véase [cómo trabajar la unidad](index.md#como-trabajar-la-unidad)).

## El hotel necesita seguir cumpliendo el plazo

En la [UT1](../ut1/index.md) construisteis un informe con datos integrados y comprobados. La [transición de los 500 GB](../ut1/transicion-ut2.md) plantea qué ocurre cuando crece el histórico. Ahora necesitamos justificar cómo conservar esos datos y utilizarlos sin que el crecimiento impida cumplir los requisitos del [grupo hotelero de Cantabria](../ut1/caso-hotel.md).

Recepción registra reservas, mantenimiento recibe medidas de sensores y finanzas registra cobros. Las **23:00 marcan el corte de negocio**; gerencia necesita el informe de ese cierre a las **8:00 del día siguiente**. En una noche sin cambio de hora hay nueve horas entre ambos momentos, pero dentro de ese margen deben caber la preparación, el procesamiento, la validación y la publicación del resultado. Si los datos llegan tarde o el trabajo empieza después, queda menos tiempo.

Una máquina puede ser suficiente mientras cumpla los requisitos. El problema aparece si el histórico ya no cabe, las consultas compiten con las cargas o una avería impide entregar el informe. Que un fichero no abra en Excel solo demuestra un límite de esa herramienta: para decidir si necesitamos más recursos hay que estudiar el proceso completo.

En este apartado, **sistema de almacenamiento masivo** designa una solución para conservar y dar acceso a grandes volúmenes de datos, con mecanismos de organización, protección y crecimiento. Trabaja con herramientas de procesamiento; guardar los datos y calcular sobre ellos son funciones distintas. La expresión no identifica un producto concreto ni un volumen mínimo universal.

## Tres necesidades que debemos medir

| Necesidad | Qué debemos averiguar | Ejemplo del hotel |
| --- | --- | --- |
| **Capacidad** | Cuánto ocupan los datos, cuánto crecen y qué espacio adicional necesitamos. | Histórico, índices, copias y archivos temporales deben caber durante el procesamiento. |
| **Rendimiento** | Cuánto tarda cada fase y qué recurso limita el trabajo. | El disco tiene espacio, pero el informe termina después de las 8:00. |
| **Continuidad** | Qué ocurre ante un fallo, cuánto tarda la recuperación y qué datos podrían perderse. | Una avería durante la madrugada obliga a recuperar datos o repetir parte del trabajo. |

**Ejemplo de capacidad.** Supongamos, solo para el ejercicio, que se conservan **20 GB nuevos al día durante 365 días**. Son `20 × 365 = 7.300 GB`, es decir, **7,3 TB decimales** de datos nuevos antes de compresión o copias. A esa cifra se añade el histórico previo que se mantenga y el espacio auxiliar. El cálculo corresponde a los primeros 365 días; si después se eliminan datos al vencer su plazo de conservación, no implica añadir otros 7,3 TB netos cada año. Es una estimación didáctica, no una medición real del hotel ni una obligación de leer todo el histórico cada noche.

**Ejemplo de rendimiento.** Si preparar, procesar, validar y publicar un cierre requiere once horas desde las 23:00, el resultado llegaría a las 10:00 en una noche sin cambio de hora. Más espacio libre no resuelve por sí solo ese retraso: primero debemos localizar la fase que consume el tiempo.

**Ejemplo de continuidad.** Si un disco falla a las 3:00, no basta con saber que existe una copia. Debemos comprobar cuánto tarda la recuperación, qué parte del trabajo hay que repetir y si queda tiempo para entregar el informe a las 8:00. Conservar los datos, recuperar el servicio y cumplir el plazo son comprobaciones diferentes.

El criterio **a)** del [RA2](ra2.md) se trabaja justificando estas necesidades y su relación con los datos y las operaciones. La elección de tecnología viene después del diagnóstico.

## Datos diferentes, usos diferentes

Ya sabemos cuánto crecen los datos y cuándo necesitamos el resultado. Ahora debemos concretar qué operaciones realizaremos: no se accede del mismo modo a una fotografía que a un histórico de reservas.

La variedad estudiada en la UT1 sigue presente. **El formato y la consulta se consideran juntos:** guardar una foto, localizar una reserva y recorrer un año de cobros exigen accesos distintos.

| Datos y necesidad | Posible organización | Qué debe aportar el procesamiento |
| --- | --- | --- |
| Ficheros CSV o Parquet de reservas para un resumen histórico. | Un almacén de ficheros; en la UT2 practicaremos con [HDFS](hdfs.md), el sistema de ficheros distribuido de Hadoop. | Leer los campos necesarios, aplicar filtros y obtener totales correctos. |
| Documentos JSON de sensores o reservas para consultar campos concretos. | Conservar el original en ficheros y, si las consultas lo justifican, utilizar una base documental como [MongoDB](mongodb.md). | Interpretar los campos, validar sus tipos y ejecutar las consultas. |
| Fotos de habitaciones que deben conservarse y localizarse. | Un almacén de objetos o de ficheros, con referencias y metadatos en una base de datos. | Buscar por hotel, habitación o fecha; analizar la imagen requiere otro programa. |

HDFS conserva los bytes de un fichero, pero no reconoce por sí mismo qué muestra una fotografía. MongoDB permite consultar campos de documentos, pero recibir JSON no obliga a elegir esa base. En [2.5](nosql.md) compararemos también modelos para relaciones entre datos y para accesos por clave, como una caché de sesión.

En el diseño del caso, el programa de reservas y la base relacional siguen atendiendo las operaciones del hotel; las copias para análisis alimentan el histórico. Se mantiene así la separación de la [UT1 entre operar e informar](../ut1/almacenamiento.md). Esta elección depende de consultas y garantías, no de que un modelo sea siempre superior a otro.

## Procesar cerca de los datos puede reducir transferencias

Volvamos al histórico de **500 GB**. Descargarlo completo al portátil añade una transferencia y necesita espacio local. Leerlo por bloques desde la red evita guardar una copia completa, pero sigue transfiriendo los datos que se leen. El límite puede estar en la red, el disco, la interpretación del formato o el cálculo: hay que medirlo.

Si los datos ya están repartidos en un clúster, una estrategia es ejecutar tareas cerca de los bloques que necesitan y combinar después sus resultados. Para aprender cómo se divide y reúne un cálculo, utilizaremos una operación más sencilla que el informe de cobros de Pentaho: sumar noches reservadas por hotel. Este resultado no representa un importe cobrado ni un porcentaje de ocupación. El recorrido sería:

1. Cada tarea **map** lee una parte de las reservas y emite un par `(hotel, noches)` por reserva. Por ejemplo, dos reservas de Laredo con 3 y 2 noches producen `(Laredo, 3)` y `(Laredo, 2)`; el mapper todavía no las suma.
2. El sistema agrupa los pares por hotel durante el **shuffle**, de modo que los valores de una misma clave lleguen al mismo reducer.
3. El **reducer** suma las noches de cada hotel: en el ejemplo, Laredo obtiene 5. Después comprobamos los totales con un cálculo independiente sobre el mismo CSV.

Como optimización, algunos trabajos pueden sumar valores parciales antes de enviarlos por la red mediante un **combiner**, si la operación lo permite. Es opcional y no lo configuramos en esta práctica: el recorrido básico es emitir pares, agruparlos y sumar sus valores.

Este es un anticipo de [MapReduce en 2.4](computacion-distribuida.md). **HDFS almacena los bloques; el motor de procesamiento realiza el cálculo.** La [arquitectura de HDFS](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html) facilita acercar las aplicaciones a sus datos, pero todavía hay transferencias para distribuir datos, comunicar tareas o reunir resultados.

La mejora depende del trabajo y de los recursos. Con pocos datos, la coordinación puede costar más tiempo que el cálculo local. Tampoco todas las bases NoSQL ejecutan sus consultas de esta manera. Para demostrar una mejora compararemos el mismo trabajo y verificaremos tanto su tiempo como su resultado.

## Qué debe ocurrir cuando falla un componente

Reducir el tiempo de cálculo no basta: también necesitamos saber qué ocurrirá si una pieza deja de funcionar durante la noche. Imaginad que un disco falla durante el cálculo nocturno. Si la única copia estaba allí, habrá que recuperarla de otra fuente. La **replicación** mantiene copias de los datos en distintos nodos para poder acceder a otra copia ante ciertos fallos. Su utilidad depende de dónde estén esas copias y de que los servicios necesarios sigan disponibles.

Replicar y repartir tienen finalidades distintas: **replicar conserva copias; particionar distribuye partes del conjunto**. Pueden combinarse. Repartir datos sin copias no basta para protegerlos de la pérdida de un nodo.

También deben protegerse los componentes que coordinan el sistema. En [2.3](hdfs.md) veremos que tener varios nodos con datos no elimina por sí solo el posible fallo del coordinador. En [2.8](replicas-shards.md) probaremos cómo MongoDB elige un nuevo servidor encargado de aceptar escrituras cuando la configuración y los miembros disponibles lo permiten.

Una **copia de seguridad** permite recuperar datos de un estado anterior; hay que comprobar que se puede restaurar. Una réplica puede propagar un borrado equivocado, por lo que no sustituye a esa protección. Un NAS —almacenamiento accesible por red— también puede incorporar redundancia: su respuesta ante fallos depende de la configuración.

En el aula, varios contenedores en un mismo ordenador permiten estudiar fallos de procesos, pero no protegen frente a perder ese ordenador. Las conclusiones deben indicar siempre **qué fallo se ha probado y qué configuración lo ha soportado**.

## Conservar hoy para responder nuevas preguntas

Podemos conservar registros de reservas antes de conocer todos los informes que necesitaremos. Más adelante, otro programa puede interpretarlos para una consulta nueva. Aplicar una estructura al consultar se conoce como **esquema al leer**. Es una forma de trabajar los usos posteriores de los datos del criterio **d)**, no una obligación de guardar todo sin reglas.

También podemos reutilizar tablas ya preparadas o documentos validados. Lo decisivo es conservar los datos necesarios, su significado y una forma adecuada de consultarlos; los usos futuros no dependen exclusivamente del esquema al leer.

Para reutilizar el histórico necesitamos metadatos: origen, fecha de extracción, formato, versión y significado de los campos. Dos fuentes distintas pueden utilizar el nombre `importe` para conceptos diferentes, como el precio previsto o el cobro confirmado; también pueden llamar `fecha` a la de reserva, estancia o pago. En cada conjunto de datos debemos respetar el significado definido para sus campos y comprobarlo antes de relacionar fuentes. Una suma técnicamente correcta puede producir un informe equivocado si confundimos esos significados.

La conservación requiere capacidad, permisos, calidad y plazos definidos. Crecer puede implicar ampliar una máquina o añadir nodos, pero debemos comprobar qué mejora aporta cada recurso y cuánto cuesta administrarlo. Añadir almacenamiento no garantiza acelerar un cálculo; añadir copias consume espacio y no equivale a repartir la carga de escritura. Estas decisiones se desarrollan en 2.2–2.4 y 2.8.

## Qué debéis poder explicar antes de pasar al 2.2

La conclusión debe relacionar **datos, operaciones, plazo y respuesta ante fallos**. No basta con afirmar que el hotel tiene muchos datos o nombrar una herramienta. En este apartado justificamos el sistema; las pruebas de distribución, tolerancia y crecimiento llegarán en los laboratorios posteriores.

!!! success "Idea clave"
    Un sistema de almacenamiento debe conservar y facilitar el acceso a los datos que necesitamos, con capacidad y protección suficientes. Las herramientas de procesamiento deben obtener resultados correctos dentro del plazo. Elegimos y ampliamos ambos a partir de medidas.

En [2.2 Ecosistema Hadoop](ecosistema.md) separaremos las piezas que almacenan los ficheros, gestionan los recursos y ejecutan el trabajo. Esa separación permite comprender qué componente responde a cada necesidad del hotel.

## Actividades

Aplicad las ideas al caso hotelero y justificad las respuestas con vuestras palabras. No hace falta instalar herramientas ni descargar 500 GB. Las entregas evaluables y sus condiciones se concretan en Moodle.

### Práctica guiada: justificar el siguiente paso

Trabajad con estos **supuestos del ejercicio**, sin instalar herramientas: llegan 20 GB nuevos al día y conservamos todos los recibidos durante los primeros 365 días. El proceso nocturno completo tarda once horas desde las 23:00, en una noche sin cambio de hora. Solo sabemos que dispone de espacio para los datos actuales; todavía no conocemos su cuello de botella.

1. Calculad cuánto espacio ocupan los datos nuevos al terminar esos 365 días, antes de copias y compresión. Indicad qué espacio queda fuera de esa cifra y qué dato falta para saber cuánto almacenamiento habría que añadir al equipo.
2. Determinad a qué hora terminaría el proceso y si cumple el plazo de las 8:00.
3. Anotad qué medir antes de decidir entre optimizar el procedimiento, ampliar la máquina o repartir el trabajo.
4. Explicad qué necesitaríais para continuar ante la pérdida de un disco y qué protección permitiría recuperar un borrado equivocado.
5. Elegid un dato del hotel y proponed una consulta futura. Identificad los metadatos que necesitaríais para interpretarlo correctamente.

Recoged la respuesta en vuestra hoja de decisiones: **problema → evidencia disponible → información que falta → propuesta condicionada → comprobación**. Las condiciones de entrega se concretan en Moodle.

Utilizad una fila por cada necesidad que analicéis:

| Problema | Evidencia disponible | Información que falta | Propuesta condicionada | Comprobación |
| --- | --- | --- | --- | --- |
| ¿Qué requisito no se cumple o podría incumplirse? | ¿Qué dato del supuesto lo indica? | ¿Qué habría que medir o averiguar? | ¿Qué cambio proponéis y bajo qué condición? | ¿Cómo verificaríais el resultado y la mejora? |


??? success "Orientación para comprobar la respuesta"
    El crecimiento es de **7,3 TB decimales**, sin contar histórico previo, índices, copias ni espacio de trabajo. Para calcular cuánto almacenamiento hay que añadir también necesitamos conocer el espacio libre utilizable. Once horas desde las 23:00 sitúan el final a las **10:00**, dos horas después del plazo en el supuesto indicado.

    Antes de elegir recursos, medid tiempos por fase, bytes realmente leídos, uso de CPU y memoria, tasas de disco y red y tareas concurrentes. Una propuesta válida explica qué observación justificaría el cambio y cómo se comprobaría el resultado.

    Para la pérdida de un disco, la continuidad depende de copias accesibles y servicios capaces de utilizarlas; deben probarse la interrupción y la recuperación. Para un borrado propagado, hace falta una versión recuperable anterior. Los metadatos de la consulta deben aclarar el significado de campos, unidades y periodo.

??? info "Ampliación: el coste de mantener copias"
    Si esos 7,3 TB se almacenaran con **tres copias completas en total**, ocuparían aproximadamente **21,9 TB** antes de compresión, metadatos y espacio auxiliar. La capacidad física dedicada a esas copias no representa 21,9 TB de datos distintos. Las copias de seguridad deben planificarse aparte.

### Aplicar y explicar

6. **Guardar, interpretar y calcular.** El hotel conserva un CSV de reservas y fotografías de habitaciones. Explicad qué aporta el almacenamiento en cada caso, qué metadatos permiten localizar los datos y qué programa u operación hace falta para obtener información de su contenido. ¿Guardar una foto en HDFS demuestra que el sistema reconoce la habitación?
7. **Acercar el cálculo.** Comparad descargar todo el histórico al portátil, leerlo por bloques desde la red y ejecutar tareas cerca de los datos ya repartidos. Indicad qué se transfiere y qué recursos medir en cada alternativa. No elijáis una ganadora sin explicar las condiciones. Para comparar tiempos, mantened el mismo trabajo y comprobad el resultado.
8. **Recuperar no es necesariamente llegar a tiempo.** Un disco falla a las 3:00. En este supuesto, restaurar tarda dos horas y repetir el trabajo completo requiere cuatro horas más. No hay cambio de hora ni otras demoras. ¿A qué hora terminaría? ¿Se han recuperado los datos? ¿Se cumple el plazo de las 8:00? Explicad qué mejora investigaríais y cómo la comprobaríais.
9. **Qué demuestra el laboratorio.** Tres contenedores mantienen réplicas en un mismo portátil. Se detiene uno y los otros siguen atendiendo consultas. Explicad qué fallo se ha probado, qué evidencia guardaríais y qué ocurriría si se apaga el portátil. Distinguid lo observado de lo que necesitaría otra prueba.

??? success "Orientaciones para revisar las actividades"
    **6.** Almacenar conserva y permite acceder a los archivos; un lector interpreta el CSV y un programa calcula los totales. Las referencias y metadatos permiten localizar fotos; reconocer su contenido requiere una herramienta adicional.

    **7.** Descargar necesita transferencia y espacio para la copia completa. Leer por bloques reduce la necesidad de espacio local, pero sigue usando la red. Ejecutar cerca de los datos puede reducir transferencias de entrada, aunque mantiene costes de coordinación y comunicación. La elección exige medir y contrastar resultados equivalentes.

    **8.** La restauración termina a las 5:00 y el trabajo a las 9:00: se recuperan los datos, pero se incumple el plazo por una hora. Podrían estudiarse una recuperación más rápida o la reanudación desde un punto comprobado, si el procedimiento lo permite. Habría que probar tanto el tiempo como la corrección del resultado.

    **9.** Se observa la respuesta ante la parada de un proceso en esa configuración. Registrad el estado inicial, la parada y las consultas posteriores. Los contenedores comparten el ordenador: esta prueba no demuestra continuidad ante la pérdida del portátil ni sustituye a comprobar una restauración.

## Autoevaluación del 2.1

Diez preguntas (A–D, **una** correcta) sobre los conceptos del apartado. No puntúan en Moodle. En cada pregunta, **Comprobar respuesta** muestra si habéis acertado y explica el motivo. Podéis repetir el test; antes, revisad el apartado enlazado y explicad por qué descartaríais las otras opciones.

<div class="dwec-quiz" data-dwec-quiz data-src="../../assets/quizzes/ut2-2-1.json"></div>
