"""Administración de usuarios: aprobar registros, bloquear, cambiar rol y eliminar."""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.api.deps import requiere_permiso
from app.core.catalogos import ROLES
from app.database import get_db
from app.models import Descarga, Documento, EstadoUsuario, Rol, Usuario
from app.schemas.auth import MensajeOut, UsuarioOut
from app.services.auth_service import a_usuario_out

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
solo_gestor = requiere_permiso("usuario.gestionar")

NombreRol = Literal[tuple(ROLES)]  # "administrador" | "docente" | "estudiante"


class RolIn(BaseModel):
    rol: NombreRol = "estudiante"


class UsuarioAdminOut(BaseModel):
    id: int
    username: str
    nombres: str
    apellidos: str
    cedula: str
    email: str
    rol: str
    estado: str
    creado_en: datetime
    ultimo_acceso: datetime | None


def _admin_out(u: Usuario) -> UsuarioAdminOut:
    return UsuarioAdminOut(
        id=u.id, username=u.username, nombres=u.nombres, apellidos=u.apellidos, cedula=u.cedula,
        email=u.email, rol=u.rol.nombre, estado=u.estado.value, creado_en=u.creado_en,
        ultimo_acceso=u.ultimo_acceso,
    )


def _otro_usuario(db: Session, usuario_id: int, admin: Usuario) -> Usuario:
    """Busca al usuario e impide que el administrador se modifique a sí mismo
    (evita quedarse bloqueado o sin privilegios por error)."""
    if usuario_id == admin.id:
        raise HTTPException(400, "No puede aplicarse esta acción a su propia cuenta")
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(404, "Usuario no encontrado")
    return usuario


def _rol(db: Session, nombre: str) -> Rol:
    return db.scalar(select(Rol).where(Rol.nombre == nombre))


@router.get("", response_model=list[UsuarioAdminOut])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(solo_gestor)):
    """Todos los usuarios: primero los pendientes de aprobación."""
    usuarios = db.scalars(select(Usuario).order_by(Usuario.apellidos, Usuario.nombres)).all()
    usuarios.sort(key=lambda u: u.estado != EstadoUsuario.pendiente)
    return [_admin_out(u) for u in usuarios]


@router.get("/pendientes", response_model=list[UsuarioOut])
def pendientes(db: Session = Depends(get_db), _: Usuario = Depends(solo_gestor)):
    usuarios = db.scalars(
        select(Usuario).where(Usuario.estado == EstadoUsuario.pendiente).order_by(Usuario.creado_en)
    )
    return [a_usuario_out(u) for u in usuarios]


@router.post("/{usuario_id}/aprobar", response_model=UsuarioAdminOut)
def aprobar(usuario_id: int, datos: RolIn, db: Session = Depends(get_db),
            admin: Usuario = Depends(solo_gestor)):
    """Activa una cuenta registrada y le asigna su rol."""
    usuario = _otro_usuario(db, usuario_id, admin)
    if usuario.estado != EstadoUsuario.pendiente:
        raise HTTPException(409, "La cuenta no está pendiente de aprobación")
    usuario.rol = _rol(db, datos.rol)
    usuario.estado = EstadoUsuario.activo
    usuario.aprobado_por = admin.id
    db.commit()
    return _admin_out(usuario)


@router.post("/{usuario_id}/bloquear", response_model=UsuarioAdminOut)
def bloquear(usuario_id: int, db: Session = Depends(get_db), admin: Usuario = Depends(solo_gestor)):
    """Suspende la cuenta: pierde el acceso de inmediato, aunque tenga una sesión abierta."""
    usuario = _otro_usuario(db, usuario_id, admin)
    usuario.estado = EstadoUsuario.suspendido
    db.commit()
    return _admin_out(usuario)


@router.post("/{usuario_id}/desbloquear", response_model=UsuarioAdminOut)
def desbloquear(usuario_id: int, db: Session = Depends(get_db), admin: Usuario = Depends(solo_gestor)):
    usuario = _otro_usuario(db, usuario_id, admin)
    if usuario.estado != EstadoUsuario.suspendido:
        raise HTTPException(409, "La cuenta no está bloqueada")
    usuario.estado = EstadoUsuario.activo
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    db.commit()
    return _admin_out(usuario)


@router.patch("/{usuario_id}/rol", response_model=UsuarioAdminOut)
def cambiar_rol(usuario_id: int, datos: RolIn, db: Session = Depends(get_db),
                admin: Usuario = Depends(solo_gestor)):
    usuario = _otro_usuario(db, usuario_id, admin)
    usuario.rol = _rol(db, datos.rol)
    db.commit()
    return _admin_out(usuario)


@router.delete("/{usuario_id}", response_model=MensajeOut)
def eliminar(usuario_id: int, db: Session = Depends(get_db), admin: Usuario = Depends(solo_gestor)):
    """Elimina la cuenta y sus solicitudes. Si ya tiene historial (descargas o
    tesis cargadas) no se borra, para no perder la auditoría: se debe bloquear."""
    usuario = _otro_usuario(db, usuario_id, admin)
    con_historial = db.scalar(select(
        exists().where(Descarga.usuario_id == usuario.id) | exists().where(Documento.subido_por == usuario.id)
    ))
    if con_historial:
        raise HTTPException(409, "Este usuario tiene historial de descargas o tesis cargadas; "
                                 "bloquéelo en lugar de eliminarlo")
    nombre = usuario.username
    db.delete(usuario)
    db.commit()
    return MensajeOut(detail=f"Usuario «{nombre}» eliminado")
