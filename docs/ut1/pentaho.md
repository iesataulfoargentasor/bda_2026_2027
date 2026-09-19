---
title: 1.8 Pentaho
tags:
  - Big Data
  - BDA
  - RA1
  - Pentaho
---

# 1.8. Pentaho: procesar y presentar

Los criterios **d)** y **e)** del RA1 se cierran aquí: **procesar** el dato ya almacenado y **enseñárselo** a alguien que no abre Spoon.

En el aula usamos **Pentaho Data Integration (PDI / Kettle)**, de Hitachi Vantara. No sustituye a Spark en un clúster de petabytes. Sí te deja **ver** un [ETL](ingesta.md): extraer, filtrar, unir, agregar y cargar **sin programar el motor**.

El PDF de prácticas (capturas y clics): [Pentaho.pdf](../assets/originales/Pentaho.pdf). Esta página cuenta **qué competencia** entrenas en cada taller, con **otros ficheros** (hotel en Cantabria) para que el flujo no sea una receta calcada. Los pasos de Spoon se llaman igual; cambia el caso.

Los CSV y el SQL de esta página:

| Fichero | Taller |
| --- | --- |
| [alojamientos_cp.csv](../assets/practicas/alojamientos_cp.csv) | 1 |
| [reservas_pdi.csv](../assets/practicas/reservas_pdi.csv), [cobros_pdi.csv](../assets/practicas/cobros_pdi.csv), [hoteles_pdi.csv](../assets/practicas/hoteles_pdi.csv) | 2 |
| [cadenas_pdi.csv](../assets/practicas/cadenas_pdi.csv) | 4 |
| [alojamientos_opiniones.csv](../assets/practicas/alojamientos_opiniones.csv) | 3 |
| [incidencias.csv](../assets/practicas/incidencias.csv), [incidencias2.csv](../assets/practicas/incidencias2.csv), [hotel_pdi.sql](../assets/practicas/hotel_pdi.sql) | 6 |

## Qué es PDI (y qué no)

Pentaho es una plataforma de integración y análisis. **PDI** es la pieza ETL: un lienzo donde arrastras pasos y el motor mueve las filas.

Se llama herramienta de **metadatos** porque tú declaras *qué* tiene que ocurrir (leer este CSV, filtrar Trasmiera, escribir allí). El *cómo* (buffers, tipos, paralelismo interno) lo resuelve Kettle. Por eso el flujo se guarda en XML (`.ktr` / `.kjb`) y se puede ejecutar igual en tu Windows y en un servidor sin pantalla.

Con Spoon, sin escribir el motor:

- conectar orígenes (CSV, Excel, XML, JSON, SQL, APIs);
- filtrar, limpiar, tipar, *lookup*, *merge join*, agregar, fórmulas;
- cargar a fichero, tabla o nube;
- esbozar un almacén en **estrella** (hechos / dimensiones) para informes [OLAP](procesamiento.md).

**No** es el programa de recepción: no picas la reserva en PDI. Procesas una **copia**.

| Característica | En el aula |
| --- | --- |
| Multiplataforma | Windows, Linux, macOS |
| Community / comercial | En clase, Community; la empresa puede pagar soporte |
| Motores SQL | PostgreSQL viene; MySQL/MariaDB piden el `.jar` en `lib` |
| Escala | Local, programada o en un servidor. Petabytes → otro stack |

!!! warning "Versión y Java"
    Usa la versión de PDI que indique el aula (en los apuntes de prácticas se trabaja con la **9.4** Community). PDI 9.x espera **Java 8**. Si Spoon no arranca, lo primero es `java -version`, no “reinstalar Windows”. En Windows: descomprime el zip y lanza `spoon.bat`. En Linux: `spoon.sh` (puede hacer falta un JDK 8 y, en algunas distros antiguas, una librería WebKit; el profesor te dirá el paquete de vuestro lab).

Descarga Community (Hitachi / espejos que indique el aula): el zip típico se llama `pdi-ce-9.4.0.0-343.zip` o `pme-ce-…`. No hace falta registrarse en todos los espejos.

## Tres ejecutables que se confunden

| Pieza | Analogía | Qué lanza | Fichero |
| --- | --- | --- | --- |
| **Spoon** | El taller | Diseñar (arrastrar pasos) | `.ktr` y `.kjb` |
| **Pan** | El obrero de *una* pieza | Una **transformación** sin ventana | `.ktr` |
| **Kitchen** | El capataz | Un **job**: orden, condiciones, abortar | `.kjb` |

Spoon es para **clase y diseño**. En producción (o en la entrega “como en empresa”) lanzas **Pan** o **Kitchen**. Si solo funciona cuando pulsas Play, el procedimiento no está cerrado.

!!! example "Regla"
    ¿Un solo flujo leer → filtrar → escribir? → transformación → **Pan**.  
    ¿“Si no está el CSV, aborta; si está, borra el informe viejo y lanza dos transformaciones”? → job → **Kitchen**.

En PDI hay **dos** tipos de diseño:

- **Transformación:** el dato **cambia** (filas in, filas out).
- **Job:** **orquesta** (¿existe el fichero? ¿falló el paso anterior?).

Al conectar dos pasos, Spoon pregunta a menudo:

- **Main output of step:** el camino bueno.
- **Error handling of step:** qué haces si *este* paso revienta.

El lienzo (árbol de categorías a la izquierda, zona de trabajo, panel de *Logging* / métricas abajo) es el mismo en todos los talleres. El menú emergente sobre un paso (editar, previsualizar, conectar salida) lo usarás hasta el cansancio.

## Criterio d) y criterio e)

Has **procesado** (d) cuando la salida **no es** la entrada: menos filas, columnas con nombre de negocio, un agregado, un JSON que otra app entiende.

El cliente **no** abre Spoon. “Fácil de interpretar” (e) es:

- un CSV con **cabeceras claras** y solo las columnas pedidas,
- un JSON coherente,
- una **tabla** que Power BI o un informe ya entienden,
- un **agregado** (importe por comarca) en lugar de veinte mil reservas crudas.

!!! tip "Prueba del cliente"
    Cierra Spoon. Abre el fichero como lo abriría alguien de empresa: Excel, un visor JSON, una consulta SQL. Si tiene que preguntarte “¿qué es `id_cadena`?”, el **e)** no está cerrado.

## Cómo atacar cada taller

1. Escribe en una **nota** del lienzo (botón derecho → *New Note*) la pregunta del cliente y **tu nombre**.
2. Marca origen, la T **mínima** y el destino. Si no cabe en una frase, el flujo está sobrado o incompleto.
3. **Preview** (ojo de la barra o clic derecho): 1000 filas por defecto. Ahí cazas el nulo y el tipo raro. *Stop* para cortar.
4. Mira las métricas. En el log verás letras del estilo `I` (input), `O` (output), `R` (read), `W` (written), `U` (updated), `E` (errors). `E=1` no es un detalle: es una fila que no hizo lo que pediste.
5. Vuelve a ejecutar con **Pan** o **Kitchen**.
6. Abre el artefacto **sin Spoon**.

Rutas: no dejes `C:\Users\tú\...` tapadas si el `.ktr` tiene que correr en el aula. Usa una carpeta de trabajo acordada o variables.

!!! warning "Nube y secretos"
    Credenciales de AWS o Azure **nunca** van en el `.ktr` que subes a Moodle ni en un repo. Variables de entorno, no capturas del `appId` / `password`. Un *bucket* público con `s3:*` y `Principal: *` es un ejemplo de **qué no** dejar en producción.

---

## Taller 0 — Que Spoon hable

Objetivo: una transformación que **no** lee un CSV. Compruebas que PDI arranca y ves la versión.

1. *File → New → Transformation* (o `Ctrl+N`).
2. Categoría **Input** → **Get system info** (*Información del sistema*). Doble clic: un campo `Version_PDI` alimentado de *Kettle Version*.
3. Categoría **Utility** → **Write to log**. Conecta la salida del primero al segundo (cuarta opción del menú emergente: nueva conexión).
4. *Run* o `F9`. El panel *Logging* debe mostrar la versión.

Si esto falla, no pases al taller 1: el entorno no está listo.

---

## Taller 1 — Filtrar, ordenar, persistir y Pan

Cliente: *“Listado de alojamientos de la comarca **Trasmiera**, ordenados por código postal, en un CSV limpio.”*

Fichero: [alojamientos_cp.csv](../assets/practicas/alojamientos_cp.csv) (`hotel`, `comarca`, `codigo_postal`).

### Leer

1. Nueva transformación.
2. **CSV file input**. Ruta al CSV. *Get fields* / *Traer campos*: comprueba nombres y tipos.
3. *Preview*: deben salir filas de Santander, Liébana, Trasmiera…

### Filtrar

**Flow → Filter rows.** Al soltar el hop elige *Main output of step*. Condición: `comarca = Trasmiera` (el texto tiene que coincidir; `trasmiera` no vale).

Preview sobre el filtro: solo Laredo, Noja, Santoña, Isla… *Stop* cuando valgas.

### Ordenar y un error a propósito

**Transform → Sort rows.** Campo `codigo_postal`.

Para ver cómo avisa Spoon: escribe `CP` en vez de `codigo_postal`. Preview: icono de prohibido, log y métricas con el campo inexistente. Corrige. Así dejas de “adivinar” el nombre.

### Escribir

**Output → Text file output.** Conecta desde el *Sort*. Primera ejecución: a menudo **rellena con espacios** (anchura fija). Pestaña *Fields* → **Minimal width**. Segunda ejecución: `Mirador Laredo;Trasmiera;39770` sin cola de blancos.

Has **procesado** (menos filas, ordenadas) y **presentado** (CSV que se abre en Excel).

### Pan (sin Spoon)

Guarda `taller1_trasmiera.ktr`. Borra el CSV de salida. En la carpeta de PDI:

```text
pan.bat /file="C:\ruta\taller1_trasmiera.ktr"
```

En Linux/macOS: `pan.sh /file=...`. El log debe terminar en *Finished* y el fichero debe **reaparecer**. Eso es el procedimiento de madrugada.

Parámetros útiles (también en Kitchen): `/level:Basic` (o `Error`, `Debug`, `Rowlevel`…) y `/param:"nombre=valor"` si el flujo espera variables.

---

## Taller 2 — Unir dos orígenes y agregar

Cliente: *“Importe cobrado y número de reservas **por hotel y canal**. Las que aún no tienen cobro no entran.”*

Es el mismo oficio que el [Hola ETL](ingesta.md#hola-etl) de ingesta (reservas + cobros), ahora en Spoon.

| Fichero | Separador | Rol |
| --- | --- | --- |
| [reservas_pdi.csv](../assets/practicas/reservas_pdi.csv) | coma | Hecho (estancia) |
| [cobros_pdi.csv](../assets/practicas/cobros_pdi.csv) | **punto y coma** | Cobro |
| [hoteles_pdi.csv](../assets/practicas/hoteles_pdi.csv) | punto y coma | Dimensión (nombre y comarca) |

1. Dos (o tres) **CSV file input**. En cobros y hoteles, `Delimiter = ;`.
2. En reservas, si algún código se interpreta como número y se come ceros, fuerza **String** en ese campo (*Get fields* y corrige el tipo).
3. **Join → Merge join.** Enlaza desde el *Merge* hacia cada origen: uno *left*, otro *right*. Clave: `id_reserva` (reservas ⋈ cobros). Tipo *INNER* si solo quieres cobradas.

Spoon **avisa**: si los flujos no están **ordenados por la clave**, el join miente. Añade **Sort rows** por `id_reserva` **en cada rama** *antes* del merge. Preview del merge: deben aparecer `hotel` aún no (si no has unido la dimensión) y `cobrado`.

4. Tercer origen `hoteles_pdi.csv` + otro *Merge join* por `id_hotel` (otra vez: **ordenar ambas entradas** por `id_hotel`).
5. **Statistics → Group by.** Agrupa por `hotel` y `canal`. Agregados: `SUM(cobrado)`, `COUNT` de `id_reserva` (o `SUM(noches)` si el cliente pide noches).
6. El *Group by* también quiere el flujo **ordenado** por las columnas de agrupación. *Sort* por `hotel`, `canal` entre el merge y el grupo.
7. **Text file output** → `informe_hotel_canal.csv`.

Criterio **e):** gerencia lee **unas pocas filas** (hotel × canal), no el cruce fila a fila.

---

## Taller 3 — Limpiar, filtrar en serio y JSON

Cliente: *“Alojamientos para un escaparate web: no habitación privada, precio real menor de 200 €, estancia mínima de 4 noches o menos. En JSON, claves en castellano.”*

Fichero: [alojamientos_opiniones.csv](../assets/practicas/alojamientos_opiniones.csv). Hay **nulos** a propósito (`puntuacion`, `estancia_min`) y un precio `-1`.

### Leer y elegir columnas

**CSV file input**, separador `,`. *Get fields*: `precio` y `puntuacion` como **Number**; `id`, `dormitorios`, `huespedes` como Integer.

**Transform → Select values:** quédate con `id`, `tipo`, `comarca`, `dormitorios`, `puntuacion`, `huespedes`, `precio`, `estancia_min` y renombra, por ejemplo:

| Original | Salida |
| --- | --- |
| `id` | `alojamiento_id` |
| `tipo` | `alojamiento_tipo` |
| `comarca` | `comarca` |
| `precio` | `precio` |
| `estancia_min` | `noches_min` |

### Nulos

Un **Java Filter** que compare `noches_min < 4` **revienta** si el campo es nulo (el PDF de prácticas lo deja claro con otro dataset).

**Utility → If field value is null.** Sustituye nulos de `precio` y `noches_min` por `-1`. Luego el filtro **debe** excluir esos `-1`: no los cueles como “baratos”.

### Filtro simple y filtro Java

**Filter rows** basta para `precio < 200`. Condiciones con `&&` / `||` y texto se leen mejor en **Flow → Java Filter**. Ejemplo (ajústalo a *tus* nombres de campo):

```text
(precio >= 0 && precio < 200) && (noches_min >= 0 && noches_min <= 4) && !alojamiento_tipo.equals("Habitacion privada")
```

Puedes poner **Dummy** en la rama que no cumple (no hace nada; cierra el camino) y la salida JSON en la que sí.

### JSON

**Output → JSON output.**

- *Filename:* ruta de `escaprate_cantabria.json`.
- *Json bloc name:* p. ej. `alojamientos`.
- *Nr rows in a bloc:* `0` = un solo documento con todos; `1` = un fichero por fila (casi nunca lo quieres aquí).
- Pestaña *Fields* → **Get fields**. Si no, el JSON sale con objetos vacíos.

Ejecuta. Abre el JSON **sin Spoon**. Si un compañero de DAW entiende las claves, el **e)** va bien.

---

## Taller 4 — Fórmula y dejar el informe en la nube

Cliente: *“Por **cadena** hotelera: noches cobradas, importe cobrado y **precio medio por noche**. El CSV tiene que acabar en el almacenamiento del centro (S3 o Azure).”*

Partes del taller 2 (reservas ⋈ cobros ⋈ hoteles). Añades [cadenas_pdi.csv](../assets/practicas/cadenas_pdi.csv):

1. CSV de cadenas (`;`) → *Sort* por `id_cadena`.
2. *Sort* del flujo de hoteles por `id_cadena`.
3. **Merge join** `id_cadena`.
4. *Sort* por `cadena` → **Group by:** `id_cadena`, `cadena`; `SUM(noches)`, `SUM(cobrado)`.
5. **Transform → Calculator.** Operación *A/B* (o la equivalente en tu versión): `importe_total / noches_total` → `precio_medio_noche`. Recorre el desplegable: hay texto, fechas y números; no memorices la lista.

### Destino S3 (si el aula usa AWS)

1. *Bucket* del **centro** (el nombre lo da el profesor; no copies el de otro ciclo).
2. Credenciales por **variables de entorno** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, y si aplica `AWS_SESSION_TOKEN`) o el perfil `~/.aws/credentials`.
3. Paso **S3 file output**. La URI suele ir en la forma `s3n://s3n/NOMBRE-BUCKET/informeCadenas` y extensión `csv`.

Una política `Principal: *` + `s3:*` deja el cubo abierto al mundo. En clase, si os la muestran, es para que el paso *funcione*; **no** es el diseño de una empresa.

### Destino Azure (cuenta de estudiante)

El PDF de prácticas desarrolla este camino (cuenta de almacenamiento → contenedor → subida). En resumen:

1. En Azure: grupo de recursos → **cuenta de almacenamiento** → **contenedor**.
2. En el PC: Azure CLI (`winget install -e --id Microsoft.AzureCLI`), cierras y abres PowerShell, `az version`.
3. Para automatizar: un *service principal* con rol **Storage Blob Data Contributor** *sobre vuestro* ámbito; `az login --service-principal` con `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID` en variables de entorno. **No** pegues esos valores en el apunte ni en Git.
4. Subida idempotente:

```bash
az storage container create --account-name TU_CUENTA --name practicas-bda --auth-mode login --only-show-errors
az storage blob upload --account-name TU_CUENTA --container-name practicas-bda --file informe_cadenas.csv --name informe_cadenas.csv --overwrite true --auth-mode login
```

Alternativa: token **SAS** (sin `az login`). Caduca; no lo subas a un repo.

En Spoon, si vuestra versión trae paso de Azure Blob, úsalo con las mismas precauciones. Si no, el job (taller 5) puede llamar a un script *después* de generar el CSV local.

Has procesado (d: agregas y calculas) y presentado (e: tres números por cadena, en un sitio que gerencia ya usa).

---

## Taller 5 — Un job que no se miente

Cliente: *“De madrugada: si ya existe el informe del taller 2, bórralo; regenera 2; si ese CSV **no** apareció, **para**; luego el 4 (nube).”*

1. *File → New → Job.*
2. **General → Start.**
3. **Conditions → File exists** sobre `informe_hotel_canal.csv`.
4. Si existe: **Delete files** + (opcional en clase) **Display msgbox info** “He borrado el informe viejo”. En un servidor **sin ventana**, el *msgbox* estorba: en la entrega “empresa” quítalo.
5. **General → Transformation:** el `.ktr` del taller 2. Une tanto la rama “no existía” como la de “ya lo borré” a esta transformación.
6. Otro **File exists** sobre el CSV que **debe** haber dejado el 2. Si no está: **Utility → Abort job**. Así no das por bueno un panel vacío.
7. Segunda **Transformation** (taller 4). Si comprobáis objeto en S3/Azure, el mismo *File exists* admite esquema S3 (URL del *bucket*) en muchas versiones; si no, un paso *Shell* / script del aula.

Guarda `taller5_noche.kjb`.

```text
kitchen.bat /file="C:\ruta\taller5_noche.kjb" /level:Basic
```

Linux: `kitchen.sh /file=taller5_noche.kjb`.

---

## Taller 6 — Hablar con una base de datos

Cliente: *“Las incidencias del mostrador llegan en CSV; los nombres están en la tabla de huéspedes. Inserta el cierre, actualiza si ya existía, y si el id no está, que se vea **por qué** falló.”*

En el PDF aparece un ejemplo con RDS y un esquema deportivo. Aquí el esquema es el **hotel**, en **local** (PostgreSQL o MariaDB). RDS vale si el profesor lo monta; el oficio no cambia.

### Preparar

1. Crea una base `hotel_pdi` y ejecuta [hotel_pdi.sql](../assets/practicas/hotel_pdi.sql) (tabla `huespedes` + `fases_incidencia`).
2. PDI trae driver de **PostgreSQL**. Para MySQL/MariaDB: copia un conector JDBC **compatible con vuestra 9.4** en la carpeta `lib` de PDI y **reinicia Spoon**. El “último jar del universo” a veces no carga.
3. *File → New → Database connection.* Host `localhost`, base, usuario de **aula**. Prueba la conexión.

### Lookup (enriquecer el CSV)

Lee [incidencias.csv](../assets/practicas/incidencias.csv) (`id_huesped;tipo;fecha`).

La tabla `huespedes` tiene `tipo = huesped`. Si el lookup necesita las dos columnas:

1. **Transform → Add constants:** `tipo_entidad` = `huesped`.
2. **Lookup → Database lookup:** claves `id_huesped` + `tipo_entidad` → `nombre` (y lo que pidas).

Preview: nombres de Ana, Luis… Si un id no existe, los campos salen **nulos**. Marca *Do not pass the row if the lookup fails* si no quieres esa fila en el flujo bueno.

### Insertar

Misma lectura. **Get system info:** campo `sysdate` = fecha/hora del sistema (el cierre “termina ahora”).

**Output → Table output** → `fases_incidencia`. *Get fields* y mapea `id_huesped`, `tipo`, `fecha` → `fecha_inicio`, `sysdate` → `fecha_fin`.

Comprueba en SQL:

```sql
SELECT * FROM fases_incidencia ORDER BY fecha_fin DESC;
```

### Actualizar y ver el error

Lee [incidencias2.csv](../assets/practicas/incidencias2.csv). **Output → Update:** claves de búsqueda (`id_huesped`, `fecha`); campos a pintar (`tipo`, `lado`, `comentario`).

La fila `id_huesped = 99` **no está** en `huespedes` / no hay fase previa. El log dirá algo como `E=1`. Clic derecho en el *Update* → **Error handling…**: rellena *Error description fieldname* y *Error fields fieldname*. Conecta esa salida a **Write to log**. Al repetir verás *qué* clave falló, no solo “ha habido un error”.

### Upsert

Si en vez de fallar quieres **insertar** lo que no exista: **Insert / Update** (no es el mismo paso que *Update*). Eso es la carga diaria que no duplica la clave.

---

## Mapa de pasos ↔ criterios

| Taller | Pasos que tienes que saber nombrar | d / e |
| --- | --- | --- |
| 0 | Get system info, Write to log | Entorno |
| 1 | CSV input, Filter, Sort, Text file output, **Pan** | d + e (CSV) |
| 2 | Merge join, Sort (obligatorio), Group by | d + e (agregado) |
| 3 | Select values, If null, Java Filter, JSON output | d + e (JSON) |
| 4 | Merge extra, Calculator, S3 o Azure | d + e (nube del BOE) |
| 5 | Start, File exists, Delete, Abort, Transformation, **Kitchen** | Procedimiento |
| 6 | Conexión JDBC, Constant, DB lookup, Table output, Update, Error handling, Insert/Update | d con una BD |

*Upsert* = si la fila existe, actualiza; si no, inserta.

## Errores que se repiten

- Kitchen sobre un `.ktr` o Pan sobre un `.kjb`.
- Filtrar “en la cabeza” y no en un paso: no es reproducible.
- *Merge join* / *Group by* **sin** ordenar por la clave.
- Java Filter + nulos sin *If field value is null*.
- JSON output sin *Get fields*.
- Cumplir d) (el fichero se genera) y olvidar e) (nadie entiende las claves).
- Rutas absolutas de tu usuario en casa.

!!! success "Al terminar la UT1"
    Ante un problema propuesto: almacén (a), ingesta (b), formato (c), **procesar** con PDI u otra herramienta del centro (d) y **enseñar** un resultado que no requiera ser ingeniero (e).

## Para practicar (Moodle manda)

No sustituye a la entrega. Comprueba que lo sostienes en voz alta.

1. Talleres **0 a 3**: `.ktr` + captura del lienzo **con nota** (nombre completo + pregunta del cliente). Abre el CSV/JSON **fuera** de Spoon.
2. Talleres **4 y 5**: el informe de cadenas en el destino que indique el profesor (S3, Azure o carpeta del aula) y el `.kjb` lanzado con Kitchen.
3. Taller **6** (si el aula tiene BD): lookup + insert + update con el error de la fila 99 **explicado** (captura del log).
4. Opcional: el tutorial Community de Hitachi Vantara (lista de correo: limpiar, tipar y cargar un CSV a una tabla). Mismo oficio, otro enunciado.

La entrega, si la hay, es Moodle. No hace falta compartir el `.ktr` fuera del centro.
