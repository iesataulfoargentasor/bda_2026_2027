---
title: 1.2 Clústeres de computadoras
tags:
  - Big Data
  - BDA
  - RA1
---

# 1.2. Clústeres de computadoras

Cuando una sola máquina no da más de sí, la tentación es “comprar el servidor más gordo del catálogo”. Eso funciona un tiempo (escalado **vertical**) y luego choca con un techo: precio, enchufe, lo que el fabricante vende.

Un **clúster** es otro planteamiento: varios ordenadores (**nodos** o servidores) unidos por red que resuelven el trabajo **como si fueran uno**. En Big Data es la pieza que permite crecer **añadiendo máquinas**, no solo agrandando *esa*.

Hoy se construyen sobre **commodity hardware** (servidores normales, no necesariamente un mainframe) más un *framework* de computación distribuida que reparte tareas y datos.

!!! example "La metáfora del comedor"
    Una cocina con un solo fogón enorme (vertical) cocina un puchero muy grande, pero si se apaga el gas, no hay comida. Varios fogones coordinados (clúster) parten el trabajo; si uno falla, los otros pueden seguir (si habías **replicado** la receta y los ingredientes).

## Qué ganas (y qué significa cada cosa)

| Propiedad | En la práctica | Cómo lo notas |
| --- | --- | --- |
| **Alto rendimiento** | Partes el trabajo en subtareas y las ejecutas a la vez | El job de 8 horas pasa a 1 hora con 8 nodos *si* se puede partir |
| **Alta disponibilidad** | Si un nodo cae, otro tiene réplica o asume el servicio | Un disco muerto no tumba el cuadro de mando |
| **Equilibrio de carga** | No mandas todo al mismo nodo | Miras tamaño del trabajo, carga actual y potencia de cada máquina |
| **Escalabilidad** | Añades nodos cuando crece el dato | Empiezas con 4 y el año que viene pones 6, sin rediseñar el programa |

Estas cuatro se apoyan entre sí. Un clúster “rápido” pero sin réplica es frágil. Uno muy replicado pero mal balanceado deja un nodo al 100 % y el resto de brazos cruzados.

### Alto rendimiento

Cada nodo es un ordenador completo (CPU, RAM, disco). Si el trabajo se puede **trocear**, mandas un trozo a cada uno y juntas el resultado. Es la idea de “llevar el cálculo al dato”: mejor mover una función pequeña que mover petabytes por la red hacia una sola CPU.

### Alta disponibilidad

Los nodos se vigilan. Si uno desaparece (luz, disco, red), el sistema puede:

- Rearrancar ese nodo o levantar otro.
- Seguir sirviendo desde una **réplica** que ya tenía los mismos datos.

Sin réplica, “varios ordenadores” solo es más potencia, no más seguridad.

### Equilibrio de carga

Un mal balanceo es mandar todos los jobs al nodo que “siempre ha ido bien”. El algoritmo debería mirar:

- Lo grande que es el trabajo.
- Lo ocupado que está cada nodo.
- Lo potente que es cada nodo (no todos son iguales).

Si no, creas un **cuello de botella**: la latencia media sube aunque el clúster “tenga máquinas libres”.

### Escalabilidad

No hace falta acertar el tamaño el día 1. Empiezas con lo que puedes pagar y creces. Eso es muy deseable en Big Data: el volumen **no** se estima bien a priori; si te pasas de pesimista, has tirado el dinero; si te quedas corto, el sistema se ahoga.

## Escalado vertical y horizontal

| | Vertical (*scale-up*) | Horizontal (*scale-out*) |
| --- | --- | --- |
| Qué haces | Más CPU, RAM o disco **en la misma máquina** | **Más máquinas** en el clúster |
| Analogía | Un camión más grande | Más furgonetas |
| Límite | El mejor hardware del catálogo (y su precio) | Red, coordinación, presupuesto de nodos |
| Típico en | Un SGBD relacional en un solo servidor | Hadoop, almacenes distribuidos, muchas NoSQL |

!!! warning "Cuidado con el nombre *scale-in*"
    En el material antiguo a veces se llamaba *scale-in* al vertical. En la jerga habitual:

    - **scale-up** = vertical (agrandar *una* máquina)
    - **scale-out** = horizontal (añadir máquinas)
    - **scale-in** = **quitar** nodos (reducir el clúster cuando sobra capacidad)

    En clase decimos **vertical** y **horizontal** y no hay duda.

El vertical **no te da escalabilidad real** en Big Data: siempre hay un techo (y un precio absurdo cerca de ese techo). El horizontal es el que encaja con un volumen que no para de crecer.

## Cuándo un clúster no hace magia

Añadir nodos **no** acorta el tiempo de forma lineal si la tarea **no se puede partir**. Si cada paso depende del resultado del anterior, el segundo nodo está esperando al primero: tienes más máquinas y el mismo cuello.

Eso se desarrolla en [procesamiento paralelo](procesamiento.md). El clúster brilla cuando hay **independencia** entre trozos: sumar bloques de números, procesar ficheros distintos, consultas que el motor puede repartir. En clase lo pones a prueba con la [tarea de los 500 GB](tarea-clase.md): el portátil no es un clúster.

También hay coste de **coordinación**: la red, el maestro que reparte, el momento de juntar resultados. Diez nodos no son “diez veces más rápido” en todos los problemas; a veces son 6 o 7, y a veces casi 1.

## Relación con el RA1

Diseñar el almacenamiento masivo implica decidir: ¿un servidor ACID o un clúster que replica y reparte? Esa decisión condiciona:

- cómo **ingieres** (un destino o muchos nodos),
- qué **formato** usas (que se pueda trocear),
- qué pasa si un nodo falla **a mitad** de un job (¿el cliente ve un informe a medias?).

Caracterizar esa decisión es el criterio **a)**.
