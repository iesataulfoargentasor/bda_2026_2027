---
title: 2.1 Por qué un almacén masivo
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.1. Por qué un almacén masivo

El criterio **a)** pide esto: entender **por qué** hace falta un sistema pensado para **depositar** y **procesar** grandes cantidades de **cualquier tipo** de dato, **rápido**. No es “comprar un disco más gordo”.

## El hotel el martes por la mañana

En el [grupo hotelero de Cantabria](../ut1/caso-hotel.md), recepción genera reservas, mantenimiento recibe medidas de sensores y finanzas registra cobros. El cierre empieza a las **23:00** y gerencia necesita el informe antes de las **8:00**: tenemos una ventana de nueve horas.

Al principio podemos guardar y procesar los ficheros en una máquina. El problema aparece cuando crecen los datos o coinciden varias tareas: mientras se carga el día, alguien consulta el histórico y otro proceso prepara un resumen. Que un fichero no abra en Excel indica un límite de esa herramienta; por sí solo **no demuestra** que necesitemos un clúster.

Para decidir, medimos tres necesidades:

1. **Capacidad:** bytes nuevos al día, histórico que conservamos, índices, copias y espacio de trabajo. Si llegan 20 GB diarios, 365 días suman unos 7,3 TB antes de réplicas y compresión.
2. **Rendimiento:** cuánto tarda el cierre y cuántos datos lee por segundo. Si el proceso tarda once horas, incumple la ventana aunque el disco todavía tenga espacio.
3. **Continuidad:** qué sucede si falla un disco durante el cierre y cuánto tiempo podemos esperar para recuperar el servicio.

Un almacén masivo organiza los datos para afrontar esas necesidades. Puede repartirlos entre servidores, acercarles el procesamiento y mantener copias. La elección se justifica por las mediciones y el tipo de acceso, no por alcanzar una cifra mágica de gigabytes.

## Cualquier tipo (variedad)

En la [UT1](../ut1/por-que-big-data.md) las 5 V ya decían que el dato no es solo la fila SQL. Aquí lo **guardas de verdad**:

| Qué llega | Dónde encaja de primeras |
| --- | --- |
| CSV / Parquet de reservas | [HDFS](hdfs.md) (lago de ficheros) |
| JSON de sensores, anidado | HDFS (bruto) o [MongoDB](mongodb.md) (consultas) |
| Foto de la habitación | HDFS (objeto grande); metadatos en Mongo |
| Grafo “quién recomendó a quién” | Familia [NoSQL de grafos](nosql.md) |
| Caché de sesión del motor de reservas | Clave-valor (Redis o similar) |

En nuestro diseño, el relacional conserva las operaciones de cobro y el lago reúne históricos para análisis. Es una decisión de arquitectura: existen sistemas documentales con transacciones y sistemas SQL distribuidos. Elegimos cada uno por las consultas, las garantías y el coste de administrarlo.

Guardar un formato no significa entenderlo automáticamente. HDFS conserva los bytes de una foto, pero reconocer una habitación requiere otro programa. MongoDB permite consultar campos de documentos; los ficheros binarios grandes suelen quedar en un almacén de objetos o de ficheros, con su referencia en el documento.

## Rápido = cálculo junto al dato

**La cercanía reduce transferencias; no garantiza rapidez por sí sola.** El tiempo final depende también del disco, la red, los índices y de si el trabajo se puede dividir. El título resume una estrategia de Hadoop, no una igualdad matemática.

Si copias 500 GB al portátil para contar noches por hotel, el cuello es el **USB o la red**, no la CPU. El modelo de Hadoop (y de muchas NoSQL) es:

- el fichero **ya está partido** en trozos en varias máquinas;
- cada máquina **cuenta su trozo**;
- al final **juntas** los parciales.

Eso es el criterio **b)** visto desde la puerta: el almacén no es un armario muerto; **está pensado para que el procesamiento se siente encima**. El detalle está en [2.4](computacion-distribuida.md).

## Sin un solo punto que lo tumbe todo

Un disco puede fallar tanto en un portátil como en un servidor. La **replicación** guarda el mismo contenido en distintos nodos para poder leer otra copia. Pero duplicar datos en tres contenedores del mismo ordenador no protege frente al fallo de ese ordenador.

También hay que proteger los procesos que coordinan el sistema. Un HDFS con varios DataNodes y un solo NameNode tiene réplicas de datos, pero necesita una configuración de alta disponibilidad para tolerar la caída de ese NameNode. En MongoDB, un conjunto de réplicas necesita suficientes miembros comunicados para elegir primario.

Un NAS puede incorporar redundancia; no es necesariamente un único disco. En cualquier tecnología distinguimos **réplica** (seguir trabajando ante ciertos fallos) y **copia de seguridad** (recuperar una versión anterior). Un borrado equivocado puede propagarse a todas las réplicas.

## Guardar ahora, decidir el uso después

El criterio **d)** es el lago: escribes el JSON de 2024 **sin** haber inventado el informe de 2026. Mañana Hive o Spark leen solo `hotel` e `importe`. Eso se llama a menudo **esquema al leer** (*schema-on-read*): no tiras el bruto porque hoy no sepas la pregunta.

Conservar datos en bruto permite formular nuevas preguntas, pero necesitamos registrar origen, fecha, formato y significado de los campos. Sin esos metadatos, dentro de dos años no sabremos si `importe` incluía impuestos o si `fecha` era la entrada o la creación de la reserva.

La capacidad tampoco es infinita: se amplía con presupuesto, espacio y administración. Por eso definimos periodos de conservación y verificamos permisos y calidad. **Esquema al leer** significa aplicar una interpretación al consultar; no significa guardar sin organización.

**Comprueba que lo entiendes:** si el informe tarda once horas, ¿añadir otro disco lo solucionaría? Solo si el cuello de botella era capacidad o rendimiento de almacenamiento. Si el programa usa una única CPU y no se paraleliza, antes hay que revisar el procesamiento. Esa conexión conduce al [ecosistema Hadoop](ecosistema.md).

!!! success "Lo que tienes que poder decir"
    “El almacén debe admitir nuestros formatos, procesarlos dentro del plazo y tolerar los fallos previstos. Crece añadiendo recursos, pero hay que medir sus límites y configurar sus garantías.”
