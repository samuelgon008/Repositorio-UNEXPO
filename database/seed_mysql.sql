-- Datos iniciales (catálogos) para crear la BD MySQL a mano.
-- DEBE COINCIDIR con backend/app/core/catalogos.py (un test lo verifica).
-- Igualmente, el backend sincroniza estos catálogos al arrancar.
--
-- El usuario administrador se crea con
-- `python database/init_db.py --crear-admin` para que la contraseña se
-- guarde con hash bcrypt y nunca quede escrita en un .sql.
USE repositorio_unexpo;

INSERT INTO roles (id, nombre, descripcion, nivel) VALUES
 (1, 'administrador', 'Control total del repositorio', 1),
 (2, 'docente',       'Consulta las fichas y lee las tesis en línea', 2),
 (3, 'estudiante',    'Consulta las fichas y solicita acceso a los PDF', 3);

INSERT INTO permisos (id, codigo, descripcion) VALUES
 (1, 'documento.ver',        'Buscar y ver la ficha y el resumen de las tesis'),
 (2, 'documento.leer',       'Abrir el PDF completo en línea sin solicitud'),
 (3, 'documento.descargar',  'Descargar cualquier PDF sin solicitud'),
 (4, 'documento.editar',     'Editar datos de las tesis y publicarlas u ocultarlas'),
 (5, 'documento.eliminar',   'Eliminar tesis del repositorio'),
 (6, 'solicitud.crear',      'Solicitar acceso al PDF de una tesis'),
 (7, 'solicitud.gestionar',  'Aprobar, rechazar y revocar solicitudes de acceso'),
 (8, 'usuario.gestionar',    'Aprobar, bloquear, eliminar y cambiar el rol de usuarios'),
 (9, 'auditoria.ver',        'Consultar registros de acceso y descargas');

INSERT INTO rol_permiso (rol_id, permiso_id) VALUES
 (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),
 (2,1),(2,2),
 (3,1),(3,6);

INSERT INTO tipos_documento (id, codigo, nombre) VALUES
 (1, 'TEG', 'Trabajo Especial de Grado'),
 (2, 'IEI', 'Informe de Entrenamiento Industrial');

INSERT INTO etiquetas (nombre) VALUES
 ('Telecomunicaciones'), ('Control y Automatización'), ('Electrónica de Potencia'),
 ('Instrumentación'), ('Sistemas Digitales y Embebidos'), ('Procesamiento de Señales'),
 ('Energías Renovables'), ('Redes y Comunicaciones de Datos');
