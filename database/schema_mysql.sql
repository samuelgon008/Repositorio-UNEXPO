-- =====================================================================
-- Repositorio Digital de TEG e Informes de Entrenamiento Industrial
-- Departamento de Ingeniería Electrónica - UNEXPO
-- Esquema MySQL 8.0+  (motor InnoDB, utf8mb4)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS repositorio_unexpo
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE repositorio_unexpo;

-- ---------------------------------------------------------------------
-- 1. SEGURIDAD: roles, permisos y usuarios
-- ---------------------------------------------------------------------
CREATE TABLE roles (
    id          TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(30)  NOT NULL UNIQUE,      -- administrador, bibliotecario, estudiante, invitado
    descripcion VARCHAR(255),
    nivel       TINYINT UNSIGNED NOT NULL          -- 1 = mayor privilegio
) ENGINE=InnoDB;

CREATE TABLE permisos (
    id          SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo      VARCHAR(50)  NOT NULL UNIQUE,      -- p.ej. 'documento.descargar'
    descripcion VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE rol_permiso (
    rol_id     TINYINT UNSIGNED  NOT NULL,
    permiso_id SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (rol_id, permiso_id),
    FOREIGN KEY (rol_id)     REFERENCES roles(id)    ON DELETE CASCADE,
    FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE usuarios (
    id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cedula            VARCHAR(15)  NOT NULL UNIQUE,
    nombres           VARCHAR(80)  NOT NULL,
    apellidos         VARCHAR(80)  NOT NULL,
    email             VARCHAR(120) NOT NULL UNIQUE,
    username          VARCHAR(40)  NOT NULL UNIQUE,
    password_hash     VARCHAR(255) NOT NULL,          -- bcrypt, nunca texto plano
    rol_id            TINYINT UNSIGNED NOT NULL,
    estado            ENUM('pendiente','activo','suspendido') NOT NULL DEFAULT 'pendiente',
    intentos_fallidos TINYINT UNSIGNED NOT NULL DEFAULT 0,
    bloqueado_hasta   DATETIME NULL,
    ultimo_acceso     DATETIME NULL,
    aprobado_por      INT UNSIGNED NULL,
    creado_en         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id)       REFERENCES roles(id),
    FOREIGN KEY (aprobado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. DOCUMENTOS
-- ---------------------------------------------------------------------
CREATE TABLE tipos_documento (
    id     TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,                -- TEG, IEI
    nombre VARCHAR(80) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE documentos (
    id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo           VARCHAR(300) NOT NULL,
    resumen          TEXT,
    tipo_id          TINYINT UNSIGNED NOT NULL,
    anio             SMALLINT UNSIGNED NOT NULL,
    fecha_aprobacion DATE NULL,
    empresa          VARCHAR(150) NULL,                -- sólo para Entrenamiento Industrial
    ruta_archivo     VARCHAR(255) NOT NULL UNIQUE,     -- relativa a storage/documentos
    nombre_original  VARCHAR(255) NOT NULL,
    tamano_bytes     BIGINT UNSIGNED NOT NULL,
    hash_sha256      CHAR(64) NOT NULL UNIQUE,         -- integridad y anti-duplicados
    publicado        BOOLEAN NOT NULL DEFAULT FALSE,
    subido_por       INT UNSIGNED NOT NULL,
    creado_en        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_id)    REFERENCES tipos_documento(id),
    FOREIGN KEY (subido_por) REFERENCES usuarios(id),
    INDEX idx_doc_anio (anio),
    FULLTEXT INDEX ft_doc_titulo_resumen (titulo, resumen)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. METADATOS NORMALIZADOS
-- ---------------------------------------------------------------------
-- Personas: autores y tutores (una misma persona puede ser autor de un
-- TEG y años después tutor de otro, por eso no se separan en dos tablas).
CREATE TABLE personas (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombres     VARCHAR(80)  NOT NULL,
    apellidos   VARCHAR(80)  NOT NULL,
    cedula      VARCHAR(15)  NULL UNIQUE,
    email       VARCHAR(120) NULL,
    institucion VARCHAR(150) NULL,                     -- UNEXPO o empresa (tutor industrial)
    INDEX idx_persona_nombre (apellidos, nombres)
) ENGINE=InnoDB;

CREATE TABLE documento_persona (
    documento_id INT UNSIGNED NOT NULL,
    persona_id   INT UNSIGNED NOT NULL,
    participacion ENUM('autor','tutor_academico','tutor_industrial','jurado') NOT NULL,
    orden        TINYINT UNSIGNED NOT NULL DEFAULT 1,  -- orden de aparición de autores
    PRIMARY KEY (documento_id, persona_id, participacion),
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE CASCADE,
    FOREIGN KEY (persona_id)   REFERENCES personas(id)
) ENGINE=InnoDB;

-- Etiquetas: vocabulario CONTROLADO (áreas temáticas del departamento).
CREATE TABLE etiquetas (
    id     SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE documento_etiqueta (
    documento_id INT UNSIGNED      NOT NULL,
    etiqueta_id  SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (documento_id, etiqueta_id),
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE CASCADE,
    FOREIGN KEY (etiqueta_id)  REFERENCES etiquetas(id)
) ENGINE=InnoDB;

-- Palabras clave: vocabulario LIBRE tomado del propio documento.
CREATE TABLE palabras_clave (
    id      INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    termino VARCHAR(80) NOT NULL UNIQUE                -- guardado en minúsculas
) ENGINE=InnoDB;

CREATE TABLE documento_palabra_clave (
    documento_id     INT UNSIGNED NOT NULL,
    palabra_clave_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (documento_id, palabra_clave_id),
    FOREIGN KEY (documento_id)     REFERENCES documentos(id) ON DELETE CASCADE,
    FOREIGN KEY (palabra_clave_id) REFERENCES palabras_clave(id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 4. AUDITORÍA
-- ---------------------------------------------------------------------
CREATE TABLE registro_accesos (
    id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT UNSIGNED NULL,                      -- NULL si el username no existe
    username   VARCHAR(40) NOT NULL,
    exitoso    BOOLEAN NOT NULL,
    motivo     VARCHAR(60) NULL,
    ip         VARCHAR(45) NULL,
    fecha      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    INDEX idx_acceso_fecha (fecha)
) ENGINE=InnoDB;

CREATE TABLE descargas (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id   INT UNSIGNED NOT NULL,
    documento_id INT UNSIGNED NOT NULL,
    ip           VARCHAR(45) NULL,
    fecha        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id)   REFERENCES usuarios(id),
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE CASCADE,
    INDEX idx_descarga_doc (documento_id)
) ENGINE=InnoDB;
