---
title: "U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema"
tags:
  - Big Data
  - BDA
  - RA2
---

# U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema

El hotel ya dispone de un procedimiento para preparar y comprobar sus informes. Ahora queremos estudiar qué sucede cuando aumenta el histórico, coinciden varios trabajos o un componente deja de funcionar. En esta unidad aprenderemos a gestionar los sistemas que almacenan y procesan esos datos, comprobando qué pueden hacer y bajo qué condiciones.

Este trabajo desarrolla el **[RA2](ra2.md)**: *gestiona sistemas de almacenamiento y el amplio ecosistema alrededor de ellos, facilitando el procesamiento de grandes cantidades de datos, sin fallos y de forma rápida*.

En esta unidad, «sin fallos» significa estudiar y probar la respuesta del sistema ante **determinados fallos**, con sus condiciones y límites. La rapidez también se comprueba: depende de los datos, los recursos y el trabajo que se realiza.

## De dónde venimos y qué cambia

En la [UT1](../ut1/index.md) diseñasteis una solución, elegisteis almacenamiento y formatos, integrasteis datos y construisteis un informe comprobado con [Pentaho](../ut1/tarea-clase.md). Seguimos con el mismo **[grupo hotelero de Cantabria](../ut1/caso-hotel.md)**: recepción registra operaciones, finanzas cierra a las **23:00** y gerencia necesita el informe de ese cierre a las **8:00 del día siguiente**.

En la práctica integradora aprendisteis a relacionar reservas y cobros, validar el resultado y controlar la publicación. Esas comprobaciones siguen siendo necesarias. Ahora ampliamos la pregunta: además de obtener un resultado correcto, ¿qué recursos y mecanismos necesita el sistema para seguir prestando el servicio cuando cambian las condiciones?

La [transición desde la UT1: 500 GB y un portátil](../ut1/transicion-ut2.md) plantea el crecimiento del histórico. La UT2 amplía ese escenario: ¿qué cambia si seguimos acumulando reservas, cobros, registros de sensores y fotos hasta alcanzar varios terabytes? Debemos comprobar si podemos conservarlos, procesarlos dentro del plazo y recuperar el servicio ante un fallo.

**El volumen por sí solo no obliga a utilizar un clúster.** Antes de ampliar o repartir recursos, hay que medir capacidad, tiempos y carga de trabajo. Si el cierre supera el plazo, estudiaremos qué lo limita y qué cambio puede ayudar. Hadoop y MongoDB son las tecnologías elegidas para practicar estas decisiones en el módulo.

## Qué aprenderéis a comprobar

Al terminar la unidad, debéis poder explicar y apoyar con evidencias:

- **Dónde guardar los datos y cómo utilizarlos.** Conservar un fichero no significa que el sistema interprete automáticamente su contenido; hacen falta formatos, metadatos y programas adecuados.
- **Cómo repartir un cálculo y comprobar su resultado.** Dividir el trabajo exige reunir correctamente los resultados parciales y medir si compensa.
- **Qué sucede cuando falla un componente.** Identificar qué servicio se interrumpe, qué datos siguen disponibles y cómo se recupera el sistema.
- **Cómo conservar datos para nuevas consultas.** Poder darles otro uso más adelante exige mantener su significado y organización.
- **Qué aporta añadir recursos.** Distinguir más capacidad, más posibilidades de procesamiento y mayor disponibilidad, según la configuración.

## Cómo se relacionan los apartados

El hotel necesita tanto revisar su histórico como consultar y actualizar información concreta. Por ejemplo, dirección puede pedir un resumen de muchas reservas, mientras recepción necesita recuperar una reserva y modificar sus datos. Estas necesidades nos permiten organizar **dos bloques de trabajo relacionados**:

| Necesidad que utilizamos como ejemplo | Bloque de la unidad |
| --- | --- |
| Conservar archivos históricos y recorrer muchas reservas para obtener un resumen | **2.1–2.4:** almacenamiento de ficheros y procesamiento con Hadoop. |
| Organizar reservas y opiniones, consultarlas y modificar información concreta | **2.5–2.9:** bases de datos documentales, gestión y acceso desde Python. |

Son ejemplos para aprender las funciones de cada sistema, no usos exclusivos de esas tecnologías. Antes de recorrer los apartados, situad cuatro nombres:

- **HDFS** es el sistema de ficheros de Hadoop: almacena archivos divididos en bloques que pueden repartirse entre nodos.
- **MapReduce** organiza un cálculo en tareas y reúne sus resultados parciales.
- **YARN** administra los recursos disponibles para ejecutar los trabajos.
- **MongoDB** almacena y permite consultar y modificar documentos: registros con campos que también pueden contener listas y estructuras anidadas.

Con esas funciones situadas, el recorrido será el siguiente:

- **2.1–2.4: almacenar ficheros y repartir el cálculo.** Primero identificamos las necesidades del hotel (2.1) y conocemos el ecosistema Hadoop y su entorno de prácticas (2.2). Después estudiamos HDFS, el sistema que guarda los ficheros en bloques (2.3), y profundizamos en cómo MapReduce divide y reúne el cálculo, con recursos gestionados por YARN (2.4). El ejemplo común calcula noches reservadas por hotel.
- **2.5–2.9: organizar, consultar y gestionar documentos.** Comparamos las familias NoSQL (2.5), practicamos consultas y cambios en MongoDB (2.6) y diseñamos documentos según las operaciones que necesita el hotel (2.7). Después estudiamos cómo mantener copias de los datos y cómo repartirlos en partes (2.8), y accedemos al sistema desde Python (2.9).

Seguimos con el mismo hotel, pero **no reconstruimos directamente el informe de cobros de Pentaho**. En Hadoop empezamos con una pregunta más sencilla: cuántas noches reservadas aparecen por hotel. Así podemos concentrarnos en cómo se divide y reúne el trabajo y comprobar los resultados. En MongoDB utilizaremos reservas y opiniones para aprender a consultar, actualizar y organizar documentos. Cada práctica indicará sus datos y el significado del resultado.

La pregunta común a ambos bloques es: **¿qué cambia cuando crecen los datos, aumenta el trabajo o falla un componente?** Compararemos la organización, los recursos y los mecanismos de cada sistema. Los laboratorios utilizan entornos independientes; completar el primer bloque no exige trasladar automáticamente sus salidas al segundo.

La **replicación** mantiene copias de los datos en varios miembros del sistema, y el **particionado** reparte los datos en partes. Pueden combinarse: cada parte puede tener sus propias réplicas. Replicar tampoco sustituye a una copia de seguridad, porque puede propagar borrados o cambios incorrectos.

Hive y Spark aparecen como herramientas del ecosistema. A medida que avancéis, relacionad cada nombre con la función que aporta: guardar, ejecutar, gestionar recursos, consultar o facilitar la recuperación.

## Cómo trabajar la unidad

Leed los apartados **en orden**, empezando por el caso hotelero y la transición de los 500 GB. Identificad primero el problema, explicad los conceptos con vuestras palabras y aplicadlos en la práctica. Mantened una hoja de decisiones: **problema, entrada, resultado esperado, recursos y comprobación**.

El recorrido común reúne los conceptos y las prácticas guiadas de los apartados. Las actividades señaladas como **opcionales, extras o ampliaciones** permiten profundizar; su ejecución o detalle adicional solo se exige si el profesor lo anuncia antes. Las entregas evaluables y sus condiciones se concretan en Moodle. Las preguntas de autoevaluación sirven para repasar y no fijan por sí solas el contenido de una prueba calificada.

**Son comunes también las observaciones de los criterios b) y e)**: comparación de uno y dos trabajadores en [2.4](computacion-distribuida.md#evidencia-comun-del-criterio-b-comparar-uno-y-dos-trabajadores) e incorporación de shards en [2.8](replicas-shards.md#evidencia-comun-del-criterio-e-observar-la-ampliacion). Pueden hacerse mediante demostración docente cuando el equipo del alumno no permita ejecutarlas. Cada alumno entrega su interpretación y las evidencias indicadas en el [RA2](ra2.md#evidencias-minimas-comunes-de-b-y-e); la instalación individual del laboratorio opcional no es obligatoria.

Necesitáis los fundamentos de la UT1, manejo básico de terminal y Python: variables, bucles, funciones y lectura de archivos. Utilizad los materiales y el entorno del módulo; los requisitos de instalación se detallan en [2.2](ecosistema.md) y [2.6](mongodb.md). Antes de ejecutar un comando, identificad si corresponde al equipo anfitrión, al contenedor, a la consola de MongoDB o a Python. Seguid las indicaciones de arranque y parada al cambiar de práctica, especialmente en [2.8](replicas-shards.md).

<span id="que-vais-a-trabajar"></span>

## Mapa de apartados y criterios de evaluación

Utilizad esta tabla para localizar dónde se trabaja cada criterio del [RA2](ra2.md) y qué aprendizaje aporta cada apartado. Estudiar un concepto y demostrarlo en el laboratorio requieren evidencias diferentes.

| Apartado | Criterio | Qué os lleváis |
| --- | --- | --- |
| [Transición desde la UT1: 500 GB](../ut1/transicion-ut2.md) | Puente hacia **RA2** | Justificar qué recursos y procedimiento necesita un histórico creciente. |
| [2.1 Por qué un almacén masivo](por-que-almacenamiento.md) | **a)** | Relacionar volumen, variedad y plazo con las necesidades de almacenamiento y procesamiento. |
| [2.2 Ecosistema Hadoop](ecosistema.md) | **a)** / **b)** / **e)** | Distinguir almacenamiento, gestión de recursos y ejecución; poner en marcha un primer trabajo. |
| [2.3 HDFS](hdfs.md) | **a)** / **c)** / **d)** / **e)** | Guardar y recuperar ficheros, localizar sus bloques y explicar qué permiten sus réplicas y su ampliación. |
| [2.4 Computación distribuida](computacion-distribuida.md) | **b)** | Dividir un cálculo, contrastar los totales y medir el efecto de los recursos disponibles. |
| [2.5 Familias NoSQL](nosql.md) | **a)** / **c)** / **d)** / **e)** | Elegir un modelo según los datos, las consultas y las garantías necesarias. |
| [2.6 MongoDB](mongodb.md) | **a)** / **d)** | Consultar y modificar documentos, comprobando qué cambia y qué se conserva. |
| [2.7 Modelado documental](modelado.md) | **d)** | Diseñar documentos y reglas de validación según las operaciones del hotel y la evolución de sus datos. |
| [2.8 Réplicas y particiones](replicas-shards.md) | **c)** / **e)** | Probar la respuesta ante la caída de un miembro y razonar cómo repartir los datos para crecer. |
| [2.9 MongoDB y Python](pymongo.md) | **d)** / **c)**; apoyo a **b)** | Consultar, agregar y modificar desde Python; aplicar las opciones de acceso al conjunto de réplicas. |
| [Práctica Integradora de la UT2](practica-integradora.md) | **a–e** | Reunir el histórico del cierre y la recepción viva, con datos ficticios de cerca de 1 GB y pruebas de los cinco criterios. |
| [Autoevaluación](autoevaluacion.md) | — | Repasar la unidad y revisar la explicación de los errores. No puntúa en Moodle. |

En **2.9**, ejecutar una agregación en el servidor permite practicar procesamiento, pero **no demuestra por sí solo computación distribuida**. La evidencia del criterio **b)** se trabaja en 2.2 y 2.4, indicando qué distribución permite observar el entorno disponible.

## Prácticas y comprobaciones

En las prácticas guiadas trabajamos con conjuntos pequeños para poder revisar los resultados. El volumen del escenario empresarial justifica las preguntas de la unidad; los ficheros de aula permiten aprender los procedimientos. Las pruebas de rendimiento de estos apartados requieren los datos y condiciones indicados en 2.4. La [práctica integradora](practica-integradora.md) usa otro conjunto, ficticio y de cerca de 1 GB, con los cuatro hoteles del caso. No reutiliza los totales de la tabla siguiente.

| Práctica | Datos iniciales | Qué comprobáis |
| --- | --- | --- |
| Ficheros y cálculo en Hadoop (2.2–2.4) | CSV de 20 reservas, 62 noches | Rutas, bloques, tareas y totales de noches reservadas por hotel. |
| Consultas en MongoDB (2.6 y 2.9) | JSONL de 15 reservas y 6 opiniones | Filtros, listas de valores, recorridos de resultados y agregaciones. |
| Escrituras en MongoDB (2.6 y 2.9) | Copia de las colecciones de consulta | Altas, cambios y borrados, conservando los datos originales para las consultas. |
| Modelado documental (2.7) | Necesidades y documentos de ejemplo del hotel | Organización de los datos, evolución del esquema y reglas de validación. |
| Conjunto de réplicas (2.8) | Documento de prueba identificado | Elección de un nuevo primario, lectura de otras copias y recuperación. |
| Particionado: observación común; instalación individual opcional (2.8) | 15 reservas importadas en ese entorno | Reparto y movimiento de datos sin alterar los resultados de las consultas. |
| Transacciones, práctica opcional (2.9) | Reserva y una plaza de parking, sobre un conjunto de réplicas | Confirmación conjunta de los cambios o rechazo sin cambios parciales. |
| Aplicación web, extra opcional (2.9) | Datos originales de consulta | Coincidencia entre los resultados del programa y los mostrados en la web. |

Los CSV y JSONL son **conjuntos diferentes**: no tienen por qué producir los mismos totales. Seguid el fichero y la base indicados en cada práctica. Interpretad también el alcance: sumar noches reservadas no equivale a calcular un porcentaje de ocupación ni un importe cobrado.

!!! info "Qué permite demostrar el entorno de aula"
    El entorno básico de Hadoop utiliza un único nodo de datos y un único nodo de ejecución en un ordenador. Permite observar sus funciones y las tareas, pero probar la tolerancia por réplica requiere más nodos de datos y copias efectivas. Varios contenedores en un ordenador tampoco demuestran resistencia ante la pérdida de ese ordenador ni aceleración entre máquinas físicas. En cada prueba, distinguid lo observado de lo esperado por diseño.

Para observar el crecimiento del sistema, relacionad cada recurso añadido con lo que aporta: por ejemplo, capacidad de almacenamiento al incorporar un DataNode o capacidad de ejecución al añadir un trabajador. El laboratorio opcional de particionado ofrece otra forma de estudiarlo. La evidencia común del criterio **e)** se recoge mediante la secuencia de incorporación y reparto de 2.8, ejecutada por el alumno o demostrada por el profesor; explicar una ampliación prevista no equivale a haberla observado.

En cada práctica conservad **entrada, configuración, operación, resultado y explicación**. Una captura sin interpretación no permite saber si el resultado es correcto. Contrastad recuentos, totales y reglas de negocio; al probar un fallo, registrad el estado inicial, la interrupción y la recuperación. Si el entorno no permite demostrar una propiedad, explicad la limitación y qué prueba adicional necesitaríais.

Después del 2.9, cerrad la unidad con la [práctica integradora](practica-integradora.md). El repaso de conceptos sigue en la [autoevaluación](autoevaluacion.md); no sustituye a ese expediente. Revisad también los criterios del [RA2](ra2.md). Debéis poder explicar a un compañero qué necesidad resuelve cada sistema, qué habéis comprobado y bajo qué condiciones se mantiene el resultado.
