-- Datos iniciales (catálogos). El usuario administrador se crea con
-- `python database/init_db.py --crear-admin` para que la contraseña se
-- guarde con hash bcrypt y nunca quede escrita en un .sql.
USE repositorio_unexpo;

INSERT INTO roles (id, nombre, descripcion, nivel) VALUES
 (1, 'administrador', 'Gestiona usuarios, roles y todo el repositorio', 1),
 (2, 'bibliotecario', 'Docente/personal que carga y edita documentos', 2),
 (3, 'estudiante',    'Busca, consulta y descarga documentos',         3),
 (4, 'invitado',      'Sólo consulta fichas y resúmenes, sin descarga', 4);

INSERT INTO permisos (id, codigo, descripcion) VALUES
 (1, 'documento.ver',        'Buscar y ver la ficha/resumen de documentos'),
 (2, 'documento.descargar',  'Descargar el PDF completo'),
 (3, 'documento.subir',      'Cargar nuevos documentos'),
 (4, 'documento.editar',     'Editar metadatos y publicar/despublicar'),
 (5, 'documento.eliminar',   'Eliminar documentos'),
 (6, 'usuario.gestionar',    'Aprobar, suspender y cambiar rol de usuarios'),
 (7, 'auditoria.ver',        'Consultar registros de acceso y descargas');

INSERT INTO rol_permiso (rol_id, permiso_id) VALUES
 (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),
 (2,1),(2,2),(2,3),(2,4),
 (3,1),(3,2),
 (4,1);

INSERT INTO tipos_documento (id, codigo, nombre) VALUES
 (1, 'TEG', 'Trabajo Especial de Grado'),
 (2, 'IEI', 'Informe de Entrenamiento Industrial');

INSERT INTO etiquetas (nombre) VALUES
 ('Telecomunicaciones'), ('Control y Automatización'), ('Electrónica de Potencia'),
 ('Instrumentación'), ('Sistemas Digitales y Embebidos'), ('Procesamiento de Señales'),
 ('Energías Renovables'), ('Redes y Comunicaciones de Datos');
