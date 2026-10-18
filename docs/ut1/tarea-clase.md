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

Los [talleres de 1.8](pentaho.md) son vuestra referencia técnica. Aquí debéis conectar lo aprendido y demostrar que el procedimiento funciona, también cuando se repite o falta una entrada. Podéis trabajar individualmente o por parejas. Las fechas, la calificación y la entrega formal las establece el profesor en Moodle.

!!! info "Dos actividades con funciones diferentes"
    Esta práctica construye y comprueba una solución con datos pequeños. Después, la [transición a la UT2: 500 GB y un portátil](transicion-ut2.md) plantea qué revisaríamos al aumentar el volumen. No necesitáis Spark, nube ni una base de datos para completar esta práctica.

## Vídeo: qué hacer y qué entregar

Antes de empezar, mira esta guía del encargo del hotel: explica los dos resultados que debéis preparar, las validaciones, la ejecución con Kitchen, las pruebas de fallo y el contenido de la entrega. **Duración: 10 minutos y 36 segundos.**

<video controls playsinline preload="metadata" poster="../../assets/ut1/practica-pentaho-portada.jpg" aria-label="Práctica integradora de Pentaho: qué hacer y qué entregar" style="width: 100%; max-width: 960px; height: auto; border-radius: 12px;">
  <source src="../../assets/ut1/practica-pentaho.mp4" type="video/mp4">
  Tu navegador no permite reproducir este vídeo. Puedes descargarlo en el enlace siguiente.
</video>

El vídeo incluye subtítulos visibles y narración con voz sintética en español. Complementa las instrucciones detalladas de esta práctica; Moodle concreta las fechas, la calificación y la entrega formal.

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

Comprobad primero que funciona el [taller 0 de Pentaho](pentaho.md#taller-0-que-spoon-hable). Utilizad la instalación indicada por el aula.

| Archivo | Separador | Contenido esperado |
| --- | --- | --- |
| [reservas_pdi.csv](../assets/practicas/reservas_pdi.csv) | Coma | 20 reservas; `id_reserva` único |
| [cobros_pdi.csv](../assets/practicas/cobros_pdi.csv) | Punto y coma | 15 cobros; como máximo uno por reserva |
| [hoteles_pdi.csv](../assets/practicas/hoteles_pdi.csv) | Punto y coma | 5 hoteles; `id_hotel` único |

No reutilicéis los CSV de 1.6 o 1.7. Noja representa la ampliación del grupo que aparece en los talleres. Conservad los originales sin modificarlos y utilizad copias para las pruebas de fallo.

Organizad una carpeta de trabajo con `entrada`, `procesos`, `temporal`, `salida` y `evidencias`. Los originales van en `entrada`; las transformaciones y el job, en `procesos`. Acordad la ruta de trabajo con el profesor o utilizad variables. No dejéis rutas que solo funcionen en vuestra cuenta de casa.

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
2. Usad **Group by**, sin campos de agrupación, para obtener el recuento de filas y las sumas de `n_reservas` y `cobrado_total`. Activad la opción de producir una fila de resultado aunque la entrada esté vacía, si vuestra versión la ofrece; verificad expresamente el caso de un archivo con solo cabecera.
3. Comprobad con **Filter rows** que hay 13 grupos, 15 reservas y 3965.50 euros. Un valor nulo tampoco cumple la validación.
4. En la rama válida escribid un mensaje en el log. En la otra, utilizad **Abort** configurado para detener la transformación con error.
5. Construid `validar_sin_cobro.ktr` con el mismo patrón: debe haber cinco filas, todas con identificadores de la lista esperada y sin duplicados. Filtrad identificadores inválidos hacia Abort. Para controlar duplicados, ordenad por `id_reserva` y agrupad por esa clave contando filas: cada grupo debe contener una sola. Después resumid esos grupos sin claves y exigid cinco identificadores. Aplicad también la comprobación de entrada vacía.

Si la versión del aula no permite obtener una fila resumen cuando no hay datos, añadid una comprobación explícita de entrada vacía antes de dar por válida la transformación. **No basta con que ninguna fila llegue a Abort**: un CSV con solo cabecera debe hacer fallar la prueba.

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

Entregad una carpeta o ZIP que otro compañero pueda utilizar con las rutas y la instalación del aula:

- Las cuatro transformaciones `.ktr` y el job `.kjb`.
- Los dos CSV finales: `informe_hotel_canal.csv` y `reservas_sin_cobro.csv`.
- Una explicación breve con el diseño, las reglas, la identificación del cierre de aula, la fecha de generación, unidades, separadores y cómo ejecutar el procedimiento. Incluid la justificación del formato y los límites de los datos.
- La tabla de comprobaciones y las evidencias de las pruebas, con una explicación del error observado y su recuperación. Una captura sin interpretación no basta.

En el lienzo añadid una nota con vuestro nombre y la pregunta que resuelve cada proceso. No incluyáis contraseñas ni dependencias de cuentas personales. La entrega formal se realiza donde indique Moodle.

### Cómo se relaciona con el RA1

| Criterio | Evidencia de esta práctica |
| --- | --- |
| a) Diseño y almacenamiento | Recorrido justificado y separación de originales, provisionales y resultados |
| b) Ingesta | Lecturas, tipos, claves, controles de entradas y repetición |
| c) Formato | CSV configurado y elección razonada frente a otras representaciones |
| d) Procesamiento | Uniones, filtrado, agregación y resultados contrastados |
| e) Presentación | Informe comprensible, periodo identificado y explicación para dirección |

Es una orientación para revisar vuestro trabajo; las ponderaciones y la calificación corresponden al profesor. No se valora solo que «se cree un archivo»: debe responder al encargo y superar las comprobaciones.

## 10. Organización de las sesiones y continuación

Como orientación, reservad **tres sesiones de 55–60 minutos**, ajustables al ritmo del aula: diseño e informe principal; listado de control y validación; job, pruebas y entrega. Si necesitáis más tiempo para los controles automáticos, completadlos en una sesión adicional antes de dar la práctica por terminada.

Al acabar, explicad a otro grupo: ¿por qué hay 13 filas y no 20?, ¿por qué sumamos `cobrado`?, ¿qué demuestra la repetición?, ¿qué fallo impide publicar?, ¿por qué este informe no mide ocupación?

La siguiente pregunta es: **¿seguiría cumpliendo el plazo este procedimiento si el histórico creciera hasta 500 GB?** Continuad con la [actividad de transición a la UT2](transicion-ut2.md). Allí justificaréis recursos y alternativas a partir de las necesidades, sin asumir que un tamaño grande obliga siempre a utilizar un clúster.
