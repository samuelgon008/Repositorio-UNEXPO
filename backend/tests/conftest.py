import importlib.util
import os
import sys
import tempfile
from pathlib import Path

import pytest

# La BD de pruebas debe configurarse ANTES de importar la app.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp) / 'test.db'}"
os.environ["STORAGE_DIR"] = str(Path(_tmp) / "documentos")
os.environ["JWT_SECRET"] = "clave-de-pruebas-suficientemente-larga-para-hs256"

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app.core.security import hashear_password  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import EstadoUsuario, Rol, Usuario  # noqa: E402
from sqlalchemy import select  # noqa: E402

_spec = importlib.util.spec_from_file_location("init_db", BACKEND.parent / "database" / "init_db.py")
init_db = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(init_db)
init_db.crear_esquema_y_catalogos()

CLAVE = "Clave2026"


def crear_usuario(username: str, rol: str, estado=EstadoUsuario.activo, password: str = CLAVE) -> int:
    """Crea (si no existe) un usuario con ese rol y devuelve su id."""
    with SessionLocal() as db:
        existente = db.scalar(select(Usuario).where(Usuario.username == username))
        if existente:
            return existente.id
        n = db.scalar(select(Usuario.id).order_by(Usuario.id.desc())) or 0
        u = Usuario(cedula=f"V-{20000000 + n + 1}", nombres=username.title(), apellidos="Prueba",
                    email=f"{username}@prueba.local", username=username,
                    password_hash=hashear_password(password),
                    rol_id=db.scalar(select(Rol.id).where(Rol.nombre == rol)), estado=estado)
        db.add(u)
        db.commit()
        return u.id


crear_usuario("admin", "administrador", password="Admin2026")


def cabecera(client, username: str, password: str = CLAVE) -> dict:
    """Inicia sesión y devuelve la cabecera Authorization lista para usar."""
    r = client.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def client():
    return TestClient(app)
