"""Dependencias de FastAPI: usuario autenticado y control de permisos."""
from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decodificar_token
from app.database import get_db
from app.models import EstadoUsuario, Usuario

_bearer = HTTPBearer(auto_error=False)


def get_usuario_actual(
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    no_autorizado = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Sesión inválida o expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if cred is None:
        raise no_autorizado
    try:
        payload = decodificar_token(cred.credentials)
    except jwt.PyJWTError:
        raise no_autorizado

    # Se relee el usuario en cada petición: si el admin lo suspende o le
    # cambia el rol, el efecto es inmediato aunque el token siga vigente.
    usuario = db.get(Usuario, int(payload["sub"]))
    if usuario is None or usuario.estado != EstadoUsuario.activo:
        raise no_autorizado
    return usuario


def requiere_permiso(codigo: str) -> Callable[..., Usuario]:
    def _verificar(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
        if codigo not in usuario.codigos_permiso:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tiene permiso para esta acción")
        return usuario
    return _verificar
