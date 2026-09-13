---
title: 1.4 Procesamiento
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.4. Procesamiento de datos

Almacenar no basta: el criterio **d)** pide **procesar** lo guardado. Aquí decides *cómo* se parte el trabajo y *con qué prisa* debe salir el resultado. Un dato en el lago que nadie transforma no sirve al cliente.

En clase lo aplicas en la [tarea de los 500 GB](tarea-clase.md): concurrente, paralelo y distribuido, con un portátil que **no** puede tragarse el fichero.

## Paralelo (dentro de una máquina)

El sistema operativo **reparte el tiempo** entre procesos. Si solo hay **un núcleo**, la “multitarea” es **simulada**: el procesador atiende un rato a cada uno (ventanas de milisegundos). Tú tienes la *impresión* de que el vídeo, el editor y el antivirus van a la vez; en realidad se turnan tan rápido que no lo notas.

**Multinúcleo:** varios núcleos físicos, cada uno una CPU de verdad. Ahí sí hay paralelismo real.

**Multihilo (SMT):** un núcleo *comparte* recursos entre hilos. Mientras un hilo espera un dato de memoria, el otro puede multiplicar. Si **los dos** necesitan la misma unidad a la vez, uno espera. Por eso un procesador “4 núcleos / 8 hilos” **no** es lo mismo que 8 núcleos físicos.

### Cuándo se puede paralelizar

**Sí (independiente):** sumar mil millones de números. Partes en 8 bloques, cada núcleo suma el suyo, al final sumas 8 parciales. El último paso es barato.

**No (dependiente):** empiezas en 0; si el resultado va *par* sumas el siguiente número, si va *impar* lo restas. Cada paso necesita el resultado del anterior. Aunque cortes el vector en trozos, el segundo trozo **no sabe** si debe sumar o restar hasta que acabe el primero.

!!! tip "Pregunta para el examen"
    “Si solo hay un núcleo y el SO cambia de proceso cada X ms, ¿hace varias tareas al mismo tiempo?”  
    **No.** Es multitarea **simulada**. El usuario lo percibe como simultáneo; el silicio no.

## Distribuido (entre máquinas)

El procesamiento **distribuido** reparte subtareas a **nodos de un clúster**. Es paralelo *más* tres problemas que en un solo PC no tenías:

- Los datos **no** están todos en la misma RAM.
- La **red** tarda y a veces falla.
- Un nodo puede caer **a mitad** del job.

La consigna de Hadoop/Spark es “**lleva el cálculo al dato**”: copiar 200 GB a tu portátil para sumarlos es absurdo; mandas la función al nodo que **ya** tiene el trozo.

MapReduce y Spark viven aquí. En este módulo no tienes que programarlos aún; sí debes saber *por qué* existen.

## Estrategias: no todo es “tiempo real”

| Estrategia | ¿Urge el resultado? | Volumen típico | Idea | Ejemplo |
| --- | --- | --- | --- | --- |
| **Por lotes (batch)** | No | Muy alto | Horas o de noche; todo el histórico | Cierre mensual de ventas |
| **Transaccional** | Sí (muy por debajo de 1 s) | Bajo por operación | Un `INSERT` / `UPDATE` de negocio | Picar una línea en caja |
| **Tiempo real / interactivo** | Sí | Medio-alto | Consulta analítica mientras miras el dashboard | “¿Qué tal van las reservas *hoy*?” |
| **Streaming** | Sí, **al ritmo** en que llegan | Una ventana en memoria | Cada evento actualiza un estado | Contador de personas que entran al recinto |

!!! tip "Trampa de vocabulario (muy examinable)"
    Una **transacción** ocurre en tiempo real (el cajero no espera).  
    Un **análisis** en tiempo real **no** es transaccional: no hay `COMMIT` de negocio, hay una consulta o una agregación.  
    Decir “el OLAP es transaccional porque es online” está **mal**. *Online* aquí significa “mientras usas el sistema”, no “hay una transacción ACID”.

**Streaming** añade otra dificultad: las estructuras se actualizan **conforme llegan** los datos. Suele hacerse en memoria, así que hay un **techo** de cuánto puedes tener “caliente”. No es “batch pero más rápido”: es otro contrato.

## OLTP y OLAP

Suenan parecido y los dos son “online”. No hacen el mismo trabajo.

| | **OLTP** | **OLAP** |
| --- | --- | --- |
| Para qué | Operación del día | Análisis e inteligencia de negocio |
| Pregunta típica | “Cobra *esta* línea” | “Ventas por región y mes” |
| Operaciones | Pocas filas: insertar, actualizar, borrar | Agregados, cruces, cubos |
| Modelo | Relacional, **normalizado** | Dimensional, a menudo **desnormalizado** |
| Tiempo | Milisegundos | Segundos (o menos si cabe en RAM) |
| Usuarios | Muchos a la vez (cajeros, web) | Analistas, dirección |
| Relación | **Produce** los hechos | **Lee** esos hechos ya integrados |

Los cubos OLAP guardan el dato en varias **dimensiones** (tiempo, producto, tienda) para no hacer diez `JOIN` cada vez que alguien abre el informe. A veces viven en RAM: rapidísimo, con un límite claro de tamaño.

OLAP **no sustituye** a OLTP: **se alimenta** de él (vía [ingesta](ingesta.md)). Mezclar ambos en la misma base “para no duplicar” suele acabar así:

- el cajero espera porque el informe bloquea la tabla, o
- el informe tarda una eternidad porque la tabla está normalizada para la caja.

## Principio SCV (solo analítica)

Parece CAP, pero **no habla de lecturas y escrituras** en el almacén. Habla de **procesar** datos en un sistema analítico distribuido. Como máximo **dos** de tres:

| Letra | Aquí significa | No lo confundas con |
| --- | --- | --- |
| **S**peed | Poco tiempo desde que el dato está en el sistema analítico hasta el **número** del informe | La “velocidad” de las 5 V (ritmo de *llegada*) |
| **C**onsistency | **Precisión**: usas **todos** los datos (sin muestrear) | La C de CAP (mismo valor en todos los nodos) |
| **V**olume | Puedes atacar conjuntos enormes | El “volumen” de las 5 V es el mismo espíritu, aplicado al *job* |

En Big Data **V casi siempre está** (si no, no estarías aquí). Entonces el menú real es:

| Eliges | Qué sacrificas | Cuándo tiene sentido |
| --- | --- | --- |
| **C + V** | Speed | Cierre de mes: todos los tickets, el tiempo da igual |
| **S + V** | Consistency (muestreo o ventana) | Un widget “en vivo” que no necesita el último céntimo |
| **S + C** | Volume | Un cálculo exacto y rápido sobre un conjunto **pequeño** |

!!! example "Pregunta de aula"
    ¿Analítica en tiempo real con *todos* los petabytes del lago y la misma precisión que el cierre de mes?  
    En general **no**: sería S + C + V. O muestreas (pierdes C) o esperas al lote (pierdes S).

!!! success "Para el criterio d)"
    Procesar no es “darle a Ejecutar”. Es elegir **lote o stream**, **OLTP u OLAP**, y ser consciente del **SCV**. Luego, en [Pentaho](pentaho.md), lo haces visible con un flujo que cambia el dato.
