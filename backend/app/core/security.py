"""Hash de contraseñas (bcrypt) y tokens de sesión (JWT)."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

BCRYPT_MAX_BYTES = 72  # bcrypt ignora/rechaza lo que exceda 72 bytes

# Hash ficticio para gastar el mismo tiempo cuando el usuario no existe y no
# revelar, por diferencia de tiempos, qué nombres de usuario son válidos.
_HASH_FICTICIO = bcrypt.hashpw(b"contrasena-ficticia", bcrypt.gensalt()).decode()


def ahora_utc() -> datetime:
    """Fecha UTC sin zona horaria (así la guardan SQLite y MySQL DATETIME)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def hashear_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode()


def verificar_password(password: str, password_hash: str | None) -> bool:
    datos = password.encode("utf-8")
    if password_hash is None or len(datos) > BCRYPT_MAX_BYTES:
        bcrypt.checkpw(b"x", _HASH_FICTICIO.encode())
        return False
    return bcrypt.checkpw(datos, password_hash.encode())


def crear_token(usuario_id: int, rol: str, permisos: list[str]) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "rol": rol,
        "permisos": permisos,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=settings.jwt_minutos_expiracion),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algoritmo)


def decodificar_token(token: str) -> dict:
    """Lanza jwt.PyJWTError si el token es inválido o expiró."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algoritmo])
