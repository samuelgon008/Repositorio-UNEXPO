from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_usuario_actual
from app.core.security import crear_token
from app.database import get_db
from app.models import Usuario
from app.schemas.auth import LoginIn, MensajeOut, RegistroIn, TokenOut, UsuarioOut
from app.services import auth_service
from app.services.auth_service import AuthError

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenOut)
def login(datos: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    try:
        usuario = auth_service.autenticar(db, datos.username, datos.password, ip)
    except AuthError as e:
        raise HTTPException(e.status_code, e.mensaje)

    token = crear_token(usuario.id, usuario.rol.nombre, usuario.codigos_permiso)
    return TokenOut(access_token=token, usuario=auth_service.a_usuario_out(usuario))


@router.post("/registro", response_model=MensajeOut, status_code=status.HTTP_201_CREATED)
def registro(datos: RegistroIn, db: Session = Depends(get_db)):
    try:
        auth_service.registrar_usuario(db, datos)
    except AuthError as e:
        raise HTTPException(e.status_code, e.mensaje)
    return MensajeOut(detail="Registro recibido. Un administrador debe aprobar su cuenta.")


@router.get("/yo", response_model=UsuarioOut)
def yo(usuario: Usuario = Depends(get_usuario_actual)):
    return auth_service.a_usuario_out(usuario)
