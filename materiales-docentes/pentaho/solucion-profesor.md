# Solución docente de la práctica integradora de Pentaho

**Referencia para el profesor. Publicada en los materiales docentes del repositorio; su contenido es accesible públicamente.**

La solución responde al encargo del grupo hotelero: generar un informe del dinero cobrado por hotel y canal y un control de reservas sin cobro asociado. Incluye las cuatro transformaciones y el job exigidos en la práctica. Utiliza pasos estándar de PDI y archivos locales. No necesita Python para ejecutarse ni una base de datos.

[Descargar la solución completa en ZIP](solucion-profesor-pentaho.zip) · [Volver a las instrucciones docentes](README.md)

El ZIP contiene los procesos, datos, resultados de referencia y registros de las 25 pruebas. Las rutas de archivos que se indican a continuación corresponden a su contenido una vez descomprimido.

## 1. Qué contiene y cómo abrirla

| Carpeta o archivo | Contenido |
| --- | --- |
| `entrada` | Los tres CSV del paquete A001 sin modificar |
| `asignacion.json` | Identificación y huellas del paquete A001 |
| `procesos/informe_cobros.ktr` | Informe principal |
| `procesos/reservas_sin_cobro.ktr` | Listado de control |
| `procesos/validar_informe.ktr` | Validación automática de cifras |
| `procesos/validar_sin_cobro.ktr` | Validación de los cinco identificadores |
| `procesos/cierre_hotel.kjb` | Orquestación y publicación |
| `temporal` | Archivos provisionales, regenerados en cada ejecución |
| `salida` | Los dos informes publicados por la ejecución |
| `referencia` | Resultados esperados para contrastar; no los lee el proceso |
| `evidencias` | Registros de las pruebas ejecutadas y su resumen |

1. Descomprimir el ZIP completo en una carpeta de trabajo del profesor. No abrir los procesos directamente dentro del ZIP.
2. Usar **PDI Community 9.4.0.0-343**, la versión del aula, con su configuración Java.
3. Confirmar que existen `entrada`, `temporal` y `salida`. El ZIP conserva las carpetas necesarias.
4. En Spoon, abrir `procesos/cierre_hotel.kjb`. Se pueden abrir también los cuatro `.ktr` para examinar los pasos. No se necesita un repositorio interno de Pentaho.
5. Ejecutar el job. Debe terminar correctamente y escribir los dos CSV en `salida`.
6. Compararlos con `referencia`. El contenido debe coincidir; los saltos de línea pueden variar entre sistemas.

Las rutas de las transformaciones parten de `${Internal.Transformation.Filename.Directory}`. Las del job parten de `${Internal.Job.Filename.Directory}`. Se puede mover la carpeta completa sin editar cada entrada. No mover solo los `.ktr` o el `.kjb`.

### Ejecución con Kitchen y Pan

En Windows, desde la consola de la instalación de Pentaho, adaptando únicamente la ubicación del paquete:

```text
kitchen.bat /file:"C:/ruta/solucion-profesor-pentaho/procesos/cierre_hotel.kjb" /level:Basic
pan.bat /file:"C:/ruta/solucion-profesor-pentaho/procesos/validar_informe.ktr" /level:Basic
```

En PowerShell se antepone `&` a la ruta del ejecutable si está entre comillas. En Linux se utilizan `kitchen.sh` y `pan.sh`. Las pruebas documentadas se realizaron en Windows con PDI 9.4.0.0-343 y Java 16.0.0 disponible en este equipo; eso documenta el entorno probado, no una recomendación general de compatibilidad de Java. En el aula se conserva la configuración indicada por el profesor.

Para ejecutar con otro paquete, sustituir **los tres CSV de entrada y asignacion.json** por los del alumno. No cambiar las transformaciones ni las cifras de control. Los resultados finales se mantienen para A001 a A015.

## 2. Decisiones de diseño

- **Unidad de entrada:** cada fila de reservas representa una reserva; cada fila de cobros representa un pago asociado a una reserva; cada fila de hoteles describe un hotel. En este conjunto existe como máximo un cobro por reserva.
- **Unidad de salida:** una fila por hotel y canal en el informe principal; una fila por reserva sin coincidencia en el archivo de cobros en el control interno.
- **Cierre:** `cierre_aula_01`. Los datos no incluyen fechas para seleccionar ayer. El momento de ejecución consta en el registro y no debe presentarse como fecha del cobro.
- **Proceso:** lectura por lotes de los tres archivos locales. Kitchen inicia el job cuando se ejecuta el comando; para fijar un horario haría falta un programador externo.
- **Almacenamiento:** originales separados de los provisionales y de los resultados publicados. Los originales no se modifican durante el tratamiento.
- **Formato:** CSV UTF-8 con cabecera y punto y coma en las salidas. Importes en euros con punto decimal y dos decimales. CSV permite inspección sencilla con herramientas habituales. Para un histórico grande consultado por columnas se estudiaría Parquet, según motor y consultas.
- **Límites:** no se calcula ocupación; no se deduce impago de una reserva sin cobro en el archivo recibido. No hay datos de clientes ni fechas de vencimiento.

## 3. Cómo funciona informe_cobros.ktr

| Paso | Configuración o propósito | Filas esperadas |
| --- | --- | ---: |
| Reservas | CSV con coma; claves y noches Integer; importe BigNumber | 20 |
| Cobros | CSV con punto y coma; clave Integer; cobrado BigNumber | 15 |
| Ordenar reservas y Ordenar cobros | Ascendente por id_reserva en ambas ramas | 20 y 15 |
| Unir reservas y cobros | Merge join INNER por id_reserva | 15 |
| Hoteles y Ordenar hoteles | Leer cinco hoteles y ordenar por id_hotel | 5 |
| Ordenar detalle por hotel | Ordenar el resultado de la primera unión por id_hotel | 15 |
| Añadir nombre hotel | Merge join INNER por id_hotel | 15 |
| Ordenar hotel y canal | Preparar el flujo ordenado para Group by | 15 |
| Resumir cobros | Agrupar por hotel y canal; COUNT_ALL(id_reserva) y SUM(cobrado) | 13 |
| Escribir informe provisional | Seleccionar las cuatro columnas y sobrescribir el CSV | 13 |

Las dos entradas de cada Merge join se ordenan por la clave de esa unión. Ordenar por reserva no sirve para la siguiente unión por hotel. Group by también recibe los grupos contiguos gracias a su ordenación previa.

Se cuenta `id_reserva` porque cada fila unida corresponde aquí a una reserva cobrada y la clave no es nula. Si hubiese varios pagos por reserva, habría que sumar los pagos y contar reservas distintas o agregar primero por reserva. No bastaría con contar todas las filas del cruce.

Se suma `cobrado`, no `importe`. Aunque coincidan en las reservas pagadas de estos paquetes, tienen significados diferentes y una solución correcta debe utilizar el campo adecuado.

## 4. Cómo funciona reservas_sin_cobro.ktr

1. Leer reservas y cobros con sus tipos y separadores.
2. Renombrar la clave del flujo de cobros a `id_reserva_cobro` con Select values. Se conservan medio y cobrado.
3. Ordenar las dos ramas y utilizar Merge join **LEFT OUTER**, con reservas a la izquierda.
4. La unión conserva las 20 reservas. Filter rows conserva las que tienen `id_reserva_cobro IS NULL`; las demás van a un paso Dummy, sin mezclarse con la salida de control.
5. Ordenar por hotel e incorporar su nombre mediante INNER con hoteles ordenados.
6. Añadir el motivo constante y ordenar por id_reserva.
7. Escribir los cinco campos de la salida, sobrescribiendo el provisional anterior.

El filtro observa la ausencia de la clave derecha. Un pago de cero seguiría teniendo una clave y no equivaldría a una reserva sin pago asociado. En este listado, `importe` sigue representando el precio de la reserva, no una cantidad cobrada.

## 5. Los dos archivos correctos

### Informe por hotel y canal

| Hotel | Canal | Reservas | Cobrado total (€) |
| --- | --- | ---: | ---: |
| Comillas | ota | 1 | 132,00 |
| Comillas | recepcion | 1 | 525,00 |
| Comillas | web | 2 | 642,00 |
| Laredo | ota | 1 | 124,00 |
| Laredo | web | 2 | 496,50 |
| Noja | ota | 1 | 195,00 |
| Noja | web | 1 | 280,00 |
| Potes | ota | 1 | 260,00 |
| Potes | recepcion | 1 | 201,00 |
| Potes | web | 1 | 150,00 |
| Santander | ota | 1 | 390,00 |
| Santander | recepcion | 1 | 410,00 |
| Santander | web | 1 | 160,00 |
| **Total: 13 grupos** | | **15** | **3965,50** |

### Control interno

| id_reserva | Hotel | Canal | Importe de la reserva (€) |
| --- | --- | --- | ---: |
| 4 | Santander | web | 89,90 |
| 9 | Noja | ota | 140,00 |
| 11 | Laredo | recepcion | 72,00 |
| 15 | Noja | recepcion | 268,00 |
| 18 | Potes | ota | 70,00 |

Todas incluyen el motivo `Sin cobro asociado en el archivo recibido`. Las quince reservas cobradas más las cinco del control recuperan las veinte originales.

## 6. Qué comprueban las validaciones

**validar_informe.ktr** lee el CSV provisional y utiliza Group by sin claves, con **Always give back a result row**. Calcula número de filas, suma de reservas y suma de cobrado. Filter rows exige simultáneamente 13, 15 y 3965.50. La rama correcta registra el resultado; la otra utiliza Abort con **ABORT_WITH_ERROR** y umbral **0**.

**validar_sin_cobro.ktr** comprueba primero que cada identificador sea uno de 4, 9, 11, 15 y 18. Ordena y agrupa por identificador, exigiendo una sola fila en cada grupo. Resume después sin claves, también con **Always give back a result row**, y exige cinco identificadores. Un identificador no esperado, un duplicado o un CSV vacío producen error.

En una transformación los pasos trabajan como un flujo concurrente. Aunque algunas filas válidas avancen mientras otra alcanza Abort, el resultado final de la transformación debe ser error. El job debe atender a ese estado, no a la presencia de un mensaje parcial en el registro.

Son **los controles automáticos mínimos del enunciado**, no una validación exhaustiva de todos los campos. Un total correcto puede ocultar asignaciones incorrectas entre hoteles. Por eso la corrección también compara todos los grupos y el contenido completo del control con la referencia. Los valores fijos son propios de los paquetes de aula; un proceso real necesitaría reconciliaciones variables, controles de origen y reglas de negocio adicionales.

## 7. Cómo actúa cierre_hotel.kjb

```text
START
  → comprobar las tres entradas
  → informe_cobros
  → reservas_sin_cobro
  → comprobar ambos provisionales
  → validar_informe
  → validar_sin_cobro
  → copiar informe a salida
  → copiar control a salida
  → registrar éxito
  → FIN CORRECTO

Cualquier resultado falso de esas tareas → ERROR (Abort job)
```

Las transiciones después de START son condicionales: solo se continúa por la rama de éxito. Cada tarea tiene su rama de error. Las copias sobrescriben los destinos, no añaden contenido. El mensaje `CIERRE CORRECTO` solo aparece después de las dos copias.

El job no borra al comenzar lo publicado anteriormente. Una entrada ausente o una validación fallida conserva esas salidas. **Las dos copias no constituyen una publicación atómica**: si la primera termina y la segunda falla, puede quedar un conjunto parcialmente actualizado. La solución debe registrar fallo y no anunciar éxito. Una publicación por versiones completas sería una ampliación de arquitectura.

## 8. Pruebas para corregir

En esta instalación, el lanzador Windows `.bat` devuelve a veces 0 aunque Kitchen registre un fallo. Por eso hay que revisar el estado del job en Spoon y el registro final (`Finished with errors`), y no confiar únicamente en el código del `.bat`. Las pruebas automatizadas invocan el motor Java de Kitchen/Pan directamente para recoger su código real.

Las ejecuciones reales y sus códigos de salida se recogen en `evidencias/verificacion.json` y en sus logs. Las pruebas se realizan sobre una copia independiente de esta solución para mantener A001 y sus archivos correctos en el paquete entregado.

| Prueba | Procedimiento | Evidencia que debe buscarse |
| --- | --- | --- |
| Primera ejecución | Ejecutar Kitchen sin salidas anteriores | Código 0 y ambos informes iguales a la referencia |
| Repetición | Ejecutar otra vez | Código 0; mismos bytes de salida, sin filas acumuladas |
| Entrada ausente | Retirar temporalmente cobros en una copia | Código distinto de 0; salidas publicadas sin cambios |
| Solo cabecera | Vaciar los datos de cada provisional y ejecutar su validador directamente | Ambas validaciones fallan aunque el archivo exista |
| Total alterado | Cambiar un importe provisional y ejecutar validar_informe | Error, sin modificar las salidas publicadas |
| Recuperación | Restaurar entradas y ejecutar el job | Código 0 y resultados correctos |
| Identificador no esperado | Introducir 999 en una copia del control | Error del validador |
| Identificador duplicado | Repetir 9 en una copia del control | Error del validador |
| Fallo de validación dentro del job | Alterar un cobro de entrada en la copia y ejecutar Kitchen | Error; no se ejecutan las entradas Publicar ni se alteran las salidas anteriores |
| Paquetes A001–A015 | Sustituir entradas por cada paquete y ejecutar el mismo job | Todos producen los mismos dos resultados completos |

Para una prueba de salida defectuosa, ejecutar **directamente la validación**. Si se ejecuta primero el job, este regenerará el provisional y ocultará el defecto introducido. Para evaluar protección de la publicación, utilizar el fallo dentro del job y comparar el contenido anterior y posterior de `salida`.

No se han simulado todos los errores de disco o de permisos ni se ha probado la ejecución en Linux. Los registros de éxito no sustituyen esas pruebas específicas.

## 9. Orientación para aplicar la rúbrica

| Criterio | Máximo | Qué revisar en la solución del alumno |
| --- | ---: | --- |
| Repositorio y reproducción | 1,00 | Paquete asignado, accesibilidad, avances por sesión, commit final, README y prueba desde otra carpeta |
| Diseño | 1,00 | Sentido de las dos salidas, unidades, cierre, decisiones y límites |
| Informe | 2,00 | Configuración de tipos, uniones y agrupación; los 13 grupos completos |
| Control sin cobro | 1,00 | Los cinco identificadores y sus campos; filtro por clave nula |
| Job y controles | 2,00 | Secuencia, comprobación de vacío, ramas de error y publicación posterior a validar |
| Pruebas | 1,00 | Las seis pruebas obligatorias interpretadas, no solo capturas |
| Defensa: explicar | 1,00 | Recorrido coherente en Spoon con palabras propias |
| Defensa: responder y comprobar | 1,00 | Razonamiento y pequeña comprobación a petición del profesor |
| **Total** | **10,00** | **Defensa individual: 2,00** |

Aplicar máximo, mitad o cero conforme a la rúbrica publicada. No exigir el mismo nombre de los pasos, disposición del lienzo o implementación exacta de este ejemplo cuando otra solución cumple el encargo. Tampoco conceder automáticamente toda la nota porque aparezcan dos CSV correctos.

Los informes finales iguales son esperables. La autoría se contrasta mediante el paquete utilizado, los avances observados y la defensa. Este paquete es una solución docente: no contiene avances ficticios, historial de GitHub ni evidencias de aprendizaje de un alumno.

## 10. Preguntas de defensa y respuesta esperada

| Pregunta | Respuesta que demuestra comprensión |
| --- | --- |
| ¿Por qué 13 filas y no 20? | Se han seleccionado 15 reservas con cobro y agrupado por hotel y canal. Hay 13 combinaciones. |
| ¿Por qué se suma cobrado? | Es el dinero recibido. Importe es el precio de la reserva y puede diferir en otros datos. |
| ¿Por qué ordenar dos veces? | Cada unión requiere sus entradas ordenadas por su propia clave: primero reserva, después hotel. |
| ¿Qué reserva seguirías para explicar el control? | Por ejemplo la 4: existe en reservas, no en cobros; la unión izquierda conserva la reserva y deja nula la clave derecha. |
| ¿Nulo equivale a cero? | No. Cero puede ser un valor de un registro existente. La clave nula significa que no se encontró correspondencia. |
| ¿Qué ocurre si el CSV solo tiene cabecera? | El resumen emite una fila incluso sin entrada y no satisface los recuentos; Abort genera error. |
| ¿Qué evita duplicados al repetir? | Sobrescribir los provisionales y los resultados. No es eliminar filas repetidas sin investigar su origen. |
| ¿Qué sucede si hay dos pagos por reserva? | La unión multiplica filas por pago. Habría que revisar cómo se cuentan reservas, conservando la suma de pagos. |
| ¿Qué pasa si falla la segunda copia? | El job falla y no anuncia éxito. La primera copia puede haberse publicado: no hay atomicidad del conjunto. |
| ¿Puedo afirmar que hay cinco impagos? | No. Solo cinco reservas sin cobro asociado en los datos recibidos. Faltan condiciones y plazos del negocio. |
| ¿Por qué el compañero obtiene el mismo total? | Los paquetes redistribuyen detalle dentro de grupos conservando sus resultados. |
| ¿Kitchen lo ejecuta automáticamente cada noche? | No. Kitchen ejecuta el job al invocarlo; la programación horaria corresponde a otro servicio. |

Como comprobación breve, pedir que localice una de estas decisiones en su flujo y anticipe qué ocurrirá antes de ejecutar una prueba sobre una copia.
