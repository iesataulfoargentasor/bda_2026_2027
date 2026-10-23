---
title: "U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema"
tags:
  - Big Data
  - BDA
  - RA2
---

# U.T. 2. Gestión de sistemas de almacenamiento y su ecosistema

El título sigue el **[RA2](ra2.md)**: *gestiona sistemas de almacenamiento y el amplio ecosistema alrededor de ellos, facilitando el procesamiento de grandes cantidades de datos, sin fallos y de forma rápida*.

En esta unidad, «sin fallos» significa estudiar y probar la respuesta del sistema ante **determinados fallos**, con sus condiciones y límites. La rapidez también se comprueba: depende de los datos, los recursos y el trabajo que se realiza.

## De dónde venimos y qué cambia

En la [UT1](../ut1/index.md) diseñasteis una solución, elegisteis almacenamiento y formatos, integrasteis datos y construisteis un informe comprobado con [Pentaho](../ut1/tarea-clase.md). Seguimos con el mismo **[grupo hotelero de Cantabria](../ut1/caso-hotel.md)**: recepción registra operaciones, finanzas cierra a las **23:00** y gerencia necesita el informe del cierre de ayer a las **8:00**.

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

El recorrido tiene **dos bloques de trabajo con prácticas relacionadas**:

- **2.1–2.4: almacenar ficheros y repartir el cálculo.** Primero identificamos las necesidades del hotel (2.1) y conocemos el ecosistema Hadoop y su entorno de prácticas (2.2). Después estudiamos HDFS, el sistema que guarda los ficheros en bloques (2.3), y profundizamos en cómo MapReduce divide y reúne el cálculo, con recursos gestionados por YARN (2.4). El ejemplo común calcula noches reservadas por hotel.
- **2.5–2.9: organizar, consultar y gestionar documentos.** Comparamos las familias NoSQL (2.5), practicamos consultas y cambios en MongoDB (2.6) y diseñamos documentos según las operaciones que necesita el hotel (2.7). Después distinguimos replicación —conservar copias— y particionado —repartir datos— (2.8), y accedemos al sistema desde Python (2.9).

Ambos bloques responden a necesidades del mismo caso hotelero y utilizan entornos independientes. Hive y Spark aparecen como herramientas del ecosistema; la replicación y el particionado son mecanismos que estudiamos en los sistemas. Cada elemento debe relacionarse con la función que aporta.

## Cómo trabajar la unidad

Leed los apartados **en orden**, empezando por el caso hotelero y la transición de los 500 GB. Identificad primero el problema, explicad los conceptos con vuestras palabras y aplicadlos en la práctica. Mantened una hoja de decisiones: **problema, entrada, resultado esperado, recursos y comprobación**.

El recorrido común reúne los conceptos y las prácticas guiadas de los apartados. Las actividades señaladas como **opcionales, extras o ampliaciones** permiten profundizar; su ejecución o detalle adicional solo se exige si el profesor lo anuncia antes. Las entregas evaluables y sus condiciones se concretan en Moodle. Las preguntas de autoevaluación sirven para repasar y no fijan por sí solas el contenido de una prueba calificada.

Necesitáis los fundamentos de la UT1, manejo básico de terminal y Python: variables, bucles, funciones y lectura de archivos. Utilizad los materiales y el entorno del módulo; los requisitos de instalación se detallan en [2.2](ecosistema.md) y [2.6](mongodb.md). Antes de ejecutar un comando, identificad si corresponde al equipo anfitrión, al contenedor, a la consola de MongoDB o a Python. Seguid las indicaciones de arranque y parada al cambiar de práctica, especialmente en [2.8](replicas-shards.md).

## Qué vais a trabajar

La tabla recoge las relaciones principales con los criterios del [RA2](ra2.md). Estudiar un concepto y demostrarlo en el laboratorio requieren evidencias diferentes.

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
| [Autoevaluación](autoevaluacion.md) | — | Repasar la unidad y revisar la explicación de los errores. No puntúa en Moodle. |

En **2.9**, ejecutar una agregación en el servidor permite practicar procesamiento, pero **no demuestra por sí solo computación distribuida**. La evidencia del criterio **b)** se trabaja en 2.2 y 2.4, indicando qué distribución permite observar el entorno disponible.

## Prácticas y comprobaciones

Trabajamos con conjuntos pequeños para poder revisar los resultados. El volumen del escenario empresarial justifica las preguntas de la unidad; los ficheros de aula permiten aprender los procedimientos. Las pruebas de rendimiento requieren los datos y condiciones indicados en 2.4.

| Práctica | Datos iniciales | Qué comprobáis |
| --- | --- | --- |
| Ficheros y cálculo en Hadoop (2.2–2.4) | CSV de 20 reservas, 62 noches | Rutas, bloques, tareas y totales de noches reservadas por hotel. |
| Consultas en MongoDB (2.6 y 2.9) | JSONL de 15 reservas y 6 opiniones | Filtros, listas de valores, recorridos de resultados y agregaciones. |
| Escrituras en MongoDB (2.6 y 2.9) | Copia de las colecciones de consulta | Altas, cambios y borrados, conservando los datos originales para las consultas. |
| Modelado documental (2.7) | Necesidades y documentos de ejemplo del hotel | Organización de los datos, evolución del esquema y reglas de validación. |
| Conjunto de réplicas (2.8) | Documento de prueba identificado | Elección de un nuevo primario, lectura de otras copias y recuperación. |
| Particionado, laboratorio opcional (2.8) | 15 reservas importadas en ese entorno | Reparto y movimiento de datos sin alterar los resultados de las consultas. |
| Transacciones, práctica opcional (2.9) | Reserva y una plaza de parking, sobre un conjunto de réplicas | Confirmación conjunta de los cambios o rechazo sin cambios parciales. |
| Aplicación web, extra opcional (2.9) | Datos originales de consulta | Coincidencia entre los resultados del programa y los mostrados en la web. |

Los CSV y JSONL son **conjuntos diferentes**: no tienen por qué producir los mismos totales. Seguid el fichero y la base indicados en cada práctica. Interpretad también el alcance: sumar noches reservadas no equivale a calcular un porcentaje de ocupación ni un importe cobrado.

!!! info "Qué permite demostrar el entorno de aula"
    El entorno básico de Hadoop utiliza un único nodo de datos y un único nodo de ejecución en un ordenador. Permite observar sus funciones y las tareas, pero probar la tolerancia por réplica requiere más nodos de datos y copias efectivas. Varios contenedores en un ordenador tampoco demuestran resistencia ante la pérdida de ese ordenador ni aceleración entre máquinas físicas. En cada prueba, distinguid lo observado de lo esperado por diseño.

En cada práctica conservad **entrada, configuración, operación, resultado y explicación**. Una captura sin interpretación no permite saber si el resultado es correcto. Contrastad recuentos, totales y reglas de negocio; al probar un fallo, registrad el estado inicial, la interrupción y la recuperación. Si el entorno no permite demostrar una propiedad, explicad la limitación y qué prueba adicional necesitaríais.

Terminad con la [autoevaluación](autoevaluacion.md) y revisad los criterios del [RA2](ra2.md). Debéis poder explicar a un compañero qué necesidad resuelve cada sistema, qué habéis comprobado y bajo qué condiciones se mantiene el resultado.
