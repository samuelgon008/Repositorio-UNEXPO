"""Gestión de usuarios por el administrador (aprobación de registros)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import requiere_permiso
from app.database import get_db
from app.models import EstadoUsuario, Rol, Usuario
from app.schemas.auth import UsuarioOut
from app.services.auth_service import a_usuario_out

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
solo_gestor = requiere_permiso("usuario.gestionar")


class AprobacionIn(BaseModel):
    rol: str = "estudiante"


@router.get("/pendientes", response_model=list[UsuarioOut])
def pendientes(db: Session = Depends(get_db), _: Usuario = Depends(solo_gestor)):
    usuarios = db.scalars(
        select(Usuario).where(Usuario.estado == EstadoUsuario.pendiente).order_by(Usuario.creado_en)
    )
    return [a_usuario_out(u) for u in usuarios]


@router.post("/{usuario_id}/aprobar", response_model=UsuarioOut)
def aprobar(usuario_id: int, datos: AprobacionIn, db: Session = Depends(get_db),
            admin: Usuario = Depends(solo_gestor)):
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(404, "Usuario no encontrado")
    rol = db.scalar(select(Rol).where(Rol.nombre == datos.rol))
    if rol is None:
        raise HTTPException(422, f"Rol desconocido: {datos.rol}")

    usuario.rol = rol
    usuario.estado = EstadoUsuario.activo
    usuario.aprobado_por = admin.id
    db.commit()
    return a_usuario_out(usuario)
