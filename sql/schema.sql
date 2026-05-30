-- =============================================================================
-- schema.sql — Sistema de Inventario de Equipos TI
-- Proyecto Final SO2 — Antonio Samayoa
-- Base de datos: PostgreSQL 15
-- =============================================================================

-- Limpiar si existen objetos previos (útil en re-deployments)
DROP TABLE IF EXISTS historial_equipos CASCADE;
DROP TABLE IF EXISTS asignaciones CASCADE;
DROP TABLE IF EXISTS equipos CASCADE;
DROP TABLE IF EXISTS departamentos CASCADE;
DROP TYPE IF EXISTS tipo_equipo CASCADE;
DROP TYPE IF EXISTS estado_equipo CASCADE;

-- -----------------------------------------------------------------------------
-- ENUMS: tipos controlados para equipos
-- -----------------------------------------------------------------------------
CREATE TYPE tipo_equipo AS ENUM ('laptop', 'switch_poe', 'servidor');
CREATE TYPE estado_equipo AS ENUM ('bodega', 'asignado', 'mantenimiento');

-- -----------------------------------------------------------------------------
-- TABLA: departamentos
-- Almacena los departamentos de la empresa
-- -----------------------------------------------------------------------------
CREATE TABLE departamentos (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    ubicacion   VARCHAR(150),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- TABLA: equipos
-- Catálogo de equipos de TI con su estado actual
-- -----------------------------------------------------------------------------
CREATE TABLE equipos (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(150) NOT NULL,
    tipo            tipo_equipo NOT NULL,
    estado          estado_equipo NOT NULL DEFAULT 'bodega',
    numero_serie    VARCHAR(100) UNIQUE NOT NULL,
    departamento_id INTEGER REFERENCES departamentos(id) ON DELETE SET NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- TABLA: asignaciones
-- Registra a quién está asignado cada equipo y por cuánto tiempo
-- -----------------------------------------------------------------------------
CREATE TABLE asignaciones (
    id                SERIAL PRIMARY KEY,
    equipo_id         INTEGER NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    responsable       VARCHAR(150) NOT NULL,
    fecha_asignacion  DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_devolucion  DATE,
    notas             TEXT
);

-- -----------------------------------------------------------------------------
-- TABLA: historial_equipos
-- Tabla de auditoría — poblada automáticamente por el trigger
-- -----------------------------------------------------------------------------
CREATE TABLE historial_equipos (
    id               SERIAL PRIMARY KEY,
    equipo_id        INTEGER NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
    estado_anterior  estado_equipo NOT NULL,
    estado_nuevo     estado_equipo NOT NULL,
    cambiado_en      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cambiado_por     VARCHAR(100) DEFAULT current_user
);

-- =============================================================================
-- TRIGGER OBLIGATORIO: audit_cambio_estado
-- Se dispara AFTER UPDATE en la tabla equipos cuando cambia el campo 'estado'.
-- Inserta automáticamente un registro de auditoría en historial_equipos.
-- =============================================================================

-- Primero creamos la función que ejecutará el trigger
CREATE OR REPLACE FUNCTION fn_audit_cambio_estado()
RETURNS TRIGGER AS $$
BEGIN
    -- Solo registrar si el estado realmente cambió
    IF OLD.estado IS DISTINCT FROM NEW.estado THEN
        INSERT INTO historial_equipos (
            equipo_id,
            estado_anterior,
            estado_nuevo,
            cambiado_en,
            cambiado_por
        ) VALUES (
            NEW.id,
            OLD.estado,
            NEW.estado,
            NOW(),
            current_user
        );

        -- Actualizar el timestamp de modificación del equipo
        NEW.updated_at = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Ahora creamos el trigger que llama a la función
CREATE TRIGGER audit_cambio_estado
    BEFORE UPDATE ON equipos
    FOR EACH ROW
    EXECUTE FUNCTION fn_audit_cambio_estado();

-- =============================================================================
-- DATOS DUMMY — Datos de prueba realistas
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Departamentos (mínimo 4, incluyendo "Administración" y "Redes")
-- -----------------------------------------------------------------------------
INSERT INTO departamentos (nombre, ubicacion) VALUES
    ('Administración',  'Edificio A, Piso 1'),
    ('Redes',           'Edificio B, Cuarto de Servidores'),
    ('Recursos Humanos','Edificio A, Piso 2'),
    ('Soporte TI',      'Edificio C, Planta Baja'),
    ('Gerencia',        'Edificio A, Piso 3');

-- -----------------------------------------------------------------------------
-- Equipos (mínimo 10, variados en tipo y estado)
-- -----------------------------------------------------------------------------
INSERT INTO equipos (nombre, tipo, estado, numero_serie, departamento_id) VALUES
    ('Dell Latitude 5540',      'laptop',      'asignado',      'DL5540-001-GT', 1),
    ('HP ProBook 450 G9',       'laptop',      'asignado',      'HP450-002-GT',  3),
    ('Lenovo ThinkPad X1',      'laptop',      'bodega',        'LTX1-003-GT',   NULL),
    ('MacBook Pro M3',          'laptop',      'asignado',      'MBP-004-GT',    5),
    ('Cisco Catalyst 2960',     'switch_poe',  'asignado',      'CC2960-005-GT', 2),
    ('Netgear GS308EP',         'switch_poe',  'mantenimiento', 'NG308-006-GT',  2),
    ('Dell PowerEdge R740',     'servidor',    'asignado',      'DPE740-007-GT', 2),
    ('HPE ProLiant DL380',      'servidor',    'bodega',        'HPE380-008-GT', NULL),
    ('Dell Latitude 3540',      'laptop',      'mantenimiento', 'DL3540-009-GT', 4),
    ('Cisco Catalyst 9200',     'switch_poe',  'asignado',      'CC9200-010-GT', 2);

-- -----------------------------------------------------------------------------
-- Asignaciones (mínimo 3, incluyendo una a "Ana Lucia Pérez")
-- -----------------------------------------------------------------------------
INSERT INTO asignaciones (equipo_id, responsable, fecha_asignacion, fecha_devolucion, notas) VALUES
    (1, 'Ana Lucia Pérez',    '2025-01-15', NULL,         'Equipo principal asignado de forma permanente al área de Administración'),
    (2, 'Carlos Mendoza',     '2025-02-01', NULL,         'Uso para gestión de personal y nómina'),
    (4, 'Roberto García',     '2025-03-10', NULL,         'Equipo de gerencia general'),
    (5, 'Luis Tojín',         '2025-01-10', NULL,         'Switch principal del cuarto de comunicaciones'),
    (7, 'Departamento Redes', '2024-12-01', NULL,         'Servidor principal de aplicaciones internas');
