---
title: "Práctica integradora: el informe del hotel con Pentaho"
tags:
  - Big Data
  - BDA
  - RA1
  - Pentaho
---

# Práctica integradora: el informe del hotel con Pentaho

Esta práctica cierra la **UT1**. Vais a preparar una solución para el [grupo hotelero de Cantabria](caso-hotel.md): explicar qué datos necesitáis, procesarlos con Pentaho, comprobar el resultado y entregar un informe que dirección pueda interpretar sin abrir Spoon.

Los [talleres de 1.8](pentaho.md) son vuestra referencia técnica. Aquí debéis conectar lo aprendido y demostrar que el procedimiento funciona, también cuando se repite o falta una entrada. Cada alumno trabajará en un repositorio de su propia cuenta de GitHub y realizará una defensa individual ante el profesor. El trabajo se realizará durante las sesiones de aula, con seguimiento del profesor. Podéis contrastar dudas en clase, pero debéis identificar las ayudas recibidas y comprender todo lo que entregáis. Al finalizar cada sesión entregaréis el avance realizado, aunque todavía esté incompleto. La rúbrica de este apartado suma **10,00 puntos**; Moodle concretará las fechas y recogerá el enlace de entrega.

!!! info "Dos actividades con funciones diferentes"
    Esta práctica construye y comprueba una solución con datos pequeños. Después, la [transición a la UT2: 500 GB y un portátil](transicion-ut2.md) plantea qué revisaríamos al aumentar el volumen. No necesitáis Spark, nube ni una base de datos para completar esta práctica.

## Vídeo: qué hacer, cómo entregarlo y cómo se evalúa

Antes de empezar, mira esta guía del encargo del hotel: explica los paquetes personales A001–A015, los dos resultados, las validaciones y pruebas, las entregas de avances al finalizar cada sesión, la entrega final en GitHub y la rúbrica sobre **10,00 puntos**, incluidos los **2,00 puntos de la defensa individual**. **Duración: 19 minutos y 55 segundos.**

<video controls playsinline preload="metadata" poster="../../assets/ut1/practica-pentaho-portada.jpg" aria-label="Práctica integradora de Pentaho: trabajo, entrega en GitHub, rúbrica y defensa individual" style="width: 100%; max-width: 960px; height: auto; border-radius: 12px;">
  <source src="../../assets/ut1/practica-pentaho.mp4" type="video/mp4">
  Tu navegador no permite reproducir este vídeo. Puedes descargarlo en el enlace siguiente.
</video>

El vídeo incluye subtítulos visibles y narración con voz sintética en español. Esta versión incorpora los datos personalizados, el trabajo en el aula, los avances por sesión, la entrega en GitHub y la defensa individual. Complementa las instrucciones de los apartados 2, 9 y 10; consultad en Moodle las fechas de entrega.

[Descargar el vídeo](../assets/ut1/practica-pentaho.mp4) · [Leer la transcripción](../assets/ut1/practica-pentaho.txt) · [Descargar los subtítulos](../assets/ut1/practica-pentaho.es.srt)

## 1. El encargo de dirección

> «Necesito conocer el importe cobrado y el número de reservas cobradas por hotel y canal. Quiero recibir un CSV claro del cierre y saber qué reservas todavía no tienen un cobro asociado. El procedimiento debe poder repetirse y avisar si no puede generar el informe».

El informe principal responde a dirección. El listado de reservas sin cobro es un **control interno para revisar**, no una prueba de impago: una reserva podría tener un pago pendiente o un plazo de pago que estos archivos no describen.

!!! warning "Qué representan estos datos"
    Para esta práctica, suponemos que los tres archivos pertenecen a **un mismo cierre de aula ya seleccionado**. No tienen fechas para filtrar «ayer». Identificad el conjunto como `cierre_aula_01` y añadid en la explicación la fecha y hora de generación, sin presentarlas como fecha del cobro. Tampoco calculéis ocupación: faltan habitaciones disponibles y ocupadas por periodo.

### Reglas que debe cumplir la solución

1. Relacionar reservas y cobros por `id_reserva`; añadir el nombre del hotel mediante `id_hotel`.
2. Incluir en el informe principal solo reservas con cobro asociado.
3. Sumar **`cobrado`**, no el precio `importe` de la reserva.
4. Producir una fila por combinación de `hotel` y `canal`, con `n_reservas` y `cobrado_total`.
5. Conservar las reservas sin cobro en un listado separado, sin inventar importes ni descartarlas sin explicación.
6. Repetir la ejecución sobre las mismas entradas sin acumular filas en los archivos de salida.
7. No anunciar éxito ni publicar un resultado nuevo cuando una entrada requerida falta o el proceso falla.

## 2. Preparad el entorno y las entradas

Comprobad primero que funciona el [taller 0 de Pentaho](pentaho.md#taller-0-que-spoon-hable). Utilizad **Pentaho Data Integration Community 9.4.0.0-343**, la versión de los talleres, con el entorno Java indicado por el aula. Estos archivos se leen localmente: no necesitáis una base de datos, controladores JDBC, servicios de pago ni plugins adicionales.

| Archivo | Separador | Contenido esperado |
| --- | --- | --- |
| `reservas_pdi.csv` | Coma | 20 reservas; `id_reserva` único |
| `cobros_pdi.csv` | Punto y coma | 15 cobros; como máximo uno por reserva |
| `hoteles_pdi.csv` | Punto y coma | 5 hoteles; `id_hotel` único |

No reutilicéis los CSV de 1.6 o 1.7. Noja representa la ampliación del grupo que aparece en los talleres. Conservad los originales sin modificarlos y utilizad copias para las pruebas de fallo.

### Recibid vuestro paquete personal

El profesor asignará a cada uno de los **15 alumnos** un código diferente, de **A001 a A015**, y entregará su ZIP mediante Moodle o en el aula. Utilizad **solo el paquete que os haya asignado**; no descarguéis el de otro compañero ni sustituyáis sus archivos por los comunes del taller 1.8. Si todavía no lo tenéis o no podéis abrirlo, avisad al profesor antes de empezar.

Dentro encontraréis `entrada/reservas_pdi.csv`, `entrada/cobros_pdi.csv` y `entrada/hoteles_pdi.csv`, además de `asignacion.json`, que identifica vuestro código y las huellas de los originales. Copiad `entrada` a la raíz del repositorio y conservad allí también `asignacion.json`. Indicad vuestro código en el README. No tenéis que introducir nombres ni otros datos personales en los CSV.

Los paquetes mantienen los mismos campos, separadores y dificultad. Cambian algunos importes individuales de reservas con cobro y el orden de las filas; **se conservan todos los resultados de referencia**, incluido cada grupo del informe y el contenido del listado sin cobro. Por tanto, dos informes finales correctos pueden ser idénticos: eso no demuestra una copia. La elaboración personal se comprueba con los avances observados, las evidencias y la defensa individual. No se pide inventar diagramas distintos para aparentar diferencias.

Los archivos comunes de los talleres siguen disponibles como referencia: [reservas](../assets/practicas/reservas_pdi.csv), [cobros](../assets/practicas/cobros_pdi.csv) y [hoteles](../assets/practicas/hoteles_pdi.csv). **No son las entradas que debéis entregar en esta práctica.**

### Comprobación de los datos recibidos

Los tres CSV de vuestro paquete son los **únicos archivos de datos necesarios**. No tenéis que inventar ni buscar datos de clientes. Descomprimid el ZIP antes de abrir los archivos desde Pentaho.

1. Comprobad que los tres originales están en `entrada`, dentro de la copia local de vuestro repositorio, y que el código de `asignacion.json` coincide con el asignado por el profesor.
2. Abridlos con un editor de texto antes de importarlos: la primera línea debe ser la cabecera de campos, no código de una página web.
3. En **CSV file input**, activad la cabecera y seleccionad **UTF-8**. Indicad el separador de cada archivo según la tabla; no uséis la misma configuración para los tres.
4. Revisad los campos con la siguiente tabla. En los importes, estableced punto como símbolo decimal y dejad vacío el separador de miles. Para esta práctica pequeña podéis desactivar **Lazy conversion** y comprobar la conversión al leer.
5. Ejecutad una vista previa y después una lectura completa: deben aparecer **20, 15 y 5 filas de datos**, respectivamente, sin contar la cabecera ni producir errores de conversión.

| Archivo | Campos de tipo Integer | Campos de tipo String | Campos de tipo BigNumber |
| --- | --- | --- | --- |
| `reservas_pdi.csv` | `id_reserva`, `id_hotel`, `noches` | `canal` | `importe` |
| `cobros_pdi.csv` | `id_reserva` | `medio` | `cobrado` |
| `hoteles_pdi.csv` | `id_hotel`, `id_cadena` | `hotel`, `comarca` | Ninguno |

No hace falta utilizar `comarca`, `id_cadena` ni `medio` en los informes finales; conservadlos en los originales. Todos los identificadores de hotel tienen correspondencia y todos los cobros remiten a una reserva existente.

### Repositorio y rutas de trabajo

Cread en vuestra cuenta de GitHub un repositorio llamado **`bda-ut1-pentaho-hotel`**. Trabajad con una copia local: GitHub conserva y permite revisar los archivos, pero **no ejecuta Spoon ni Kitchen**. Podéis usar Git o GitHub Desktop para clonar, registrar y subir los cambios.

Organizadlo así:

```text
bda-ut1-pentaho-hotel/
├── README.md
├── .gitignore
├── asignacion.json # Código del paquete y huellas de los originales
├── entrada/       # Los tres CSV originales
├── procesos/      # Cuatro .ktr y un .kjb
├── temporal/      # Resultados provisionales; no se suben
├── salida/        # Los dos CSV finales comprobados
└── evidencias/    # Tabla de comprobaciones y pruebas comentadas
```

Añadid `/temporal/` a `.gitignore`. Git no conserva carpetas vacías: el README debe indicar que hay que crear `temporal` y `salida` antes de ejecutar. Subid los dos resultados finales de referencia, pero no la instalación de Pentaho, Java, archivos de respaldo ni credenciales.

Para evitar rutas propias de vuestro equipo, guardad todos los `.ktr` y el `.kjb` directamente en `procesos`. En las transformaciones, utilizad rutas como `${Internal.Transformation.Filename.Directory}/../entrada/reservas_pdi.csv` y `${Internal.Transformation.Filename.Directory}/../temporal/informe_hotel_canal.csv`. En el job, referenciad una transformación como `${Internal.Job.Filename.Directory}/informe_cobros.ktr`; para las carpetas de datos, emplead `${Internal.Job.Filename.Directory}/../entrada/` y las equivalentes de `temporal` y `salida`. Guardad el proceso antes de probar estas variables.

Registrad avances con mensajes que expliquen lo realizado, por ejemplo «Construyo el informe por hotel y canal» o «Compruebo el fallo por entrada ausente». Antes de entregar, descargad o clonad el repositorio en **otra carpeta**, cread las carpetas necesarias y comprobad que Kitchen puede ejecutarlo siguiendo solo vuestro README.

En **CSV file input**, revisad nombres, separadores y tipos antes de avanzar. Las claves deben tener el mismo tipo en las dos entradas de una unión. Para los importes, utilizad un tipo decimal adecuado, como **BigNumber**, configurando el punto decimal del origen. Una coma mal interpretada no se corrige al agrupar.

## 3. Diseñad antes de arrastrar pasos

Escribid una breve propuesta que responda a estas preguntas:

- ¿Qué necesita dirección y qué representa cada fila de entrada y de salida?
- ¿Dónde conservaréis originales, archivos provisionales e informes publicados?
- ¿Quién inicia la lectura? ¿Por qué encaja un proceso por lotes con este cierre?
- ¿Qué comprobaremos antes de entregar? ¿Qué sucederá al repetirlo o si falta un archivo?
- ¿Por qué CSV es adecuado para esta entrega? ¿Qué alternativa estudiaríais para un histórico grande consultado por columnas?

Dibujad el recorrido, por ejemplo:

```text
Reservas + cobros + hoteles
          ↓
Lectura y comprobación de tipos y claves
          ↓
Informe por hotel/canal + listado sin cobro (provisionales)
          ↓
Validación de los dos archivos
          ↓
Publicación en salida y registro del resultado
```

Relacionad vuestra propuesta con almacenamiento (1.3), procesamiento (1.4), arquitectura (1.5), ingesta (1.6) y formatos (1.7). No hace falta instalar esas tecnologías ni repetir las definiciones del tema: justificad las decisiones de esta solución.

## 4. Construid el informe de cobros

Guardad una transformación como `informe_cobros.ktr`. Podéis adaptar el taller 2, pero debéis explicar y verificar cada paso.

1. Leed reservas y cobros con sus separadores y tipos correctos.
2. Ordenad **ambas entradas** por `id_reserva` y configurad un **Merge join INNER**. Revisad explícitamente entrada izquierda, derecha y claves. La salida debe contener 15 filas.
3. Leed hoteles. Ordenad tanto el flujo anterior como hoteles por `id_hotel` y añadid otro **Merge join INNER**. Deben mantenerse las 15 filas y aparecer los nombres de hotel. Si faltara una correspondencia, no continuéis sin investigar.
4. Ordenad el resultado por `hotel` y `canal`. Configurad **Group by** con esos campos: `SUM(cobrado)` → `cobrado_total`; recuento de `id_reserva` → `n_reservas`.
5. Escribid `temporal/informe_hotel_canal.csv`, con cabecera, sin espacios de relleno y **sin añadir al contenido de ejecuciones anteriores**. Dejad las columnas en el orden `hotel;canal;n_reservas;cobrado_total`.

Usad punto y coma como separador de salida, UTF-8 e importes con punto decimal y dos decimales, sin separador de miles. Indicad en la explicación que los importes están en euros. Ordenad por hotel y canal para facilitar la revisión.

!!! tip "Por qué podemos contar las filas"
    En estos archivos hay como máximo un cobro por reserva. Si una reserva tuviera dos pagos, el cruce produciría dos filas: sumar cobros y contar reservas requerirían tratamientos distintos. Explicad qué cambiaríais; no alteréis el conjunto de referencia para la entrega básica.

## 5. Preparad el control de reservas sin cobro

Guardad una segunda transformación como `reservas_sin_cobro.ktr`. Este resultado complementa el informe; no lo suméis a las reservas cobradas.

1. Leed reservas y cobros. En la rama de cobros, usad **Select values** para renombrar `id_reserva` como `id_reserva_cobro`. Así distinguiréis la clave de la reserva de la clave encontrada en el pago.
2. Ordenad cada rama por su clave. Configurad **Merge join LEFT OUTER**, con reservas a la izquierda y cobros a la derecha, comparando `id_reserva` con `id_reserva_cobro`.
3. La salida debe conservar las 20 reservas. Aplicad **Filter rows** para quedaros con aquellas cuyo `id_reserva_cobro` sea nulo. No comprobéis `cobrado = 0`: un cobro de cero y un cobro ausente son situaciones distintas.
4. Incorporad el nombre del hotel por `id_hotel`, ordenando ambas entradas antes del nuevo Merge join.
5. Seleccionad `id_reserva`, `hotel`, `canal` e `importe`; añadid con **Add constants** el campo `motivo` con el texto `Sin cobro asociado en el archivo recibido`.
6. Ordenad por `id_reserva` y escribid `temporal/reservas_sin_cobro.csv`, sobrescribiendo el resultado provisional anterior.

Aquí `importe` es el **precio de la reserva**, no dinero cobrado. Debe conservar ese nombre y explicarse en la documentación. No añadáis nombres de huéspedes ni otros datos personales que la tarea no necesita.

## 6. Comprobad antes de publicar

Primero haced una validación manual. Registrad en una tabla **esperado, obtenido y conclusión**. Las vistas previas ayudan a investigar; la comprobación final debe realizarse sobre los archivos completos escritos.

| Comprobación | Resultado con las entradas suministradas |
| --- | --- |
| Reservas leídas / cobros leídos / hoteles leídos | 20 / 15 / 5 |
| Claves de cada origen | Sin duplicados en sus identificadores |
| Filas tras unir reservas y cobros | 15 |
| Filas tras añadir hoteles | 15 |
| Filas del informe, sin cabecera | 13 grupos |
| Suma de `n_reservas` | 15 |
| Suma de `cobrado_total` | 3965.50 € |
| Laredo, canal web | 2 reservas; 496.50 € |
| Reservas sin cobro | 5: identificadores 4, 9, 11, 15 y 18 |
| Reconciliación de reservas | 15 cobradas + 5 sin cobro = 20 |

Contrastad también **cada grupo** con la [tabla de referencia del taller 2](pentaho.md#resultado-de-referencia-del-taller-2). Un total correcto puede ocultar importes asignados al hotel equivocado.

Abrid el informe fuera de Spoon con un lector CSV, importando separadores y decimales correctamente. Confirmad que la cabecera se entiende y que no hay filas vacías ni columnas inesperadas.

### Una comprobación automática mínima

Después de la revisión manual, construid `validar_informe.ktr` para que el job pueda detectar una salida incompleta:

1. Leed el CSV provisional con sus tipos numéricos.
2. Usad **Group by**, sin campos de agrupación, para obtener el recuento de filas y las sumas de `n_reservas` y `cobrado_total`. Activad **Always give back a result row**, disponible en Group by de PDI 9.4: produce una fila resumen aunque no lleguen datos. Verificad expresamente el caso de un archivo con solo cabecera.
3. Comprobad con **Filter rows** que hay 13 grupos, 15 reservas y 3965.50 euros. Un valor nulo tampoco cumple la validación.
4. En la rama válida escribid un mensaje en el log. En la otra, utilizad **Abort** configurado para detener la transformación con error.
5. Construid `validar_sin_cobro.ktr` con el mismo patrón: debe haber cinco filas, todas con identificadores de la lista esperada y sin duplicados. Filtrad identificadores inválidos hacia Abort. Para controlar duplicados, ordenad por `id_reserva` y agrupad por esa clave contando filas: cada grupo debe contener una sola. Después resumid esos grupos sin claves y exigid cinco identificadores. Aplicad también la comprobación de entrada vacía.

Activad **Always give back a result row** también en el último resumen sin claves de `validar_sin_cobro.ktr`. En ambos controles, utilizad **Number of rows (without field argument)** para contar filas y configurad **Abort** para abortar con error desde la primera fila recibida (umbral 0). **No basta con que ninguna fila llegue a Abort**: un CSV con solo cabecera debe hacer fallar la prueba.

Estos valores son controles del conjunto `cierre_aula_01`. En un cierre real variarían: explicaríais controles de reconciliación con las entradas, no fijaríais todos los días el mismo total.

## 7. Coordinad el procedimiento con un job

Guardad `cierre_hotel.kjb`. El job organiza las tareas; las transformaciones tratan las filas. Seguid este orden:

1. **Start** y comprobaciones **File exists** para las tres entradas. Si falta alguna, terminad con **Abort job**, indicando cuál falta.
2. Ejecutad `informe_cobros.ktr` y, solo si termina correctamente, `reservas_sin_cobro.ktr`.
3. Comprobad que existen ambas salidas provisionales. Ejecutad las dos transformaciones de validación.
4. Solo si ambas validaciones terminan correctamente, copiad los dos CSV de `temporal` a `salida`, sustituyendo las versiones anteriores. Podéis usar una entrada de copia de archivos del job; verificad sus opciones de sobrescritura.
5. Registrad éxito únicamente después de que la publicación termine. Cualquier error de transformación, validación o copia debe seguir una rama de error y terminar como fallo.

No borréis el último informe publicado al empezar. Un fallo de lectura o validación debe dejarlo intacto. **Copiar dos archivos no es una publicación atómica del conjunto**: si falla la segunda copia, el job debe avisar y no anunciar éxito. Como ampliación se puede publicar una carpeta versionada completa y señalar qué versión está disponible.

Utilizad **Pan** para probar cada `.ktr` y **Kitchen** para ejecutar el `.kjb` sin depender de Spoon. Adaptad las rutas a vuestro entorno:

```text
pan.bat /file="C:/ruta/procesos/informe_cobros.ktr" /level:Basic
kitchen.bat /file="C:/ruta/procesos/cierre_hotel.kjb" /level:Basic
```

En Linux utilizad `pan.sh` y `kitchen.sh`. Para la entrega basta ejecutar Kitchen manualmente y explicar que el programador de tareas del sistema lo lanzaría de madrugada. Kitchen no queda programado a una hora por el mero hecho de ejecutar el comando.

## 8. Probad éxito, repetición y fallo

Conservad una evidencia de cada prueba y explicad su resultado. Cambiad rutas o archivos únicamente en una copia de trabajo y restauradlos al terminar.

| Prueba | Qué hacéis | Qué debe ocurrir |
| --- | --- | --- |
| Primera ejecución | Ejecutar Kitchen sin informes anteriores | Dos salidas correctas y estado final de éxito |
| Repetición | Ejecutar otra vez con las mismas entradas | Mismos grupos, filas y totales; sin añadir duplicados |
| Falta una entrada | Indicar una ruta de cobros inexistente | Job con error; no se publica un informe nuevo |
| Salida incompleta | Dejar solo la cabecera en una copia provisional y ejecutar su validación | Validación con error, incluso si el CSV existe |
| Total incorrecto | Modificar un importe del informe provisional y ejecutar su validación | Validación con error |
| Recuperación | Restaurar las entradas y ejecutar el job completo | Se generan, validan y publican otra vez las salidas correctas |

Para las dos pruebas de validación, ejecutad directamente la transformación de control sobre la copia alterada: si ejecutáis primero el job completo, regenerará el archivo y eliminará el fallo que queríais probar. Conservad también el log que demuestra que las ramas de error del job no continúan hacia publicación.

## 9. Qué entregáis

Entregad en Moodle **la URL de vuestro repositorio personal y el identificador del commit que queréis evaluar**. Ese commit identifica la versión concreta entregada. Comprobad que los últimos cambios se han subido a GitHub; guardar en Spoon o hacer un commit local no los publica por sí solo.

El repositorio debe contener:

- En `entrada`: los tres CSV originales de vuestro paquete personal, sin cambios; en la raíz, su `asignacion.json`.
- En `procesos`: `informe_cobros.ktr`, `reservas_sin_cobro.ktr`, `validar_informe.ktr`, `validar_sin_cobro.ktr` y `cierre_hotel.kjb`.
- En `salida`: `informe_hotel_canal.csv` y `reservas_sin_cobro.csv`, con los resultados comprobados.
- En `evidencias`: los registros de avance de cada sesión y la tabla de esperado/obtenido/conclusión y las seis pruebas del apartado 8, identificadas y comentadas. Las capturas o extractos de log deben permitir entender qué se ejecutó, qué ocurrió y por qué; no basta una captura sin interpretación.
- Un `README.md` que permita a otra persona preparar y ejecutar el trabajo.

### Qué debe explicar el README

1. Autor, objetivo del encargo y esquema del recorrido de los datos.
2. Versión de PDI y Java utilizadas, carpetas necesarias y pasos para ejecutar el job con Kitchen desde una copia recién descargada. Indicad dónde aparecerán los resultados.
3. Código personal asignado y procedencia de los tres CSV, sus separadores y tipos; identificación `cierre_aula_01`, fecha y hora de generación de los resultados, unidades en euros y límites de los datos.
4. Decisiones de diseño: por qué esas uniones, por qué sumar `cobrado`, cómo se detectan reservas sin cobro y por qué se entrega CSV.
5. Enlaces a las comprobaciones y pruebas de fallo y recuperación; qué ocurre al repetir la ejecución.
6. Fuentes o ayudas utilizadas y qué habéis adaptado vosotros.

El repositorio puede ser público o privado. Si es privado, añadid como colaborador al usuario que os indique el profesor y comprobad que ha aceptado la invitación antes de la evaluación. **No se exige hacerlo público para obtener la nota.** En el lienzo de cada proceso añadid una nota con vuestro nombre y la pregunta que resuelve. No subáis contraseñas ni datos personales de huéspedes.

### Rúbrica: 10,00 puntos

| Criterio | Máximo | Qué se comprueba |
| --- | ---: | --- |
| Repositorio y reproducción del trabajo | 1,00 | Repositorio personal accesible al profesor, paquete asignado y archivos completos, avances por sesión con sus commits identificados, README suficiente y ejecución desde otra carpeta sin cambiar rutas internas. |
| Diseño y comprensión del encargo | 1,00 | Recorrido coherente, reglas justificadas, cierre y unidades identificados, elección de CSV y límites de los datos explicados. |
| Informe de cobros | 2,00 | Lecturas y tipos correctos, uniones y agrupación justificadas; 13 grupos, 15 reservas, 3965.50 euros y correspondencia correcta en cada hotel/canal. |
| Control de reservas sin cobro | 1,00 | Cinco reservas correctas, sin duplicados; distinción entre ausencia de cobro y cobro cero; columnas y motivo claros. |
| Job y validaciones automáticas | 2,00 | Orden y ramas correctos, validación de ambos CSV, rechazo de salida vacía o incorrecta, publicación solo tras validar y aviso de fallo. |
| Pruebas y evidencias | 1,00 | Las seis pruebas documentadas, comparación esperado/obtenido y explicación de repetición, fallos y recuperación. |
| Defensa individual: explicar el funcionamiento | 1,00 | El alumno recorre su solución en Spoon y relaciona entradas, pasos y salidas, explicando sus decisiones con claridad y con sus propias palabras. |
| Defensa individual: responder y comprobar | 1,00 | Responde razonadamente a las preguntas del profesor y realiza o interpreta una pequeña comprobación sobre su trabajo. |
| **Total** | **10,00** | **La defensa individual representa 2,00 puntos.** |

Para cada criterio se asigna el **100 % de su máximo** si está completo y correcto, el **50 %** si se demuestra parcialmente pero hay errores u omisiones relevantes, y **0 puntos** si no se aporta evidencia o no se demuestra. Se suman los puntos obtenidos y se expresa la nota con dos decimales. Los resultados y las evidencias del repositorio se valoran en los seis primeros criterios; la comprensión demostrada personalmente se valora en los dos últimos.

### Encuentro individual con el profesor

El profesor se sentará con cada alumno, orientativamente durante **8–10 minutos**, con su repositorio y sus procesos abiertos. Primero el alumno explicará el recorrido completo y mostrará los dos informes. Después, el profesor realizará las preguntas que considere necesarias sobre ese trabajo y podrá pedir una pequeña comprobación en una copia, sin modificar los originales entregados.

Por ejemplo: seguir una reserva desde su CSV hasta el informe, explicar por qué se ordena antes de Merge join, justificar por qué hay 13 grupos y no 20, distinguir `importe` de `cobrado`, localizar la rama que impide publicar o mostrar qué ocurre si falta un archivo. Son ejemplos para prepararse, **no un cuestionario cerrado**. No se evalúa memorizar nombres de botones, sino comprender lo construido y saber comprobarlo. La explicación es individual, también cuando se hayan compartido dudas o ideas con compañeros.

### Cómo se relaciona con el RA1

| Criterio | Evidencia de esta práctica |
| --- | --- |
| a) Diseño y almacenamiento | Recorrido justificado y separación de originales, provisionales y resultados |
| b) Ingesta | Lecturas, tipos, claves, controles de entradas y repetición |
| c) Formato | CSV configurado y elección razonada frente a otras representaciones |
| d) Procesamiento | Uniones, filtrado, agregación y resultados contrastados |
| e) Presentación | Informe comprensible, periodo identificado y explicación para dirección |

Esta relación ayuda a interpretar las evidencias de la rúbrica anterior. No se valora solo que «se cree un archivo»: debe responder al encargo y superar las comprobaciones.

## 10. Organización de las sesiones y continuación

El trabajo se desarrolla **en el aula**. No avancéis ni modifiquéis la práctica fuera de las sesiones acordadas; si necesitáis recuperar una ausencia o resolver una incidencia, el profesor establecerá un momento supervisado. GitHub conserva las versiones, pero no demuestra por sí solo dónde ni cuándo se editaron los archivos. El seguimiento se apoya en lo observado en clase y en las entregas de avance.

### Un avance al finalizar cada sesión

Reservad los **últimos 5–10 minutos** para guardar y entregar el estado real del trabajo. No esperéis a tener una solución perfecta: un avance incompleto o con un error explicado también permite al profesor orientaros.

| Sesión orientativa | Objetivo de trabajo | Qué mostrar y entregar al finalizar |
| --- | --- | --- |
| 1. Preparación e informe | Recibir el paquete, crear el repositorio, diseñar el recorrido y empezar el informe de cobros | Código asignado, originales, README inicial, transformación en su estado actual y una comprobación de lectura o unión |
| 2. Control y validación | Preparar reservas sin cobro y las dos validaciones | Procesos actualizados, resultados disponibles y comparación esperado/obtenido; explicar los errores pendientes |
| 3. Job y pruebas | Coordinar el procedimiento y probar éxito, repetición, fallo y recuperación | Job, evidencias de las pruebas realizadas y estado de la ejecución desde otra carpeta |
| Sesiones adicionales, si hacen falta | Completar controles, pruebas o documentación pendientes | Un nuevo avance con los cambios y comprobaciones de esa sesión; no se traslada el trabajo pendiente a casa |

La orientación inicial es de **tres sesiones de 55–60 minutos**, ampliables por el profesor según el ritmo del grupo. Los objetivos no obligan a declarar terminada una parte que aún falla. Los encuentros individuales se organizarán aparte y conservan sus **2,00 puntos**.

En cada cierre de sesión:

1. Guardad en Spoon los procesos y anotad en `evidencias/sesion-01.md`, `sesion-02.md`, etc., qué habéis hecho, qué habéis comprobado, qué falta y qué ayuda habéis recibido.
2. Mostrad al profesor el avance o la dificultad principal. Conservad una captura o un extracto de log comentado cuando ayude a entenderlo.
3. Registrad los cambios con un mensaje identificable, por ejemplo `Sesión 1: lectura y primera unión`, y subidlos a GitHub.
4. Comprobad desde el navegador que aparecen. Entregad en el espacio de Moodle indicado por el profesor el **número de sesión, la URL del repositorio y el identificador completo del commit**. El identificador se entrega después de crear el commit; no hace falta escribirlo dentro del archivo de esa misma versión.
5. Al inicio de la siguiente sesión, retomad la versión registrada. Explicad al profesor cualquier diferencia respecto a ella antes de continuar. No borréis ni reescribáis el historial de los avances entregados.

Si falla Internet o GitHub, mostrad el estado al profesor antes de salir. Este registrará la incidencia y conservará una copia o acordará cómo subir **ese mismo avance** en la siguiente sesión, sin exigir trabajo fuera del aula. Moodle lo organiza el profesor: estas instrucciones no crean automáticamente tareas ni bloqueos horarios.

### Modelo breve para el registro de sesión

```text
Sesión y fecha:
Código del paquete:
Qué he hecho hoy:
Qué he ejecutado y qué resultado he obtenido:
Dónde están las evidencias:
Qué error o trabajo queda pendiente:
Qué ayuda he recibido y cómo la he utilizado:
```

Las entregas de avance forman parte del seguimiento y del criterio de repositorio de la rúbrica; **no añaden puntos ni cambian el total de 10,00**. La entrega final del apartado 9 debe identificar la versión final revisada en el aula. El profesor comprobará el paquete utilizado y podrá elegir preguntas relacionadas con lo observado durante las sesiones.

Al acabar, explicad a otro grupo: ¿por qué hay 13 filas y no 20?, ¿por qué sumamos `cobrado`?, ¿qué demuestra la repetición?, ¿qué fallo impide publicar?, ¿por qué este informe no mide ocupación?

La siguiente pregunta es: **¿seguiría cumpliendo el plazo este procedimiento si el histórico creciera hasta 500 GB?** Continuad con la [actividad de transición a la UT2](transicion-ut2.md). Allí justificaréis recursos y alternativas a partir de las necesidades, sin asumir que un tamaño grande obliga siempre a utilizar un clúster.
