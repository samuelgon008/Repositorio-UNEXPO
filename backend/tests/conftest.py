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
from app.models import EstadoUsuario, Usuario  # noqa: E402

_spec = importlib.util.spec_from_file_location("init_db", BACKEND.parent / "database" / "init_db.py")
init_db = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(init_db)
init_db.crear_esquema_y_catalogos()

with SessionLocal() as _db:
    _db.add(Usuario(cedula="V-1000000", nombres="Admin", apellidos="Prueba",
                    email="admin@unexpo.edu.ve", username="admin",
                    password_hash=hashear_password("Admin2026"),
                    rol_id=1, estado=EstadoUsuario.activo))
    _db.commit()


@pytest.fixture
def client():
    return TestClient(app)
