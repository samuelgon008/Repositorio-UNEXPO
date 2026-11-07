"""Roles, permisos y catálogos del sistema: FUENTE ÚNICA DE VERDAD.

Al arrancar el servidor (y con database/init_db.py) estos valores se
sincronizan con la base de datos. database/seed_mysql.sql los replica para
quien cree la BD a mano; un test verifica que ambos coincidan.
"""

PERMISOS = {
    "documento.ver": "Buscar y ver la ficha y el resumen de las tesis",
    "documento.leer": "Abrir el PDF completo en línea sin solicitud",
    "documento.descargar": "Descargar cualquier PDF sin solicitud",
    "documento.editar": "Editar datos de las tesis y publicarlas u ocultarlas",
    "documento.eliminar": "Eliminar tesis del repositorio",
    "solicitud.crear": "Solicitar acceso al PDF de una tesis",
    "solicitud.gestionar": "Aprobar, rechazar y revocar solicitudes de acceso",
    "usuario.gestionar": "Aprobar, bloquear, eliminar y cambiar el rol de usuarios",
    "auditoria.ver": "Consultar registros de acceso y descargas",
}

# nombre: (nivel, descripción, permisos). El orden define los id en una BD nueva.
ROLES = {
    # El administrador tiene todo salvo solicitar acceso (ya lee y descarga sin pedirlo)
    "administrador": (1, "Control total del repositorio", [p for p in PERMISOS if p != "solicitud.crear"]),
    "docente": (2, "Consulta las fichas y lee las tesis en línea", ["documento.ver", "documento.leer"]),
    "estudiante": (3, "Consulta las fichas y solicita acceso a los PDF", ["documento.ver", "solicitud.crear"]),
}

ROL_POR_DEFECTO = "estudiante"   # rol de quien se registra
DIAS_ACCESO_SOLICITUD = 30       # vigencia de un acceso aprobado

TIPOS_DOCUMENTO = [
    ("TEG", "Trabajo Especial de Grado"),
    ("IEI", "Informe de Entrenamiento Industrial"),
]

ETIQUETAS = [
    "Telecomunicaciones", "Control y Automatización", "Electrónica de Potencia",
    "Instrumentación", "Sistemas Digitales y Embebidos", "Procesamiento de Señales",
    "Energías Renovables", "Redes y Comunicaciones de Datos",
]
