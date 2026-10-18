# Guía docente: reparto de paquetes y entregas en Moodle

Esta guía organiza la práctica integradora de Pentaho para **15 alumnos**. Cada alumno utiliza su paquete, trabaja en el aula y entrega avances al terminar cada sesión. La entrega final se evalúa sobre **10,00 puntos**, incluidos **2,00 de defensa individual**.

Los nombres de algunos botones pueden variar según la versión y configuración de Moodle del centro. La guía describe la configuración que debe realizar el profesor; no crea actividades, restricciones ni calificaciones automáticamente.

## 1. Preparar y asignar los 15 paquetes

1. Descargar [paquetes-pentaho.zip](paquetes-pentaho.zip). Desde GitHub, abrir el archivo y utilizar el botón de descarga.
2. Descomprimir el ZIP docente en el ordenador. Contiene `A001.zip` a `A015.zip`, `control-docente.csv` y las instrucciones.
3. Asignar un código distinto a cada alumno, por ejemplo siguiendo el orden de la lista de clase. Mantener esa asignación durante toda la práctica.
4. Conservar una relación **privada** con las columnas siguientes:

| Alumno | Código asignado | Usuario de GitHub | URL del repositorio |
| --- | --- | --- | --- |
| Primer alumno | A001 | Por completar | Por completar |
| Segundo alumno | A002 | Por completar | Por completar |
| … | … | … | … |
| Decimoquinto alumno | A015 | Por completar | Por completar |

No subir esta relación con nombres a GitHub. Los paquetes contienen datos sintéticos; la relación entre códigos y alumnos debe quedar en el registro privado del profesor.

Cada paquete cambia algunos importes individuales y el orden de las filas, pero mantiene **los dos resultados finales completos**. No interpretar la igualdad de los informes finales como prueba de copia. La [guía de los paquetes](README.md) explica cómo comprobar los originales y sus huellas.

## 2. Entregar a cada alumno su paquete

Se pueden repartir los ZIP directamente en el aula. Para hacerlo desde Moodle, preparar un recurso individual por alumno:

1. Activar la edición del curso y situarse en la UT1.
2. Añadir un recurso **Archivo**, con el nombre `Pentaho — Paquete A001`.
3. Adjuntar únicamente `A001.zip`, sin descomprimirlo.
4. En **Restricciones de acceso → Añadir restricción → Perfil de usuario**, seleccionar el correo electrónico e indicar que debe coincidir exactamente con el registrado en Moodle para ese alumno.
5. Cerrar el icono del ojo de esa restricción: quienes no la cumplan no verán el recurso ni la condición.
6. Guardar y repetir hasta A015, comprobando cada correspondencia. Si se duplica el recurso, sustituir tanto el ZIP como el destinatario.
7. Durante la primera clase, comprobar que cada alumno puede abrir su recurso y recibe el código correcto.

Si la restricción por perfil no está disponible en el centro, repartir los archivos directamente en clase. Las restricciones por perfil y la visibilidad mediante el icono del ojo están descritas en la [documentación de Moodle](https://docs.moodle.org/en/Restrict_access_settings).

**Esta distribución organiza el reparto, no garantiza el secreto de los datos:** el lote también está en el repositorio público. Debe comprobarse que cada alumno utiliza el paquete asignado.

## 3. Revisar la preparación en la primera sesión

Pedir a cada alumno que:

1. Descomprima su ZIP y compruebe el código de `asignacion.json`.
2. Cree en su cuenta el repositorio `bda-ut1-pentaho-hotel` y prepare una copia local.
3. Copie `entrada` y `asignacion.json` a la raíz de esa copia.
4. Anote el código en el README y conserve intactos los originales.
5. Facilite acceso al profesor si el repositorio es privado y compruebe que la invitación ha sido aceptada.

Completar el registro privado con el usuario y la URL. Comprobar el acceso al repositorio desde la cuenta del profesor. Los pasos técnicos de Pentaho están en el [enunciado de la práctica](../../docs/ut1/tarea-clase.md).

## 4. Crear la tarea de avance de la primera sesión

Añadir una actividad **Tarea** llamada **UT1 Pentaho — Avance de la sesión 1**.

| Ajuste | Configuración propuesta |
| --- | --- |
| Tipo de entrega | Texto en línea |
| Archivos enviados | Desactivado: procesos y evidencias quedan en GitHub |
| Entrega por grupos | No |
| Calificación | Ninguna |
| Comentarios de retroalimentación | Activados |
| Requerir pulsar el botón de envío | Sí |
| Permitir entregas desde | Inicio de la sesión |
| Fecha de entrega | Final de la sesión |
| Fecha límite | Final de la sesión |

La fecha de entrega marca los retrasos; la fecha límite cierra el envío. Comprobar la zona horaria y la hora concreta. No basta con establecer solo la fecha de entrega. Estas opciones se describen en la [configuración de tareas de Moodle](https://docs.moodle.org/en/Assignment_settings).

### Texto para copiar en la descripción

```text
Entrega el estado real de tu trabajo antes de finalizar la sesión, aunque todavía esté incompleto.

1. Guarda los procesos en Spoon.
2. Actualiza el registro de sesión en la carpeta evidencias.
3. Muestra al profesor el avance o la dificultad principal.
4. Crea un commit, sube los cambios a GitHub y comprueba que aparecen en el navegador.
5. Completa esta entrega con:

Sesión y fecha:
Código del paquete:
URL del repositorio:
Identificador completo del commit:
Qué he realizado:
Qué he comprobado y qué resultado he obtenido:
Qué queda pendiente:
Qué ayuda he recibido:

Pulsa «Enviar tarea» y comprueba que la entrega no queda como borrador.

Si falla la conexión, avisa al profesor antes de salir. No continúes el trabajo desde casa para completar esta entrega.
```

El identificador se copia después de crear el commit. No hace falta incluirlo dentro del registro de esa misma versión: se entrega en Moodle.

## 5. Preparar las siguientes sesiones

Duplicar la primera tarea y cambiar nombre, fechas y objetivo. **Una tarea por sesión recoge las 15 entregas individuales**; no hacen falta 15 tareas de avance por clase.

| Tarea | Objetivo orientativo |
| --- | --- |
| Avance de la sesión 1 | Paquete, repositorio, diseño e informe de cobros |
| Avance de la sesión 2 | Reservas sin cobro y validaciones |
| Avance de la sesión 3 | Job, pruebas y reproducción desde otra carpeta |
| Avance de la sesión 4 y siguientes, si hacen falta | Completar lo pendiente bajo supervisión |

Mantener una actividad distinta por sesión para conservar los avances y los comentarios. No pedir al alumno que sobrescriba una única entrega durante toda la práctica.

Las tres sesiones de 55–60 minutos son orientativas. Ampliarlas si el grupo necesita más tiempo y acordar recuperaciones supervisadas para ausencias o incidencias. El trabajo pendiente no se traslada a casa.

## 6. Rutina para cerrar y retomar cada sesión

Reservar los últimos **5–10 minutos** para el cierre:

1. Anunciar que comienza la entrega de avances.
2. El alumnado guarda los procesos y registra lo realizado en `evidencias/sesion-01.md`, `sesion-02.md`, etc.
3. Durante la sesión y su cierre, observar especialmente los bloqueos y las modificaciones importantes. No esperar al último minuto para revisar a los quince alumnos.
4. Abrir **Ver todas las entregas** y revisar quién ha enviado.
5. Comprobar que el commit indicado está disponible y corresponde al avance mostrado.
6. Dejar una observación breve: qué se ha comprobado y qué debe abordarse después.

Con el botón de envío activado, guardar el texto puede dejarlo en borrador. El alumno debe comprobar el estado «Enviado para calificar» o equivalente. Si hay una incidencia, registrar lo observado y conservar una copia cuando sea necesario. Moodle permite conceder una ampliación individual desde la lista de entregas: localizar al alumno, abrir sus acciones y elegir **Conceder ampliación**. Usarla para un momento supervisado, no como encargo para casa. Véase [Uso de las tareas](https://docs.moodle.org/en/Using_Assignment).

Al comenzar la siguiente clase, retomar la versión registrada y pedir una explicación de cualquier diferencia antes de continuar. No borrar ni reescribir el historial de avances.

Una nota de seguimiento del profesor puede recoger: alumno/código, sesión, commit observado, comprobación realizada, bloqueo y siguiente paso. Mantener ese registro en el entorno privado del profesor.

## 7. Crear la tarea final

Añadir otra actividad llamada **UT1 Pentaho — Entrega final y defensa individual**.

Mantener texto en línea, entrega individual y botón de envío. Situar la apertura y el cierre dentro de la sesión destinada a la entrega final. En **Calificación**, establecer **Puntuación máxima: 10** y **Método: Rúbrica**.

### Texto para copiar en la descripción

```text
Código del paquete asignado:
URL del repositorio:
Identificador completo del commit final:
Enlace al README:
Enlace a la carpeta de evidencias:

Resultado de la prueba desde otra carpeta:
Incidencias o limitaciones pendientes:

Comprueba antes de enviar que:
- El profesor puede acceder al repositorio.
- Has subido los últimos cambios.
- Están los originales asignados, asignacion.json, las cuatro transformaciones, el job y los dos CSV finales.
- El README explica cómo ejecutar el trabajo.
- Están los registros de sesión y las seis pruebas comentadas.

La defensa individual se realizará sobre esta versión.
```

La última entrega de avance y la entrega final pueden coincidir en el mismo commit si no se han hecho más cambios. La final identifica inequívocamente qué versión se evalúa.

## 8. Configurar la rúbrica sobre 10,00

Después de guardar la tarea final:

1. Entrar en **Calificación avanzada** y elegir **Definir una nueva rúbrica**.
2. Darle el nombre `UT1 Pentaho — Rúbrica del trabajo y defensa individual`.
3. Crear los ocho criterios de la tabla siguiente con sus tres niveles.
4. Incorporar las evidencias de la segunda tabla como orientación de cada criterio.
5. Permitir que los alumnos consulten la rúbrica y habilitar comentarios por criterio.
6. Guardar la rúbrica como lista para usar, no como borrador.

| Criterio | No demostrado | Parcial | Completo |
| --- | ---: | ---: | ---: |
| Repositorio y reproducción del trabajo | 0 | 0,50 | 1,00 |
| Diseño y comprensión del encargo | 0 | 0,50 | 1,00 |
| Informe de cobros | 0 | 1,00 | 2,00 |
| Control de reservas sin cobro | 0 | 0,50 | 1,00 |
| Job y validaciones automáticas | 0 | 1,00 | 2,00 |
| Pruebas y evidencias | 0 | 0,50 | 1,00 |
| Defensa: explicar el funcionamiento | 0 | 0,50 | 1,00 |
| Defensa: responder y comprobar | 0 | 0,50 | 1,00 |
| **Máximo** | | | **10,00** |

Usar el separador decimal que acepte el formulario. Si una instalación exige puntos enteros en los niveles, duplicar **todos** los valores de la tabla: los niveles serán 0/1/2 y 0/2/4, con suma máxima 20, manteniendo la calificación máxima de la tarea en 10. Moodle normaliza la puntuación; así se conserva exactamente la ponderación.

| Criterio | Evidencias para valorar |
| --- | --- |
| Repositorio y reproducción | Acceso del profesor, paquete asignado, archivos completos, avances y commits identificados, README suficiente y ejecución desde otra carpeta |
| Diseño | Recorrido coherente, reglas justificadas, cierre y unidades identificados, elección de CSV y límites de los datos |
| Informe de cobros | Lecturas y tipos correctos; uniones y agrupación justificadas; 13 grupos, 15 reservas, 3965.50 euros y asignación correcta a cada hotel/canal |
| Reservas sin cobro | Cinco reservas correctas y sin duplicados; diferencia entre ausencia de cobro y cero; columnas y motivo claros |
| Job y validaciones | Orden y ramas correctos; validación de ambos CSV; rechazo de salida vacía o incorrecta; publicación tras validar y aviso de fallo |
| Pruebas | Seis pruebas documentadas; esperado/obtenido; explicación de repetición, fallos y recuperación |
| Explicación individual | Recorrido en Spoon que relaciona entradas, pasos y salidas, con decisiones explicadas con palabras propias |
| Preguntas y comprobación | Respuestas razonadas y realización o interpretación de una pequeña prueba solicitada por el profesor |

Aplicar en cada criterio la misma regla: completo y correcto, valor máximo; demostrado parcialmente con errores u omisiones relevantes, mitad; sin evidencia o sin demostrar, cero. Conservar un nivel cero en todos los criterios. Comprobar que el resultado máximo se muestra como **10,00** y la defensa representa **2,00**. La [documentación de rúbricas](https://docs.moodle.org/en/Rubrics) explica la creación de niveles y la normalización de la nota.

Los avances **no tienen calificación independiente**: se consideran dentro del criterio de repositorio y evitan duplicar su peso en la nota. La rúbrica coincide con la del enunciado de la práctica.

## 9. Evaluar el trabajo y la defensa individual

1. Revisar previamente el repositorio en el **commit entregado**, no solo su estado más reciente, y anotar la valoración de los seis primeros criterios.
2. Organizar un encuentro de **8–10 minutos** con cada alumno. Para quince alumnos son **120–150 minutos**, más las transiciones; reservar varias sesiones.
3. Pedir que recorra su solución y explique las decisiones. Puede seguir una reserva desde la entrada hasta el informe y mostrar una reserva sin pago.
4. Formular las preguntas que se consideren necesarias. Por ejemplo: por qué ordena antes de unir, por qué suma cobrado, por qué aparecen trece grupos o qué rama impide publicar.
5. Pedir una pequeña comprobación en una copia de trabajo, conservando intacta la versión entregada.
6. Completar los dos criterios individuales y guardar la calificación final con comentarios. No asignar ceros provisionales a una defensa que aún no se ha realizado.

El profesor puede recoger durante la conversación qué pregunta formuló, qué explicó el alumno y qué comprobó. No se evalúa memorizar botones, sino comprender lo construido.

## 10. Comprobación antes de empezar

- [ ] Hay quince códigos distintos asignados y la relación con nombres está guardada de forma privada.
- [ ] Cada alumno puede obtener su ZIP y el profesor puede acceder a su repositorio.
- [ ] Las tareas de avance tienen fechas propias, entrega individual y ninguna nota independiente.
- [ ] La tarea final tiene máximo 10 y la rúbrica está lista y visible.
- [ ] Se ha explicado que guardar un borrador no equivale a enviar.
- [ ] Están previstos el cierre de cada sesión, las incidencias y las defensas.

**Límite del control horario:** Moodle cierra las entregas en las horas configuradas, pero no bloquea GitHub ni la edición local. Evaluar la versión registrada y apoyar la comprobación de autoría en el trabajo observado, las evidencias y la defensa individual. Las fechas internas de los commits no acreditan por sí solas trabajo presencial.
