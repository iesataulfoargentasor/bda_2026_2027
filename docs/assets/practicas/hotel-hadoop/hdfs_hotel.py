#!/usr/bin/env python3
"""Lectura/escritura de HDFS con PyArrow (hotel). Ajustad host y puerto del aula."""
import pandas as pd
from pyarrow import fs

HDFS_HOST = "localhost"
HDFS_PORT = 9000  # RPC nativo; WebHDFS/UI usa 9870

hdfs = fs.HadoopFileSystem(host=HDFS_HOST, port=HDFS_PORT)

fichero = "/user/bda/opiniones.txt"
with hdfs.open_input_stream(fichero) as reader:
    texto = reader.read().decode("utf-8")
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
