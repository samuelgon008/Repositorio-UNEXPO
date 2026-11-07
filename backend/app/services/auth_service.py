"""Reglas de negocio de autenticación: validación de credenciales contra la
base de datos, bloqueo por intentos fallidos y bitácora de accesos."""
from datetime import timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.catalogos import ROL_POR_DEFECTO
from app.core.security import ahora_utc, hashear_password, verificar_password
from app.models import EstadoUsuario, RegistroAcceso, Rol, Usuario
from app.schemas.auth import RegistroIn, UsuarioOut

MSG_CREDENCIALES = "Usuario o contraseña incorrectos"


class AuthError(Exception):
    def __init__(self, status_code: int, mensaje: str):
        self.status_code = status_code
        self.mensaje = mensaje
        super().__init__(mensaje)


def _registrar(db: Session, username: str, exitoso: bool, motivo: str | None,
               ip: str | None, usuario: Usuario | None = None) -> None:
    db.add(RegistroAcceso(
        usuario_id=usuario.id if usuario else None,
        username=username[:40], exitoso=exitoso, motivo=motivo, ip=ip,
    ))


def autenticar(db: Session, username: str, password: str, ip: str | None) -> Usuario:
    usuario = db.scalar(select(Usuario).where(Usuario.username == username))
    ahora = ahora_utc()

    if usuario is None:
        verificar_password(password, None)  # mismo costo de tiempo
        _registrar(db, username, False, "usuario_inexistente", ip)
        db.commit()
        raise AuthError(401, MSG_CREDENCIALES)

    if usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
        minutos = int((usuario.bloqueado_hasta - ahora).total_seconds() // 60) + 1
        _registrar(db, username, False, "cuenta_bloqueada", ip, usuario)
        db.commit()
        raise AuthError(423, f"Cuenta bloqueada por intentos fallidos. Intente en {minutos} min.")

    if not verificar_password(password, usuario.password_hash):
        usuario.intentos_fallidos += 1
        motivo = "password_incorrecta"
        if usuario.intentos_fallidos >= settings.max_intentos_fallidos:
            usuario.bloqueado_hasta = ahora + timedelta(minutes=settings.minutos_bloqueo)
            usuario.intentos_fallidos = 0
            motivo = "bloqueo_activado"
        _registrar(db, username, False, motivo, ip, usuario)
        db.commit()
        raise AuthError(401, MSG_CREDENCIALES)

    # La contraseña es correcta: recién ahora es seguro informar el estado.
    if usuario.estado == EstadoUsuario.pendiente:
        _registrar(db, username, False, "pendiente_aprobacion", ip, usuario)
        db.commit()
        raise AuthError(403, "Su cuenta está pendiente de aprobación por un administrador.")
    if usuario.estado == EstadoUsuario.suspendido:
        _registrar(db, username, False, "suspendido", ip, usuario)
        db.commit()
        raise AuthError(403, "Su cuenta está suspendida. Contacte al departamento.")

    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    usuario.ultimo_acceso = ahora
    _registrar(db, username, True, None, ip, usuario)
    db.commit()
    return usuario


def registrar_usuario(db: Session, datos: RegistroIn) -> Usuario:
    duplicado = db.scalar(select(Usuario).where(or_(
        Usuario.username == datos.username,
        Usuario.email == datos.email,
        Usuario.cedula == datos.cedula,
    )))
    if duplicado:
        raise AuthError(409, "Ya existe una cuenta con ese usuario, correo o cédula.")

    rol = db.scalar(select(Rol).where(Rol.nombre == ROL_POR_DEFECTO))
    usuario = Usuario(
        cedula=datos.cedula, nombres=datos.nombres.strip(), apellidos=datos.apellidos.strip(),
        email=datos.email, username=datos.username,
        password_hash=hashear_password(datos.password),
        rol_id=rol.id, estado=EstadoUsuario.pendiente,
    )
    db.add(usuario)
    db.commit()
    return usuario


def a_usuario_out(usuario: Usuario) -> UsuarioOut:
    return UsuarioOut(
        id=usuario.id, username=usuario.username, nombres=usuario.nombres,
        apellidos=usuario.apellidos, email=usuario.email, rol=usuario.rol.nombre,
        estado=usuario.estado.value, permisos=usuario.codigos_permiso,
    )
