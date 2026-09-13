---
title: 2.4 Computación distribuida
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.4. Computación distribuida

El criterio **b)** es **comprobar el poder** del modelo: no “Hadoop es rápido” de oídas, sino ver que un trabajo **se parte** entre nodos y **termina antes** (si el problema se deja partir).

## MapReduce, con reservas (no con el Quijote)

Dirección pregunta: *¿cuántas noches cobradas hay por hotel?* Los ficheros ya están en [HDFS](hdfs.md), un bloque en cada DataNode.

**Map** (cada nodo, su trozo): lee líneas y emite pares `hotel → noches`.  
**Shuffle** (el clúster): junta todas las `Laredo` en el mismo sitio.  
**Reduce:** suma las noches de Laredo, de Potes, de Santander.

Es el mismo gesto que un `GROUP BY` de SQL, **repartido**. Un *job* puede encadenar varias de estas pasadas.

Pasos, sin romanticismo:

1. Se leen de HDFS pares clave/valor (a menudo la línea del fichero).
2. Hay **tantos *mappers* como bloques** (orden de magnitud).
3. Cada *mapper* emite claves (`Laredo`) y valores (`3`).
4. Se **ordenan** por clave y viajan al *reducer* que toca.
5. El *reducer* agrega y escribe de nuevo en HDFS.

!!! warning "Cuándo no brilla"
    Si el algoritmo **da veinte vueltas** sobre los mismos datos (mucho *machine learning*), cada vuelta **escribe a disco**. Duele. **Spark** (memoria) encaja mejor. MapReduce sigue siendo el modelo que el RA2 te pide **entender y probar** (un conteo, un agregado).

## YARN: quién presta la CPU

Desde Hadoop 2, **YARN** separa “quién tiene RAM y núcleos” de “cómo está escrito el job”. Encima pueden correr MapReduce, Spark, Tez…

Ciclo corto con HDFS:

1. Los datos ya están en HDFS.
2. La aplicación pide recursos a YARN.
3. YARN abre **contenedores** (un trozo de CPU+RAM) **cerca** de los bloques.
4. Se procesa.
5. El resultado vuelve a HDFS.

| Pieza | Analogía | Vida |
| --- | --- | --- |
| **ResourceManager** | El NameNode del *cómputo*: un por clúster | Siempre encendido |
| **NodeManager** | Un por *worker*: vigila contenedores, manda *heartbeat* | Siempre; si cae, el RM manda el trabajo a otro |
| **ApplicationMaster** | Un **por aplicación**: pide contenedores y vigila *sus* tareas | Nace y muere con el job |

El RM tiene un **Scheduler** (reparte, no repara tu *bug*) y un **ApplicationManager** (acepta jobs, relanza el AM si peta).

Un **contenedor** es, por ejemplo, “4 GB y 1 núcleo”. El número de tareas a la vez ≈ número de contenedores libres. Por eso **añadir un *worker*** (criterio **e)**) suma contenedores y **poder de procesamiento** (b).

Hadoop 1 tenía *JobTracker* + *TaskTracker*. Si sale en un texto viejo: eso **era** el cómputo antes de YARN. El API de MapReduce 2 se parece; se recompila y corre sobre YARN.

## Comprobar el poder (qué hacer en el lab)

No hace falta un clúster de 80 nodos. Con la VM o el laboratorio:

1. Sube a HDFS un CSV de reservas (el de [1.8](../ut1/pentaho.md) o uno generado como en [1.7](../ut1/formatos.md)).
2. Lanza un job que **cuente noches por hotel** (streaming en Python o el ejemplo que dé el profesor).
3. Mira el historial: **cuántos *maps***, tiempo, y que la salida en HDFS coincide con un `GROUP BY` en DuckDB sobre el mismo CSV.

```text
# Idea de Hadoop Streaming (el jar y las rutas las da el aula)
hadoop jar hadoop-streaming.jar \
  -files mapper.py,reducer.py \
  -mapper "python mapper.py" \
  -reducer "python reducer.py" \
  -input /user/bda/reservas \
  -output /user/bda/salida_noches
```

*Mapper* (una línea → `hotel\tnoches`):

```python
import sys

for linea in sys.stdin:
    partes = linea.strip().split(",")
    if partes[0] == "id_reserva":
        continue
    # id_reserva,id_hotel,canal,noches,importe  → usa el nombre si cruzaste hoteles
    noches = partes[3]
    hotel = partes[1]
    print(f"{hotel}\t{noches}")
```

*Reducer* (suma por hotel; Hadoop agrupa claves consecutivas):

```python
import sys

actual, total = None, 0
for linea in sys.stdin:
    hotel, n = linea.strip().split("\t")
    n = int(n)
    if hotel != actual:
        if actual is not None:
            print(f"{actual}\t{total}")
        actual, total = hotel, n
    else:
        total += n
if actual is not None:
    print(f"{actual}\t{total}")
```

Si el fichero es pequeño, **no** verás magia: el arranque de YARN pesa más que el cálculo. El criterio b) se entiende cuando el input **es grande** o cuando comparas 1 *mapper* frente a varios bloques.

!!! success "Frase de examen"
    “El poder está en **partir** el fichero (bloques), **mapear** en local y **reducir** las claves. YARN **presta** CPU; HDFS **guarda**. Si añado nodos, hay más contenedores y más *maps* a la vez.”
