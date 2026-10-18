# Preparación docente: 15 paquetes para la práctica de Pentaho

`paquetes-pentaho.zip` contiene A001.zip a A015.zip, un control de huellas SHA-256 y unas instrucciones. No incluye nombres de alumnos ni soluciones de las transformaciones. Esta carpeta está fuera de `docs`: MkDocs no la incorpora a la web. Si se sube al repositorio público, será accesible desde GitHub; no es un almacén privado.

## Guía paso a paso para organizar el aula

Consulta la [guía de reparto y configuración de Moodle](guia-moodle.md): asignación de A001 a A015, entrega individual de los ZIP, tareas de avance por sesión, entrega final, textos para copiar y rúbrica con defensa individual.

## Antes de la primera sesión

Para cargar la rúbrica con el complemento compatible, consulta las [instrucciones de importación](importar-rubrica.md) y descarga el [CSV de la rúbrica](rubrica-pentaho-importar.csv). Requiere los complementos indicados en la guía; no se importa desde el calificador estándar.

1. Descomprimir el paquete docente y asignar un código distinto a cada alumno.
2. Guardar la correspondencia código/alumno en Moodle o en el registro privado del profesor, nunca en este repositorio.
3. Entregar a cada alumno únicamente su ZIP mediante Moodle o en el aula. No necesita Python para utilizar los CSV.
4. Preparar en Moodle un espacio de entrega por sesión (o un registro equivalente) para recoger sesión, URL e identificador completo del commit. Las instrucciones no configuran Moodle automáticamente.
5. Registrar el estado observado y las incidencias durante la clase. El alumnado trabaja en el aula; las recuperaciones se acuerdan en momentos supervisados.

## Qué cambia y qué se mantiene

Se redistribuyen céntimos entre las reservas 1 y 16 (Laredo/web) y entre 8 y 19 (Comillas/web). Se modifican a la vez `importe` y `cobrado` para conservar la coherencia del pago completo. Las cinco reservas sin cobro no cambian. Se reordena la entrada de cada archivo para ejercitar la ordenación antes de las uniones.

Se conservan todos los identificadores, cabeceras, tipos, separadores y relaciones, los 13 grupos con sus cantidades e importes exactos, el total 3965.50 y el listado completo sin cobro. Se mantienen por tanto las tablas de referencia y la rúbrica. Los CSV finales iguales no son indicio suficiente de copia; un flujo correcto puede funcionar con cualquier variante. El paquete sirve para identificar las entradas asignadas, no para certificar autoría ni horarios.

## Comprobar las entradas entregadas

Comparar los tres archivos de `entrada` del alumno con los de su ZIP asignado. `control-docente.csv` contiene las huellas de referencia; `asignacion.json` es informativo y no debe considerarse prueba por sí solo, ya que puede editarse. En PowerShell, `Get-FileHash -Algorithm SHA256 -LiteralPath "ruta/al/archivo.csv"` muestra la huella. Una diferencia puede deberse a contenido, codificación o saltos de línea: investigar antes de atribuirla a una copia. Los originales deben conservarse y las pruebas de fallo hacerse sobre copias.

## Regenerar o ampliar el lote

Desde la raíz del proyecto, con Python 3 y sin dependencias adicionales:

```text
python scripts/generar_datos_pentaho.py --cantidad 15
```

Por defecto genera 15 paquetes. Admite de 1 a 1000 y la opción `--destino` para guardar otro ZIP. Los códigos ya existentes conservan los mismos CSV al ampliar la cantidad con las mismas entradas base. No cambiar las entradas base ni regenerar otras variantes una vez asignadas.

El generador comprueba unicidad de los detalles, claves, referencias, importes positivos y equivalencia de ambos resultados completos con los datos base. No genera la solución Pentaho del alumnado. Conservar la distribución utilizada durante el curso.

## Seguimiento y defensa

Al final de cada sesión recoger la versión realmente mostrada, aunque esté incompleta. Revisar al inicio siguiente las diferencias respecto a esa versión. No usar las fechas internas de los commits como prueba de trabajo presencial. La defensa sigue siendo individual: 1,00 punto por explicar el funcionamiento y 1,00 por responder y comprobar. Los avances se integran en el criterio existente de repositorio, sin aumentar la nota máxima de 10,00.
