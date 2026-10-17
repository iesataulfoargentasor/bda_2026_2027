---
title: 2.4 Computación distribuida
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.4. Computación distribuida

En los apartados anteriores hemos separado almacenamiento y ejecución. Ahora comprobaremos **cómo se divide un cálculo, cómo se reúnen sus resultados y cuándo compensa hacerlo**. El criterio **b)** exige observar el procesamiento distribuido y medirlo; no basta con afirmar que añadir máquinas siempre acelera un programa.

La pregunta de gerencia será: **¿cuántas noches reservadas aparecen en el fichero para cada hotel?** No son necesariamente noches cobradas ni habitaciones ocupadas en una fecha: el CSV no contiene estado del pago ni calendario de ocupación.

## MapReduce, con reservas (no con el Quijote)

Una suma por hotel puede dividirse porque la suma de enteros es asociativa: sumar primero cada grupo y después sus resultados produce el mismo total. MapReduce organiza ese trabajo en tres fases.

### Map: transformar cada registro

Partimos del [CSV de la práctica](../assets/practicas/hotel-hadoop/reservas.csv):

```csv
id_reserva,hotel,canal,noches,importe
1,Laredo,web,3,186.50
2,Laredo,ota,2,124.00
3,Potes,recepcion,5,410.00
```

El mapper selecciona `hotel` como clave y `noches` como valor. Emite `Laredo → 3`, `Laredo → 2` y `Potes → 5`, utilizando un tabulador entre clave y valor.

Cada tarea map procesa un **input split**, una división lógica de la entrada. Con texto divisible, los splits suelen guardar relación con los bloques HDFS, pero **bloque y split no son sinónimos**. El formato y la compresión pueden cambiar el reparto. Tampoco hay un mapper por máquina: una máquina puede ejecutar varias tareas, simultáneamente o por turnos.

### Shuffle y sort: reunir la misma clave

Dos mappers pueden emitir `Laredo`. Hadoop envía todos los pares de esa clave al mismo reducer y los ordena por clave. Esta fase consume red, memoria y, a menudo, disco.

El **particionador** determina qué reducer recibe cada clave. Aunque configuremos diez reducers, todos los valores de Laredo siguen llegando al mismo. Si casi todos los registros pertenecen a ese hotel, aparece un desequilibrio de carga o *skew*: un reducer concentra casi todo el trabajo.

### Reduce: agregar y escribir

El reducer recibe claves consecutivas y acumula sus valores. Cuando cambia de hotel, escribe el total anterior y reinicia el acumulador. Para las tres líneas anteriores obtendría `Laredo → 5` y `Potes → 5`.

La salida se escribe en HDFS. Puede haber varios ficheros `part-*`: debemos leerlos todos. `_SUCCESS` indica finalización correcta, pero **no demuestra que nuestra fórmula sea correcta**. Eso se comprueba con un cálculo independiente.

Un **combiner** puede sumar parciales antes del shuffle y reducir tráfico. Es válido para esta suma, pero no para calcular una media como «media de las medias»: grupos de distinto tamaño pesarían igual. Para una media se transportan **suma y número de valores** y se divide al final.

!!! note "Cuándo elegir otro modelo"
    MapReduce encaja en recorridos por lotes y agregaciones. Los algoritmos iterativos pueden pagar repetidamente el coste de materializar resultados. Spark permite reutilizar datos en memoria cuando hay capacidad, aunque también puede escribir a disco. Elegimos según el algoritmo y los recursos.

## YARN: quién presta la CPU

HDFS localiza los datos; **YARN administra los recursos**; MapReduce expresa cómo transformarlos.

| Pieza | Responsabilidad | Duración |
| --- | --- | --- |
| ResourceManager | Admite aplicaciones y administra recursos del clúster | Servicio permanente |
| NodeManager | Lanza y supervisa tareas en un nodo | Servicio permanente |
| ApplicationMaster | Coordina una aplicación y solicita recursos para sus tareas | Mientras dura la aplicación |
| Contenedor YARN | Asignación de RAM y núcleos virtuales | Mientras la necesita una tarea o el AM |

Un contenedor YARN **no es necesariamente un contenedor Docker**. Docker aloja los servicios del laboratorio; dentro, YARN administra las asignaciones de las tareas.

1. El cliente envía el trabajo y sus ficheros auxiliares.
2. YARN reserva recursos para el ApplicationMaster.
3. El AM solicita contenedores para maps y reduces, intentando aprovechar la cercanía de los datos.
4. Los NodeManagers ejecutan las tareas y comunican su estado.
5. El AM coordina la finalización y se publica la salida en HDFS.

El ResourceManager contiene un **Scheduler**, que asigna recursos, y un componente que gestiona las aplicaciones. No corrige errores de Python. El framework puede reintentar tareas fallidas: no debemos realizar cobros ni enviar correos desde un mapper, porque esos efectos externos podrían repetirse.

En Hadoop 1, JobTracker y TaskTracker asumían las funciones de ejecución. YARN separa recursos y programación y permite otros motores, como Spark. Añadir workers puede mejorar la concurrencia si existen tareas independientes y no domina otro cuello de botella.

## Comprobar el poder (qué hacer en el lab)

### Preparar una entrada común

Trabaja con `reservas.csv`, [mapper_noches.py](../assets/practicas/hotel-hadoop/mapper_noches.py) y [reducer_noches.py](../assets/practicas/hotel-hadoop/reducer_noches.py), en `docs/assets/practicas/hotel-hadoop`. **No sustituyas el CSV por uno de UT1 sin adaptar las columnas**: aquellos ejercicios pueden incluir `entrada` o `id_hotel` en otras posiciones.

| Campo | Contrato | Uso |
| --- | --- | --- |
| id_reserva | Identificador entero | Identifica la fila |
| hotel | Texto no vacío | Clave de agrupación |
| canal | Texto | No interviene en la suma |
| noches | Entero positivo | Valor que sumamos |
| importe | Número decimal | No interviene en la suma |

Hay una reserva por línea física y una cabecera. El procesamiento por líneas de Streaming no admite sin adaptación campos CSV con saltos de línea internos.

### Verificar primero en local

Los scripts enlazados contienen el código completo. El mapper usa `csv.reader`, omite la cabecera y rechaza registros incompatibles en vez de descartarlos silenciosamente. El reducer conserva solo la clave actual y su suma.

En **PowerShell**, desde la carpeta de prácticas:

```powershell
Get-Content reservas.csv | python mapper_noches.py | Sort-Object | python reducer_noches.py
```

En **Bash**:

```bash
python3 mapper_noches.py < reservas.csv | sort | python3 reducer_noches.py
```

`sort` representa la agrupación que hará Hadoop. Estas tuberías sirven para el fichero pequeño; la ordenación local de un fichero grande también consume recursos.

Con las 20 reservas originales, debes obtener:

| Hotel | Noches |
| --- | ---: |
| Comillas | 11 |
| Laredo | 12 |
| Noja | 15 |
| Potes | 14 |
| Santander | 10 |
| **Total** | **62** |

Comprueba con este programa independiente, guardado como `comprobar.py` en esa carpeta:

```python
import csv
from collections import Counter

totales = Counter()
with open("reservas.csv", encoding="utf-8", newline="") as fichero:
    for fila in csv.DictReader(fichero):
        totales[fila["hotel"]] += int(fila["noches"])
print(dict(sorted(totales.items())))
assert sum(totales.values()) == 62
```

También puedes usar pandas o un `GROUP BY hotel` en DuckDB sobre **el mismo fichero**. Las 62 noches corresponden exclusivamente al CSV pequeño sin modificar.

### Ejecutar el mismo cálculo en Hadoop

Arranca el laboratorio del [2.2](ecosistema.md). La carpeta de prácticas está montada en `/practicas`. Entra con `docker compose exec namenode bash`. Ejecuta allí:

```bash
cd /practicas
hdfs dfs -mkdir -p /user/bda
hdfs dfs -put -f reservas.csv /user/bda/reservas.csv
mapred streaming \
  -files mapper_noches.py,reducer_noches.py \
  -mapper "python3 mapper_noches.py" \
  -reducer "python3 reducer_noches.py" \
  -input /user/bda/reservas.csv \
  -output /user/bda/salida_noches_01
hdfs dfs -cat '/user/bda/salida_noches_01/part-*'
```

Antes, comprueba desde el host `docker compose exec nodemanager python3 --version`: Python debe estar instalado donde se ejecutan las tareas. Si falta, utiliza la imagen preparada por el docente con Python 3. `-files` distribuye los scripts, **no instala dependencias**.

La salida debe ser una carpeta nueva. Usa `salida_noches_02` al repetir para conservar la comparación. Comprueba el estado final en YARN, los contadores y los cinco totales.

### Medir sin cambiar dos variables a la vez

El fichero pequeño verifica el algoritmo. Para estudiar paralelismo, usa [generar_reservas_grandes.py](../assets/practicas/hotel-hadoop/generar_reservas_grandes.py). Consulta el tamaño real y `hdfs fsck`: no deduzcas los bloques solo del número de filas.

Mantén entrada, código y opciones salvo el recurso que estudias. Haz una ejecución de calentamiento y tres mediciones por configuración.

| Configuración | Bytes / registros | Maps y reduces | Concurrencia observada | Tiempo total | Resultado correcto |
| --- | --- | --- | --- | --- | --- |
| Recursos iniciales | Medición | Contadores | UI YARN | Mediana de 3 pruebas | Sí / no |
| Más recursos | Los mismos | Contadores | UI YARN | Mediana de 3 pruebas | Sí / no |

La **aceleración** es `tiempo inicial / tiempo nuevo`: pasar de 120 a 80 segundos da 1,5. El arranque, el shuffle, el disco y las partes secuenciales limitan la ganancia.

!!! warning "Qué demuestra el mini-clúster"
    El Compose básico tiene un DataNode y un NodeManager en un ordenador. Permite observar roles y tareas, pero no demuestra reparto entre máquinas físicas ni aceleración al añadir servidores. Con pocos datos puede tardar más que el cálculo local. Registra y explica ese resultado: es una conclusión válida.

### Entrega y comprobaciones

Entrega la identificación y tamaño de la entrada, comandos, contadores, resultados comparados y una interpretación de los tiempos. Sin más workers, documenta lo observado y qué experimento adicional necesitarías. No presentes «varios maps» como prueba de que había varias máquinas.

Para cerrar: ¿qué cambia si todas las reservas son de Laredo?, ¿por qué no sumamos medias sin sus tamaños?, ¿por qué `_SUCCESS` no valida la fórmula? Las respuestas conectan el algoritmo con el comportamiento del sistema.
