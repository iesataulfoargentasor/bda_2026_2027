#!/usr/bin/env python3
"""Lectura/escritura de HDFS con PyArrow (hotel).

En el compose de este módulo el RPC es namenode:8020 (config.env).
El 9000 es el de otras guías. La UI y WebHDFS van por el 9870.
Requiere un cliente Hadoop con Java, libhdfs y classpath configurados,
además de conectividad con NameNode y DataNodes. Publicar solo 9870 en
Windows tampoco basta para WebHDFS: sus lecturas redirigen al DataNode.
"""
import pandas as pd
from pyarrow import fs

HDFS_HOST = "namenode"
HDFS_PORT = 8020

hdfs = fs.HadoopFileSystem(host=HDFS_HOST, port=HDFS_PORT)

fichero = "/user/bda/opiniones.txt"
with hdfs.open_input_stream(fichero) as reader:
    texto = reader.read(200).decode("utf-8", errors="replace")
print(texto[:200])

df = pd.DataFrame(
    {
        "hotel": ["Laredo", "Potes", "Noja"],
        "noches": [12, 9, 7],
        "canal": ["web", "ota", "recepcion"],
    }
)
df.to_parquet("/user/bda/noches_resumen.parquet", filesystem=hdfs, index=False)
print("Parquet escrito en HDFS")
