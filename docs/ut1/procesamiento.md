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

El sistema operativo **reparte el tiempo** entre programas. Si solo hay **un núcleo**, la “multitarea” es **simulada**: el procesador atiende un rato a cada uno (ventanas de milisegundos). Tú tienes la *impresión* de que el vídeo, el editor y el antivirus van a la vez; en realidad se turnan tan rápido que no lo notas.

**Multinúcleo:** varios núcleos físicos, cada uno una CPU de verdad. Ahí sí hay paralelismo real.

**Multihilo:** un núcleo *comparte* recursos entre hilos. Mientras un hilo espera un dato de memoria, el otro puede multiplicar. Si **los dos** necesitan la misma unidad a la vez, uno espera. Por eso un procesador “4 núcleos / 8 hilos” **no** es lo mismo que 8 núcleos físicos.

### Cuándo se puede paralelizar

**Sí (independiente):** sumar mil millones de números. Partes en 8 bloques, cada núcleo suma el suyo, al final sumas 8 parciales. El último paso es barato.

**No (dependiente):** empiezas en 0; si el resultado va *par* sumas el siguiente número, si va *impar* lo restas. Cada paso necesita el resultado del anterior. Aunque cortes la lista en trozos, el segundo trozo **no sabe** si debe sumar o restar hasta que acabe el primero.

!!! tip "Pregunta para el examen"
    “Si solo hay un núcleo y el sistema cambia de programa cada X ms, ¿hace varias tareas al mismo tiempo?”  
    **No.** Es multitarea **simulada**. El usuario lo percibe como simultáneo; el silicio no.

## Distribuido (entre máquinas)

El procesamiento **distribuido** reparte subtareas a **nodos de un clúster**. Es paralelo *más* tres problemas que en un solo PC no tenías:

- Los datos **no** están todos en la misma RAM.
- La **red** tarda y a veces falla.
- Un nodo puede caer **a mitad** del trabajo.

La consigna de Hadoop/Spark es “**lleva el cálculo al dato**”: copiar 200 GB a tu portátil para sumarlos es absurdo; mandas la función al nodo que **ya** tiene el trozo.

MapReduce y Spark viven aquí. En este módulo no tienes que programarlos aún; sí debes saber *por qué* existen.

## Estrategias: no todo es “tiempo real”

| Estrategia | ¿Urge el resultado? | Volumen típico | Idea | Ejemplo |
| --- | --- | --- | --- | --- |
| **Por lotes** (*batch*) | No | Muy alto | Horas o de noche; todo el histórico | Cierre mensual de ventas |
| **Por transacciones** | Sí (muy por debajo de 1 s) | Bajo por operación | Un cobro, una reserva, un alta | Picar una línea en caja |
| **Tiempo real / interactivo** | Sí | Medio-alto | Consulta de análisis mientras miras el panel | “¿Qué tal van las reservas *hoy*?” |
| **Streaming** | Sí, **al ritmo** en que llegan | Una ventana en memoria | Cada evento actualiza un recuento | Contador de personas que entran al recinto |

!!! tip "Trampa de vocabulario (muy examinable)"
    Un **cobro** ocurre en tiempo real (el cajero no espera).  
    Un **análisis** en tiempo real **no** es lo mismo: no estás confirmando un cobro, estás **consultando o resumiendo**.  
    La palabra inglesa *online* aquí solo significa “mientras usas el sistema”, no “hay una [transacción](almacenamiento.md) de dinero”.

**Streaming** añade otra dificultad: las cuentas se actualizan **conforme llegan** los datos. Suele hacerse en memoria, así que hay un **techo** de cuánto puedes tener “caliente”. No es “un lote, pero más rápido”: es otro contrato.

## Dos trabajos: operar el día a día o analizar el histórico

En cualquier empresa conviven **dos oficios** que parecen el mismo (“usar el ordenador con datos”) y no lo son.

**Oficio 1 — Operar.** El cajero cobra, el hotel reserva, el alumno se matricula. Muchas personas a la vez, cada una toca **poca** información, y tiene que terminar **en milisegundos**. Si esto se atasca, la cola de la caja no avanza.

**Oficio 2 — Analizar.** Dirección pregunta “ventas por comarca y mes” o “ocupación de agosto frente a julio”. Eso recorre **mucho** histórico, resume, compara. Nadie está esperando con la tarjeta en la mano, pero el número tiene que ser **defendible**.

Mezclar los dos en **la misma** tabla “para no duplicar” suele acabar así:

- el cajero espera porque el informe está recorriendo la tabla, o
- el informe tarda una eternidad porque la tabla está pensada para cobrar, no para resumir.

Por eso se **copian** los hechos del oficio 1 hacia un almacén del oficio 2 (eso es la [ingesta](ingesta.md)). El segundo **no sustituye** al primero: **se alimenta** de él.

### Cómo se llaman en los libros: OLTP y OLAP

Cuando leas documentación o un examen, esos dos oficios aparecen con siglas inglesas. No asumas que las conoces: son solo **nombres** de lo de arriba.

| | **OLTP** | **OLAP** |
| --- | --- | --- |
| Significa | *Online Transaction Processing*: procesar **operaciones** del día a día | *Online Analytical Processing*: procesar **consultas de análisis** |
| Para qué | Cobrar, reservar, matricular | Informes, tendencias, inteligencia de negocio |
| Pregunta típica | “Cobra *esta* línea” | “Ventas por región y mes” |
| Cuánto toca cada vez | Pocas filas | Muchas filas, resúmenes |
| Tiempo | Milisegundos | Segundos (o menos si el resumen ya está preparado) |
| Usuarios | Cajeros, web, recepción | Analistas, dirección |
| Relación | **Produce** los hechos | **Lee** esos hechos ya copiados e integrados |

*Online* vuelve a significar “en el sistema, ahora”, no “pago por internet”.

A veces el almacén de análisis guarda el dato ya **cortado por ejes** (tiempo, producto, tienda). En los libros eso se llama **cubo**. La idea es simple: el informe del lunes no tiene que cruzar diez tablas cada vez; el cruce **ya está hecho**. Si además cabe en RAM, va rapidísimo… y tiene un límite de tamaño.

En [1.3](almacenamiento.md) el **warehouse** es el sitio típico del oficio 2; la base relacional de la caja es el sitio típico del oficio 1.

## Principio SCV (solo para análisis) { #scv }

Parece el [CAP](almacenamiento.md) de las bases repartidas, pero **no habla de si el saldo se ve igual en todos los nodos**. Habla de **hacer un cálculo** en un sistema de análisis. Como máximo puedes pedirle **dos** de estas tres cosas:

| Letra | Aquí significa | No lo confundas con |
| --- | --- | --- |
| **S**peed (velocidad) | Poco tiempo desde que el dato está en el sistema de análisis hasta el **número** del informe | La “velocidad” de las 5 V (ritmo al que *llegan* los datos) |
| **C**onsistency (aquí: **precisión**) | Usas **todos** los datos, sin muestrear | La C de CAP (mismo valor en todos los nodos) |
| **V**olume | Puedes atacar conjuntos enormes | El “volumen” de las 5 V, aplicado al *trabajo* de cálculo |

En Big Data **V casi siempre está** (si no, no estarías aquí). Entonces el menú real es:

| Eliges | Qué sacrificas | Cuándo tiene sentido |
| --- | --- | --- |
| **C + V** | Speed | Cierre de mes: todos los tickets, el tiempo da igual |
| **S + V** | Precisión (muestreo o ventana) | Un recuento “en vivo” que no necesita el último céntimo |
| **S + C** | Volume | Un cálculo exacto y rápido sobre un conjunto **pequeño** |

!!! example "Pregunta de aula"
    ¿Análisis en tiempo real con *todos* los petabytes del lago y la misma precisión que el cierre de mes?  
    En general **no**: sería S + C + V. O muestreas (pierdes precisión) o esperas al lote (pierdes velocidad).

!!! success "Para el criterio d)"
    Procesar no es “darle a Ejecutar”. Es elegir **lote o stream**, **operar o analizar** (OLTP u OLAP), y ser consciente del **SCV**. Luego, en [Pentaho](pentaho.md), lo haces visible con un flujo que cambia el dato.
