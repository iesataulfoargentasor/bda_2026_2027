-- Esquema mínimo para el taller 6 (PostgreSQL o MariaDB/MySQL).
-- No subas contraseñas ni hosts reales al .ktr.

CREATE TABLE IF NOT EXISTS huespedes (
    id_huesped INTEGER PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    tipo VARCHAR(20) NOT NULL
);

INSERT INTO huespedes (id_huesped, nombre, tipo) VALUES
    (1, 'Ana Ruiz', 'huesped'),
    (2, 'Luis Vega', 'huesped'),
    (3, 'Marta Soto', 'huesped'),
    (4, 'Omar Díaz', 'huesped'),
    (5, 'Eva Lama', 'huesped');

CREATE TABLE IF NOT EXISTS fases_incidencia (
    id_huesped INTEGER NOT NULL,
    tipo VARCHAR(40),
    fecha_inicio DATE,
    fecha_fin TIMESTAMP,
    lado VARCHAR(40),
    comentario VARCHAR(200)
);
