---
title: 1.1 Por qué Big Data y las 5 Vs
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.1. Por qué Big Data y las 5 Vs

!!! info "Ruta de estudio"
    **Esencial:** relacionar las 5 V con requisitos medibles y distinguir información, análisis y decisión.

    **Práctica guiada:** los cálculos de volumen y de acumulación de eventos.

    **Ampliación:** comparar perfiles profesionales y las V adicionales. No sustituye al recorrido común; su detalle adicional solo se exige si el profesor lo anuncia antes (véase [cómo trabajar la unidad](index.md#como-trabajar-la-unidad)).

## Vídeo: del cobro de Ana a las cinco Vs

Sigue el cobro de Ana hasta el informe de gerencia para comprender cuándo necesitamos Big Data y cómo las cinco Vs ayudan a diagnosticar las dificultades del recorrido. La explicación desarrolla cada V con ejemplos y cálculos sencillos, y conecta el valor de los datos con las analíticas y los roles del equipo. **Duración: 8 minutos y 36 segundos.**

<video controls playsinline preload="metadata" poster="../../assets/ut1/bigdata-historia-portada.jpg" aria-label="Por qué Big Data: del cobro de Ana a las cinco Vs" style="width: 100%; max-width: 960px; height: auto; border-radius: 12px;">
  <source src="../../assets/ut1/bigdata-historia.mp4" type="video/mp4">
  Tu navegador no permite reproducir este vídeo. Puedes descargarlo en el enlace siguiente.
</video>

El vídeo incluye subtítulos visibles y narración con voz sintética en español. Complementa las explicaciones y las actividades del apartado.

[Descargar el vídeo](../assets/ut1/bigdata-historia.mp4) · [Leer la transcripción](../assets/ut1/bigdata-historia.txt) · [Descargar los subtítulos](../assets/ut1/bigdata-historia.es.srt)

## Punto de partida: de una necesidad a una solución

El objetivo de esta unidad es aprender a justificar decisiones sobre los datos. Imaginad que dirección pide conocer cuánto se ha cobrado en cada hotel. Antes de elegir una herramienta, necesitamos identificar dónde se registra cada cobro, cómo se relaciona con una reserva y cuándo debe estar disponible el informe. Esa secuencia conecta la necesidad del negocio con el diseño técnico.

Las cinco V ayudan a describir las dificultades de ese recorrido. El volumen y la velocidad condicionan los recursos; la variedad condiciona la integración; la veracidad exige controles; el valor permite comprobar si el resultado sirve para decidir. No son cinco requisitos que deban cumplirse por igual ni una prueba automática para comprar un clúster.

A lo largo del apartado seguiremos tres pasos: comprender cómo un registro se convierte en información útil, distinguir los trabajos que aprovechan esa información y analizar qué características de los datos dificultan el proceso. Después, en 1.2, estudiaremos una posible respuesta a esas dificultades: repartir el trabajo entre máquinas.


En el [grupo hotelero](caso-hotel.md){target="_blank" rel="noopener"} esto se ve pronto: un servidor, el programa de reservas y un informe por la noche. Durante años basta. El disco no se llena, recepción registra sin esperar y las reservas tienen las mismas columnas.

Un día hay cuatro hoteles, sensores, logs de la web y marketing pide nuevos cruces con plazos más cortos. Si las medidas muestran que el diseño disponible ya no cumple los requisitos de forma viable, habrá que revisarlo. Ahí pueden ser necesarias metodologías de **macrodatos o Big Data**; el crecimiento por sí solo no demuestra que haga falta un clúster.

**Big Data no es “tener muchos Excel”.** Es un conjunto de métodos y tecnologías para capturar, almacenar, procesar y presentar datos cuyos requisitos superan la capacidad viable del diseño convencional disponible para tratarlos con garantías de tiempo, coste o variedad.

No hay una ley que diga “a partir de X terabytes ya es Big Data”. El criterio práctico es este: **el sistema tradicional no escala** en volumen, velocidad o variedad (o el coste de agrandar *esa* máquina es inasumible).

!!! tip "Pregunta que debéis saber responder"
    “¿Esto es un problema de Big Data?” no se contesta con el logo de una herramienta. Se contesta mirando si el diseño de siempre (un servidor, un esquema fijo, un lote nocturno) **sigue siendo viable**.

!!! info "Cómo se lee esta página"
    Tres bloques, **en este orden**: (1) el **viaje** del evento al valor; (2) los **oficios** que extraen ese valor (minería, ciencia de datos, IA) — van **antes** de las V, no las sustituyen; (3) las **V** para pasar revista al hotel. Los relojes del [caso](caso-hotel.md){target="_blank" rel="noopener"}: finanzas cierra a las **23:00**; de madrugada corre el job; a las **8** gerencia abre el panel de **ayer**. Eso no es tiempo real.

## Un PC no basta (y a veces sí)

No todo proyecto con datos es Big Data. El **día 1**, recepción de Laredo registra reservas en el programa del hotel (PMS: *Property Management System*) y finanzas saca el Excel del mes: eso es **Small Data**. Cabe en un PC. Las destrezas de este módulo (limpiar, unir, guardar con criterio) **también** sirven ahí.

A los seis meses hay cuatro hoteles, sensores cada 30 s, logs de la web y fotos de reformas. Este crecimiento obliga a medir si el servidor sigue cumpliendo los requisitos. Si el volumen, la variedad o los tiempos superan su capacidad viable, habrá que revisar el diseño y posiblemente **repartir** el trabajo.

Se dice a menudo que los datos son el petróleo. La analogía se queda corta: el crudo sin refinar no mueve el coche. Guardar por guardar, en la década de 2020, **no** basta. Hay que **conocer** el dato y **cuidarlo** (calidad, linaje, permiso). Si no, gerencia decide con un número bonito y falso.

```mermaid
flowchart TD
 A[Reservas, cobros, sensores y logs] --> B[Medir volumen, ritmo, calidad y plazo]
 B --> C{¿Cumple la solución actual?}
 C -->|Sí| D[Mantener y supervisar]
 C -->|No| E[Localizar el cuello de botella]
 E --> F[Comparar optimización, más recursos y distribución]
 F --> G[Elegir por medidas, coste y garantías]
```

La escala se decide midiendo requisitos, no contando hoteles.

## De los eventos al valor

La transformación del dato en valor requiere contexto. El número `186.50` aislado no permite decidir: necesitamos saber si es un importe, en qué moneda está expresado, a qué reserva corresponde y si representa un precio previsto o un cobro confirmado. Esos significados se documentan como metadatos.

Cuando relacionamos el importe con una fecha y un hotel podemos calcular ingresos diarios. Al comparar varios días aparecen patrones que conviene investigar. Una decisión basada en esos patrones solo aporta valor si se comprueba su efecto: por ejemplo, si una campaña aumenta la ocupación sin reducir excesivamente el margen. Esta secuencia es un modelo didáctico; en un proyecto real se vuelve a etapas anteriores cuando faltan datos o una interpretación resulta incorrecta.

Antes de hablar de clústeres, Parquet o Pentaho, hay que ver **el viaje del dato**. Es el mismo viaje que luego recorreréis en las [capas de la arquitectura](arquitectura.md){target="_blank" rel="noopener"}.

Pensad en el grupo en agosto (Laredo ayuda a imaginar temporada alta):

1. **Evento.** Ocurre algo en el mundo: un huésped reserva, un sensor de ocupación cambia, alguien paga con tarjeta.
2. **Dato.** Ese hecho queda registrado: una fila, un JSON, una foto de una habitación, una línea de log. Todavía no “significa” nada por sí solo; solo está guardado.
3. **Información.** Organizáis esos datos: reservas del día en una tabla, fotos en carpetas por fecha. Ya podéis *consultar* (“¿cuántas llegadas hay mañana?”).
4. **Conocimiento.** Encajáis patrones: “los que reservan el viernes por la tarde cancelan más”. Eso ya no es una fila: es una regla o un modelo.
5. **Sabiduría.** Sabéis *cuándo* aplicar esa regla. El modelo de cancelaciones de Laredo en agosto **no** se copia ciego a Potes en noviembre.
6. **Valor.** Tomáis una decisión que **mejora** el resultado: overbooking más fino, menos habitaciones vacías, una oferta a tiempo. La diferencia entre actuar con esos datos y actuar a ciegas **es el valor**.

![Escalera del dato en Laredo: del evento al valor](../assets/ut1/evento-valor.png)

Este recorrido es una guía para razonar. Encontrar un patrón no prueba su causa ni garantiza valor; hay que validar la decisión y medir su efecto.

| Escalón | Qué es | Ejemplo del hotel |
| --- | --- | --- |
| **Evento** | Algo ocurre | Se confirma una reserva |
| **Dato** | Queda registrado | JSON de la reserva en el canal |
| **Información** | Datos organizados | Tabla “reservas_2026” |
| **Conocimiento** | Regla o modelo | Patrón de cancelación |
| **Sabiduría** | Usarlo en su contexto | Solo en temporada alta |
| **Valor** | Mejor decisión | Menos habitaciones vacías |

Las tecnologías de Big Data **capturan, integran, almacenan y procesan**. Extraer valor lo hacen tres oficios que se pisan y **no** son lo mismo: **minería de datos**, **ciencia de datos** e **inteligencia artificial** (IA). Las tres **beben** de la infraestructura de este módulo; ninguna **es** Big Data. Quién *construye* esa infraestructura (el ingeniero) está al final de la página.

### Tres oficios sobre el mismo dato (y no son sinónimos)

Un viernes en Laredo tenéis el JSON de reservas, los logs de la web y el sensor del parking. Tres personas miran **el mismo** sitio donde está el bruto (el **lago**; el detalle en [1.3](almacenamiento.md){target="_blank" rel="noopener"}) y hacen **trabajos distintos**:

| Oficio | Pregunta que se hace | Qué entrega | Ejemplo del hotel |
| --- | --- | --- | --- |
| **Minería de datos** | «¿Qué patrones *ya están* en lo guardado?» | Reglas, grupos, anomalías | «Quien reserva el viernes por la web y pide parking **cancela más**.» |
| **Ciencia de datos** | «¿Qué hay que preguntar, con qué dato *limpio*, y cómo se lo cuento a quien decide?» | Pregunta bien hecha, análisis, modelo **y** un relato que gerencia entiende | «¿Por qué los martes de noviembre estamos vacíos?» Separa canal web y OTA (agencias tipo Booking), elige el indicador, enseña un gráfico y **no** copia el modelo de playa a Potes. |
| **IA** | «¿Qué *sistema* percibe, decide o genera *sin* que un humano mire cada fila?» | Un producto que **actúa** (o responde) | Al confirmar la reserva, un modelo puntúa el riesgo de cancelación y el canal ofrece tarifa flexible; un *chatbot* responde «¿queda habitación al mar?»; una cámara cuenta coches del parking. |

La minería **descubre**. La ciencia de datos **encuadra, limpia, modela y explica**. La IA **pone un sistema a hacer** una tarea que parece inteligente (percibir, clasificar, dialogar, recomendar). Podéis minar un Excel de 50 MB; podéis hacer ciencia de datos con una encuesta de 200 filas; podéis tener IA con reglas (un motor de ajedrez clásico) **sin** un lago. El clúster ayuda cuando las V de más abajo duelen; **no** define el oficio.

#### En qué se parecen

- Las tres buscan **valor**: una decisión mejor que ir a ciegas.
- Las tres se hunden si falla la **veracidad** (sensores descalibrados, el mismo huésped con tres NIF).
- Las tres pueden vivir **sin** un clúster si el conjunto cabe en una máquina.
- Ninguna sustituye a capturar, guardar y procesar: sin dato usable, el algoritmo más brillante puntúa basura.

#### En qué se distinguen

**Minería de datos** (*data mining*) viene del descubrimiento de conocimiento en bases de datos (a menudo veréis **KDD**: *Knowledge Discovery in Databases*). Caja de técnicas: asociación (“esto se reserva con aquello”), agrupación (tipos de huésped), clasificación, detección de rarezas. El centro de gravedad es el **algoritmo sobre una tabla ya bastante lista**. No obliga a un cuadro de mando ni a un *chatbot*.

**Ciencia de datos** (*data science*) es un oficio **más ancho**. Incluye formular la pregunta de negocio, decidir qué dato hace falta, **cuidar la calidad**, explorar, modelar (estadística clásica o aprendizaje automático) y **comunicar** el resultado a quien no va a leer un cuaderno de código. La minería es **una** herramienta de esa caja, no el nombre nuevo de la caja. Por eso es falso el atajo «ciencia de datos = minería pero cuando hay Big Data».

**Inteligencia artificial** es el campo de los sistemas que se comportan de forma inteligente en una tarea. Dentro hay muchas familias: búsqueda, sistemas expertos con reglas, robótica, visión, lenguaje… El **aprendizaje automático** (*machine learning*, **ML**: el programa **mejora con ejemplos** en vez de llevar todas las reglas escritas a mano) es hoy el camino más habitual hacia un producto de IA. Un árbol de decisión puede ser “minería” si lo usáis para *entender* una regla, o “ML / IA” si lo **desplegáis** para puntuar cada reserva nueva. No discutáis la etiqueta: mirad **para qué** sirve el artefacto.

!!! failure "Tres frases que estropean el mapa"
    - «La IA contiene a la ciencia de datos, que contiene a la minería» (no es una matrioska).
    - «Ciencia de datos = minería + Hadoop» (se puede hacer ciencia de datos con 200 filas; el logo del clúster no bautiza el oficio).
    - «IA = el *chatbot*» (visión, reglas, un puntuador de cancelaciones… también son IA).

Solapes, no escalera. La infraestructura de este módulo **alimenta** a los tres; no es un peldaño que “se convierte” en IA:

```mermaid
flowchart TB
  BD[Este módulo: capturar · guardar · procesar · presentar]
  DM[Minería: patrones en lo ya guardado]
  DS[Ciencia de datos: pregunta · calidad · modelo · comunicar]
  AI[IA: sistema que percibe o actúa]
  ML[Aprendizaje automático]
  BD --> DM
  BD --> DS
  BD --> AI
  DM --> DS
  ML --> DS
  ML --> AI
  ML --> DM
```

- El **ML** es el puente frecuente: la minería lo usa para descubrir; la ciencia de datos, para un modelo que se explica; la IA, para un servicio en producción.
- La **IA** no es solo un modelo: es el sistema (datos de entrada, modelo, umbral, acción, supervisión). Un *chatbot* sin el JSON de habitaciones al día **alucina** huecos.
- La **ciencia de datos** puede terminar en un informe **sin** desplegar IA. Gerencia a veces solo necesita el gráfico del martes vacío.

#### De un estudio al panel (en el hotel)

No hay una receta única. Un trabajo de ciencia de datos casi siempre recorre este bucle. El **ingeniero** de este módulo alimenta sobre todo la recuperación y la preparación; si fallan, el modelo produce resultados poco fiables.

1. **Objetivo.** Gerencia quiere menos habitaciones vacías los martes.
2. **Recuperación.** PMS, pasarela, sensores, un Excel de Comillas. Sale **bruto**.
3. **Preparación.** Unificáis `web` y `WEB`, conserváis el estado de cancelación y cruzáis reserva con cobro (eso, en [1.6](ingesta.md){target="_blank" rel="noopener"}, es la T de un ETL: extraer, transformar, cargar). Conservad las canceladas para estudiar la cancelación; no son lo mismo que los *no-show*.
4. **Exploración.** El viernes por la web cancela más.
5. **Modelado.** Estima el riesgo de que no se presente (*no-show*) o el cupo.
6. **Presentación y vuelta.** El gráfico o el panel de las 8. Si no cuadra, **volvéis al paso 2**.

En el [curso de especialización](../index.md){target="_blank" rel="noopener"} otros módulos os pondrán a modelar. **Aquí** diseñáis el almacén, la ingesta, el formato y la presentación. Si el lago está sucio o no se puede leer a tiempo, da igual el nombre del algoritmo: no hay valor.

!!! tip "Frase para el examen y para el pasillo"
    Big Data **prepara** el dato. La minería **busca patrones**. La ciencia de datos **hace la pregunta y cuenta el resultado**. La IA **encarna** una tarea en un sistema. Se solapan; no se sustituyen.

## Las V: un diagnóstico, no una lista para recitar

Al principio se usaban **tres V**: **volumen**, **velocidad** y **variedad**. Luego **valor** y **veracidad** (cinco). En algunos textos, **viabilidad** y **visualización** (siete). No memoricéis el recuento: **pasad revista** al hotel. No contéis cuántas V aparecen para decidir. Una sola puede imponer un requisito difícil; varias pueden resolverse con una solución sencilla. Medid la carga y el plazo y justificad la respuesta.

![Las V aplicadas al grupo hotelero: cinco de diagnóstico y dos que a veces se añaden](../assets/ut1/cinco-vs-hotel.png)

### Volumen

Para estimar almacenamiento hay que calcular cuánto se genera y durante cuánto tiempo se conserva. Un punto de partida es `registros diarios × bytes por registro × días de conservación`. Después se añaden las copias, los índices, los resultados intermedios y el margen de crecimiento. La compresión puede reducir la cifra, pero debe medirse con datos representativos.

Por ejemplo, 1.000 sensores que envían un registro de 200 bytes cada 30 segundos generan unos 576 MB diarios antes de añadir metadatos y réplicas. La cantidad puede ser manejable en una máquina; la dificultad cambia si conservamos años de datos, incorporamos vídeo o exigimos muchas consultas simultáneas. Por eso el tamaño se interpreta junto con los requisitos del sistema.

Es la cantidad de **bytes**. Hoy se habla con naturalidad de terabytes y petabytes; los centros grandes llegan a exabytes.

| Nombre (SI) | Símbolo | Bytes (aprox.) | Para situaros |
| --- | --- | --- | --- |
| Kilobyte | kB | 10³ | Una página de texto |
| Megabyte | MB | 10⁶ | Una foto no enorme |
| Gigabyte | GB | 10⁹ | Una película comprimida |
| Terabyte | TB | 10¹² | Un disco de sobremesa |
| Petabyte | PB | 10¹⁵ | Muchos racks o un lago serio |
| Exabyte | EB | 10¹⁸ | Escala de un operador o un ministerio |
| Zettabyte | ZB | 10²¹ | Orden de magnitud de “todo internet” |

En informática también existen KiB, MiB, GiB (potencias de 2: 1 KiB = 1024 bytes). El fabricante anuncia 1 TB como **1000 GB** (base 10). El explorador suele mostrar **cerca de 931 GB** porque cuenta GiB y a veces los llama “GB”. El disco no está roto: **cuentan distinto**.

En el hotel el volumen sale de reservas, logs de la web, sensores, fotos de habitaciones. Fuera veréis lo mismo a otra escala: redes, genómica, satélites.

!!! example "Un cálculo para notar la escala"
    Si guardáis **4 bytes al día** (un número: el peso) por cada persona del planeta (~8·10⁹) durante un año:

    `4 × 8×10⁹ × 365 ≈ 12 TB`

    Eso es **un** atributo. Añadir imágenes o conservar más años aumenta la capacidad necesaria. La cifra obliga a revisar almacenamiento, tiempos y coste; por sí sola no demuestra que ampliar un equipo sea insuficiente ni que haga falta un clúster.

**Qué implica en el diseño:** primero distinguimos el límite de memoria, la capacidad de almacenamiento y el tiempo disponible. Que un archivo no quepa entero en RAM no obliga a usar varias máquinas: según la operación, podemos leerlo por bloques y utilizar disco para resultados intermedios. Si falta espacio o el proceso no termina a tiempo, comparamos optimizar consultas y formatos, ampliar recursos, separar almacenamiento y cálculo o distribuir el trabajo. Leer por bloques tampoco garantiza cumplir el plazo: hay que medirlo.

Distribuir puede ser necesario cuando las alternativas en una sola máquina no cumplen los requisitos de forma viable. Un lago organiza datos, pero su nombre no indica cuántas máquinas calculan; un formato divisible facilita repartir tareas, pero también puede procesarse localmente. Justificar la elección con medidas de capacidad, tiempo y coste es el criterio **a)** empezando a trabajar.

### Velocidad

Aquí conviene separar **tasa de llegada** y **latencia**. La primera indica cuántos registros o bytes llegan por segundo. La segunda mide cuánto tarda un dato en estar disponible para su uso. Un sistema puede aceptar muchos eventos por segundo y, aun así, tardar varios minutos en actualizar el informe.

Si entran 1.000 eventos por segundo y solo se procesan 800, quedan pendientes 200 cada segundo: al cabo de un minuto hay 12.000 eventos acumulados. Una cola absorbe un pico temporal, pero no resuelve por sí sola una diferencia permanente entre entrada y capacidad de procesamiento.

No basta con que quepa: los datos **siguen llegando**. El reto es capturarlos, integrarlos y, si el negocio lo pide, reaccionar **antes de que dejen de servir**.

En el hotel:

- La web de reservas escribe un log por cada clic.
- Los sensores publican cada ~30 s (el semáforo de recepción no puede esperar al lote de las 23:00).
- Finanzas cierra a las 23:00; el panel de las 8 es el lote de **ayer**.

Dimensionar el disco **no** arregla un atasco de ingesta. Si el embudo es más ancho pero el cuello sigue igual, el agua se derrama. De ahí el flujo continuo y las [colas](ingesta.md){target="_blank" rel="noopener"} (desacoplan “quien produce” de “quien consume”).

!!! example "Mismo volumen, distinta V"
    10 TB de cobros históricos que cargas **una vez** al mes → duele sobre todo el **volumen**.  
    10 TB al día en eventos de sensores que hay que cruzar con el PMS **ahora** → duele la **velocidad** (y luego el volumen).

### Variedad

La variedad también existe dentro de datos aparentemente iguales. Dos CSV pueden expresar las fechas de forma distinta, utilizar monedas diferentes o asignar códigos diferentes al mismo hotel. Integrar exige acordar tanto la estructura como el significado de los campos.

“No estructurado” significa que el contenido no se presenta directamente como registros tabulares. Una imagen sí tiene formato, tamaño y metadatos; para analizar qué aparece en ella necesitamos extraer características. Del mismo modo, un PDF puede contener texto, tablas o una imagen escaneada, y su tratamiento dependerá de ese contenido.

No todos los datos se parecen a una hoja de cálculo. En el mismo hotel conviven tres familias:

| Tipo | Qué es | Cómo lo reconoces | En el hotel |
| --- | --- | --- | --- |
| **Estructurado** | Esquema fijo (filas y columnas) | Todas las filas tienen las mismas columnas | Tabla SQL de reservas del PMS |
| **Semiestructurado** | Hay marcas o claves; el esquema puede variar | Un registro trae un campo que otro no tiene | JSON del canal web, logs |
| **No estructurado** | No hay columnas fijas de entrada | No lo filtras como una tabla | Foto del DNI, PDF de incidencia, vídeo del hall |

Estas diferencias de representación influyen en cómo organizamos el almacenamiento, pero no obligan a elegir un único tipo de almacén. Un **data warehouse** reúne datos para consultas analíticas con definiciones comunes: puede tener tablas de preparación y, según el motor, admitir datos semiestructurados como JSON. Un **data lake** puede conservar originales y también tablas preparadas; al leer los originales aplicamos una interpretación, mientras que las tablas preparadas pueden tener un esquema definido y comprobado al escribirlas. Un **data mart** organiza información para un ámbito concreto, como finanzas o marketing, y puede alimentarse de un warehouse, de otras fuentes o de ambos.

En el ejemplo del hotel conservamos originales en el lago, preparamos las tablas del cierre en el warehouse y ofrecemos a cada departamento un mart con las definiciones comunes. Es una decisión de este diseño, no un recorrido obligatorio para todos los proyectos. El detalle está en [1.3](almacenamiento.md){target="_blank" rel="noopener"}.

La variedad es la V que más sorprende al que solo ha visto SQL: el problema no es solo “que quepa”, es que **no todo es tabla**.

### Veracidad

Podemos convertir esta V en controles concretos: **completitud** (¿falta el identificador?), **validez** (¿la fecha tiene un formato permitido?), **unicidad** (¿se ha recibido dos veces el mismo cobro?), **coherencia** (¿la salida es posterior a la entrada?) y **actualidad** (¿el informe corresponde al periodo anunciado?).

Detectar un dato inválido no implica borrarlo sin explicación. Se puede apartar en una zona de revisión, registrar el motivo y corregirlo con el responsable del origen. Así conservamos la trazabilidad y evitamos confundir “dato ausente” con “valor cero”.

¿Os podéis fiar de lo que hay? Duplicados, sensores descalibrados, campos vacíos, relojes mal puestos, el mismo huésped con tres NIF.

A más volumen, más basura **si no hay calidad y gobierno**: linaje (“de dónde salió esta cifra”), metadatos y reglas de limpieza. Un modelo sobre datos sucios no es “más Big Data”: es una **peor** decisión, más rápida.

!!! failure "La trampa de la veracidad"
    “Como hay muchos datos, el error se compensa.” A veces el error está **sesgado** (todos los sensores de Potes fallan igual en invierno) y el modelo lo aprende como si fuera verdad.

### Valor

Para evaluar el valor hay que definir un objetivo observable antes de construir la solución. “Tener un lago” describe un medio; “reducir de dos horas a diez minutos la preparación del cierre” describe un resultado que podemos medir.

El beneficio se compara con los costes de almacenamiento, cálculo, mantenimiento y trabajo humano. También se comprueba que la mejora no perjudique otra necesidad: un informe más rápido que ralentiza las reservas puede no compensar. La pregunta de negocio orienta, por tanto, todas las decisiones técnicas posteriores.

Es la V que **justifica el gasto**. Almacenar por almacenar no es Big Data: es un archivo caro. El valor aparece cuando una decisión (cupo, tarifa, overbooking, una oferta a tiempo) **mejora** respecto a no usar esos datos.

Si no sabéis qué decisión vais a mejorar, todavía no tenéis un proyecto: tenéis un disco.

### Viabilidad y visualización (cuando se habla de 7)

No entran en el recuento clásico. Sirven para no diseñar un sistema que **nadie puede usar**.

| V extra | Pregunta | En el hotel |
| --- | --- | --- |
| **Viabilidad** | ¿La empresa puede **usar** de verdad esos datos? ¿Cuántos hacen falta para la predicción que importa? | Poner sensores en Potes y no tener a nadie que limpie el JSON **no** es viable. |
| **Visualización** | ¿Gerencia **ve** el número a tiempo, en un gráfico o un indicador? | El panel de las 8. Un lago de 8 TB sin cuadro de mando no decide nada. |

La visualización no es “hacerlo bonito”. En [1.8](pentaho.md){target="_blank" rel="noopener"} y en el criterio **e)** del RA1 es presentar para que alguien que no abre el cuaderno pueda decidir.

## Qué pregunta hacéis (cuatro analíticas)

Las cuatro analíticas pueden encadenarse sobre un mismo problema. Primero calculamos que la ocupación de los martes ha bajado (**descriptiva**); después investigamos si cambió el calendario o el canal de venta (**diagnóstica**); estimamos la ocupación del próximo martes (**predictiva**) y comparamos posibles promociones (**prescriptiva**).

Una asociación no demuestra una causa. Si las reservas de un canal cancelan más, puede influir el tipo de tarifa o la temporada. Asimismo, una predicción debe expresar su incertidumbre y una recomendación debe respetar restricciones como el presupuesto o la capacidad del hotel.

La **inteligencia de negocio** (*business intelligence*, **BI**) coge lo ya guardado y responde sobre el **pasado**: qué ocurrió y por qué. Con más dato y, a veces, IA, podéis mirar **adelante**: qué pasará y qué conviene hacer.

| Analítica | Pregunta | En el hotel | Suele vivir en |
| --- | --- | --- | --- |
| **Descriptiva** | ¿Qué pasó? | Ocupación de agosto en Laredo | BI, panel, SQL |
| **Diagnóstica** | ¿Por qué pasó? | Los martes de noviembre, vacíos | BI + exploración |
| **Predictiva** | ¿Qué pasará? | Cancelaciones del viernes | Ciencia de datos / IA |
| **Prescriptiva** | ¿Qué hacemos? | Overbooking y tarifa flexible | Una regla de negocio; a veces IA |

El BI **no** desaparece cuando llega el lago. Gerencia sigue necesitando el “qué pasó”. Big Data **no** es un sinónimo de predicción: a veces el valor es un informe de ayer que llega **a las 8**, no un modelo.

```mermaid
flowchart TB
  N[Necesidad de gerencia: comprender y decidir] --> A[Analista: consultar, interpretar y comunicar]
  N --> C[Científico: formular preguntas, explorar y validar modelos]
  N --> I[Ingeniero: ingerir, transformar y mantener datos utilizables]
  N --> R[Arquitecto: diseñar componentes, acceso y crecimiento]
  A --> E[Equipo: contrastar resultados, límites y decisiones]
  C --> E
  I --> E
  R --> E
```

Las cuatro preguntas de la tabla anterior requieren colaboración. El científico también revisa la calidad e interpreta resultados; el analista necesita comprender el negocio. Estos perfiles describen responsabilidades que pueden solaparse, no departamentos aislados.

Los perfiles colaboran y pueden solaparse. Predecir no garantiza acertar; una recomendación debe incluir incertidumbre, restricciones del negocio y evaluación de sus efectos.

## Quién hace qué (un solo mapa)

Los tres oficios de arriba **beben** del dato. Este módulo forma sobre todo a quien **deja ese dato usable**: el **ingeniero**.

| Rol | Encargo | En el hotel |
| --- | --- | --- |
| **Analista de datos** | Convierte dato en información (SQL, gráficos). Conoce el negocio. | El informe de ocupación por canal. |
| **Científico de datos** | Pregunta, calidad, modelo (a menudo IA) y el relato a gerencia. | El riesgo de cancelación; no copia playa a Potes. |
| **Ingeniero de datos** | Extraer, transformar, cargar y guardar (ETL). **Aquí.** | El job de madrugada, **antes de las 8**. |
| **Arquitecto de datos** | Estrategia: qué crece, quién accede, linaje, seguridad. | Si mañana abre otro hotel, el diseño **aguanta**. |

El arquitecto **elige** el plano. El ingeniero **construye** las tuberías. El científico **pregunta** con el dato ya usable. El analista **cuenta a las 8** lo que gerencia puede leer. Minería e IA no son “otros nombres del ingeniero”: usan lo que el ingeniero deja listo.

El ciclo generación → ingesta → transformación → entrega → consumo está en [1.5](arquitectura.md){target="_blank" rel="noopener"}.

## Fuera de este apartado (y no lo copies aquí)

OLTP frente a OLAP (operar en recepción / informar a gerencia) se desarrolla en [1.4](procesamiento.md){target="_blank" rel="noopener"}. Dónde guardar (relacional, NoSQL, almacén de informes, lago) está en [1.3](almacenamiento.md){target="_blank" rel="noopener"}. El paisaje de herramientas y Lambda/Kappa, en [1.5](arquitectura.md){target="_blank" rel="noopener"}. La ingesta, en [1.6](ingesta.md){target="_blank" rel="noopener"}.

## El mismo oficio, otros sitios

El hotel es el hilo. El oficio se parece fuera:

- **Industria:** sensores que no pueden perder lecturas (como los de habitación).
- **Vídeo bajo demanda:** cada clic y cada pausa, para recomendar (como el canal web del hotel).
- **Mapas:** tráfico de muchos conductores a la vez (velocidad + volumen).
- **Redes sociales:** texto libre, sentimiento, publicidad (variedad + veracidad dudosa).

Si podéis decir *qué V duele* en cada uno, el 1.1 está asimilado.

## Qué conseguimos (si el diseño es bueno)

Cuando el diseño responde a las V que duelen, podéis:

- Integrar fuentes que antes vivían en silos (PMS, web, sensores).
- Replicar y distribuir para **no parar** si cae un nodo.
- Procesar en paralelo lo que una máquina no termina a tiempo.
- Alimentar minería / IA y **cuadros de mando** para quien decide (más adelante, criterio **e)**).

!!! failure "Errores frecuentes en clase y en empresas"
    - “Tenemos Big Data porque usamos Hadoop.” La herramienta no define el problema.
    - “Todo tiene que ser en tiempo real.” El panel de las 8 es un lote; el [SCV](procesamiento.md#scv){target="_blank" rel="noopener"} ayudará a valorar los compromisos entre plazo, precisión y volumen.
    - Confundir los GB de marketing del disco con lo que el explorador muestra (base 10 frente a GiB).
    - Medir el éxito en terabytes guardados, no en decisiones mejoradas.

## Para el criterio a)

Antes de elegir Mongo, Parquet o Pentaho, hay que **caracterizar** el problema:

1. ¿Qué Vs duelen de verdad (y cuáles no)?
2. ¿El dato es de operación (caja, reserva) o de análisis (informe, modelo)?
3. ¿Hace falta guardar el histórico en bruto por si cambia la pregunta?

Eso es diseñar la solución de almacenamiento. Instalar software viene **después**.

## Actividades

No puntúan en Moodle. Sirven para comprobar si podéis **caracterizar** (criterio **a)**) sin recitar la lista.

1. **¿Qué V duele?** Para cada frase, elige la V principal y justifica en una línea.
    1. Los sensores de Potes publican cada 30 s y el semáforo de recepción no puede esperar al lote de las 23:00.
    2. El mismo huésped aparece como `García`, `GARCIA` y `Garcìa` en tres canales.
    3. Dirección pide guardar *todo* “por si acaso”, pero no sabe qué decisión va a mejorar.
2. **Cuatro preguntas.** Clasifica cada una en descriptiva, diagnóstica, predictiva o prescriptiva.
    1. «¿Cuántas noches cobramos en Laredo en agosto?»
    2. «¿Por qué Comillas se vacía los martes de noviembre?»
    3. «¿Cuántos no-show habrá el viernes en Santander?»
    4. «¿Subimos el overbooking un 4 % o mandamos tarifa flexible?»
3. **Un rol.** El panel de las 8 llega a las 11 y las cifras no cuadran con recepción. ¿Lo arregla sobre todo el analista, el científico o el ingeniero? ¿Por qué?

!!! tip "Comprobación rápida"
    Si en (1) habéis puesto velocidad / veracidad / valor, en (2) descriptiva → prescriptiva en ese orden, y en (3) ingeniero (ingesta y calidad **antes** del gráfico), el apartado está asimilado.

## Autoevaluación del 1.1

Diez preguntas (A–D, **una** correcta) sobre los conceptos del apartado. No puntúan en Moodle. En **cada** una, **Comprobar respuesta**: si es correcta o no, y una explicación breve. Podéis repetir el test.

<div class="dwec-quiz" data-dwec-quiz data-src="../../assets/quizzes/ut1-1-1.json"></div>
