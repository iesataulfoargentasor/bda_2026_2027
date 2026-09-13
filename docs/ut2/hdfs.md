---
title: 2.3 HDFS
tags:
  - Big Data
  - BDA
  - RA2
---

# 2.3. HDFS

El **Hadoop Distributed File System** es la carpeta del clúster. Parte de la idea del *Google File System* (2003): muchos discos baratos, **réplicas**, y un maestro que **solo** guarda el mapa.

Cumple de golpe varios criterios: **deposita cualquier fichero** (a), **tolera** que se muera un disco (c), **guarda ahora y lees después** (d) y **crece** enchufando *datanodes* (e).

## Idea en el hotel

Subes `reservas_2024.parquet` (600 MB). HDFS lo corta en **bloques** (por defecto **128 MB**). Un fichero de 600 MB → 5 bloques. Cada bloque se copia **tres veces** (factor de réplica 3) en máquinas distintas. Si un disco de Laredo se quema, quedan dos copias.

Filosofía **WORM**: *write once, read many*. Escribes (o **añades** al final). No editas el byte 17 del medio como en un Word. Para “cambiar” un lago se **escriben ficheros nuevos** (o usas Hive/HBase encima).

**No** es el sitio para:

- el clic de recepción (poca latencia);
- millones de ficheros de 2 KB (el NameNode se ahoga en metadatos);
- diez escritores a la vez sobre el mismo archivo;
- un `UPDATE` fila a fila.

Un fichero **menor** de 128 MB ocupa **un** bloque lógico, pero en disco solo los bytes reales (1 MB ocupa 1 MB, no 128).

## NameNode y DataNode

| Rol | Qué guarda | Si cae |
| --- | --- | --- |
| **NameNode** | El **árbol** (`/user/bda/…`) y **dónde** está cada bloque. Mucha RAM. **Los bytes no pasan por él** | Sin él no hay HDFS. Por eso copias de seguridad y, en producción, alta disponibilidad |
| **DataNode** | Los **bloques** y un *checksum*. Informa al NameNode de lo que tiene | El clúster sigue; se re-replican los bloques que solo estaban ahí |
| **Secondary NameNode** | Ayuda a compactar metadatos (`fsimage` + `edits`). **No** es un NameNode de reserva automático | Confusión clásica de examen: no es el “espejo caliente” |

Réplicas y **racks**: con factor 3 suele haber dos copias en un armario y una en **otro**, por si se cae el *switch* entero.

### Cómo se lee (el cliente no traga por el maestro)

1. El cliente pide abrir el fichero.
2. El NameNode responde: “el primer bloque está en estos DataNodes” (ordena por **cercanía**).
3. El cliente **lee del DataNode**, no del NameNode.
4. Si un nodo falla o el CRC no cuadra, prueba la **siguiente** réplica.

Por eso escala: el tráfico se **reparte**. El maestro no es un *router* de petabytes.

### Cómo se escribe (tubería de réplicas)

1. El cliente crea el fichero; el NameNode comprueba permisos y elige DataNodes.
2. Los datos van en una **tubería**: nodo A guarda y reenvía a B; B a C (si la réplica es 3).
3. Cuando los tres confirman, el bloque cuenta.
4. Al cerrar, el NameNode anota el mapa final.

## Metadatos por dentro

En disco del NameNode conviven:

- **`fsimage`:** foto del árbol;
- **`edits`:** diario de cambios.

Al arrancar se mezclan. El *Secondary* va haciendo fotos nuevas para que el arranque no dure una eternidad. No hace falta recitar rutas de `hdfs-site.xml`; sí saber que **el diario existe**.

## Comandos de aula (`hdfs dfs`)

`hdfs dfs` habla con HDFS. `hadoop fs` es el cliente **genérico** (local, S3…). En versiones viejas existía `hadoop dfs`; hoy, **`hdfs dfs`**.

```text
hdfs dfs -ls /
hdfs dfs -mkdir -p /user/bda/reservas
hdfs dfs -put reservas_2024.csv /user/bda/reservas/
hdfs dfs -ls /user/bda/reservas
hdfs dfs -cat /user/bda/reservas/reservas_2024.csv | more
hdfs dfs -get /user/bda/reservas/reservas_2024.csv ./copia.csv
hdfs dfs -rm -r /user/bda/reservas/tmp
```

| Acción | Flag típico |
| --- | --- |
| Subir | `-put` / `-copyFromLocal` |
| Bajar | `-get` / `-copyToLocal` |
| Fusionar al bajar | `-getmerge` |
| Ver | `-cat`, `-head`, `-tail` |
| Contar | `-count` |
| Copiar / mover / borrar | `-cp`, `-mv`, `-rm` |

Permisos al estilo POSIX. Suele crearse `/user/…` como el `/home` de Linux. Al bajar, `-crc` pide el *checksum* para comprobar que el viaje no corrompió.

En el lab, cambiad `bda` por el usuario de **vuestra** máquina.

## Crecer (criterio e)

Añades un DataNode, lo das de alta, y el equilibrador **mueve bloques** hacia el disco nuevo. Capacidad y paralelismo **suben**. No tocas el JSON de 2023.

## Decidir el uso después (criterio d)

Dejas el bruto en `/user/bda/crudo/`. Dentro de un año Spark lee solo tres columnas. No hiciste un esquema rígido el día 1. Hive o un job pueden **interpretar** el fichero al leer.

## Python (idea)

Con el clúster del aula y las librerías que indique el profesor (`hdfs`, PyArrow) puedes **escribir un Parquet** en una ruta `hdfs://…`. El oficio es el de [1.7](../ut1/formatos.md): la **L** del ETL aterriza en HDFS, no en `C:\Users\…`.

!!! tip "Comprobar tolerancia (c)"
    En un lab controlado: sube un fichero, mira `hdfs fsck` o la UI, **para** un DataNode de prueba (con permiso) y verifica que el fichero **sigue leyéndose**. Eso es “probar” el criterio, no solo recitar “factor 3”.

Interfaces: la **UI del NameNode** (puerto que diga el lab) y a veces **Hue**. Sirven para *ver* bloques y réplicas; el examen oral se aguanta sin ellas.
