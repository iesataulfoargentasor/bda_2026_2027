# Importar la rúbrica de Pentaho en Moodle

Archivo: [rubrica-pentaho-importar.csv](rubrica-pentaho-importar.csv).

Contiene ocho criterios con tres niveles cada uno: no demostrado (0 % del criterio), parcial (50 %) y completo (100 %). Los máximos suman **10,00 puntos**. Los dos criterios de defensa individual valen **1,00 cada uno**, un total de **2,00 puntos**.

## Requisito de importación

Este CSV está preparado específicamente para **Import rubric from CSV** (`block_importrubric`) junto con **Rubric Importer Core** (`local_customgradingform_renderer`). No es un formato universal de Moodle. La importación de notas del calificador no crea rúbricas y no sirve para este archivo.

El Moodle estándar permite definir rúbricas en su editor, pero no incluye este importador CSV. Si no aparece el bloque, consultar al administrador del centro para comprobar si ambos complementos están instalados y son compatibles con la versión del centro. No se ha comprobado su instalación ni se ha realizado una importación en el Moodle del profesor.

Referencias del desarrollador: [bloque de importación](https://github.com/ingrichardrangel/moodle-block_importrubric) y [componente de importación](https://github.com/ingrichardrangel/moodle-local_customgradingform_renderer). La compatibilidad depende de las versiones instaladas; no basta con que aparezca cualquier otro importador de rúbricas.

## Pasos con el complemento disponible

1. Descargar el CSV sin modificarlo con Excel. Si se obtiene desde GitHub, utilizar la descarga del archivo, no guardar la página HTML.
2. Abrir la tarea **UT1 Pentaho — Entrega final y defensa individual**.
3. En sus ajustes, establecer calificación de tipo **Puntuación**, máximo **10**, y método **Rúbrica**. Guardar. No crear una definición manual antes de importar.
4. Activar la edición y añadir dentro de la tarea el bloque **Import rubric from CSV**. Según el tema de Moodle puede estar en el panel lateral de bloques.
5. Pulsar el botón del bloque, seleccionar `rubrica-pentaho-importar.csv` y confirmar la importación.
6. En la rúbrica importada, poner el nombre **UT1 Pentaho — Trabajo y defensa individual**. Revisar los ocho criterios y los tres niveles de cada uno.
7. Permitir que los estudiantes consulten la rúbrica y activar los comentarios por criterio si se desean. Guardarla como lista para usar: el importador la crea como borrador.
8. Comprobar las puntuaciones de la tabla siguiente antes de utilizarla para calificar.

**Si ya existe una rúbrica en la tarea:** el importador revisado no la sobrescribe. Hacer primero la prueba en una tarea nueva sin definición de rúbrica. No borrar una rúbrica utilizada para evaluar alumnos para intentar importar el archivo.

## Puntuaciones que deben aparecer

| Criterio | No demostrado | Parcial | Completo |
| --- | ---: | ---: | ---: |
| Repositorio y reproducción del trabajo | 0,00 | 0,50 | 1,00 |
| Diseño y comprensión del encargo | 0,00 | 0,50 | 1,00 |
| Informe de cobros | 0,00 | 1,00 | 2,00 |
| Control de reservas sin cobro | 0,00 | 0,50 | 1,00 |
| Job y validaciones automáticas | 0,00 | 1,00 | 2,00 |
| Pruebas y evidencias | 0,00 | 0,50 | 1,00 |
| Defensa individual: explicar el funcionamiento | 0,00 | 0,50 | 1,00 |
| Defensa individual: responder y comprobar | 0,00 | 0,50 | 1,00 |
| **Máximo** | | | **10,00** |

La calificación máxima de la tarea debe ser **10**, no 100. Este importador compara la suma de máximos del CSV con el máximo de la tarea. No duplicar las puntuaciones del archivo: se han conservado directamente los valores de la rúbrica del enunciado.

En una tarea de prueba y con una entrega de prueba, comprobar:

- Todos los niveles completos: **10,00**.
- Todos los niveles parciales: **5,00**.
- Solo los dos criterios de defensa completos y el resto a cero: **2,00**.
- Los seis criterios del trabajo completos y la defensa a cero: **8,00**.

Estas combinaciones son pruebas del cálculo, no propuestas de calificación para alumnos reales. La defensa pendiente no debe registrarse como cero provisional. Para mostrar dos decimales, revisar el ajuste de visualización del ítem en el calificador; no cambiar las ponderaciones.

## Si no está instalado ese importador

El archivo no podrá importarse por la ruta anterior. El administrador puede valorar la instalación de los complementos para la versión del centro. Como alternativa sin complementos, utilizar el editor de rúbricas siguiendo el apartado 8 de la [guía de Moodle](guia-moodle.md). Los textos del CSV pueden copiarse en las celdas de ese editor, pero sería una carga manual.

Una vez creada la rúbrica en Moodle, se puede reutilizar mediante las funciones de plantillas que permita el centro. No cambiar la extensión del CSV a XML o MBZ: eso no lo convierte en una rúbrica ni en una copia de seguridad válida.

## Formato y comprobaciones realizadas

- UTF-8 sin BOM. Separador coma. Decimales con punto.
- Cabecera exacta: `criterion,level,level_description,score`.
- 24 filas de datos: ocho criterios por tres niveles.
- Descripciones sin comas, comillas dobles ni punto y coma, para cumplir las restricciones del código del importador revisado.
- Puntuación mínima cero y puntuaciones distintas dentro de cada criterio.
- Máximo global 10 y máximo de defensa 2.

Se han verificado la estructura y las puntuaciones del archivo. La importación efectiva y la presentación deben comprobarse en el Moodle de destino. Fuentes: [código del importador](https://github.com/ingrichardrangel/moodle-local_customgradingform_renderer/blob/main/import.php) y [rúbricas en Moodle](https://docs.moodle.org/en/Rubrics).

## Aclaración de la presentación a gerencia

**Cómo se puntúa la comunicación a gerencia (CE e).** Dentro de «Diseño y comprensión del encargo», se concede **1,00** cuando tanto el diseño como la explicación para gerencia están completos y son correctos; **0,50** cuando se demuestra solo una de esas partes o hay errores relevantes; **0,00** cuando no se demuestra ninguna. No se exige un gráfico ni otra herramienta: se comprueba que una persona ajena a Spoon entienda el periodo, las unidades, el resultado y sus límites. La defensa conserva sus **2,00 puntos** y evalúa la comprensión personal; no sustituye esta evidencia escrita ni se vuelve a puntuar en ella la presentación del README.

Al actualizar una rúbrica ya creada, revise los descriptores del criterio de diseño en Moodle. El CSV actualizado no modifica automáticamente las rúbricas existentes ni las calificaciones previas.
