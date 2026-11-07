import importlib.util
from pathlib import Path

from sqlalchemy import func, select

from app.core.security import hashear_password
from app.database import SessionLocal
from app.models import Descarga, EstadoUsuario, Usuario

_spec = importlib.util.spec_from_file_location(
    "cargar_demo", Path(__file__).resolve().parents[2] / "database" / "cargar_demo.py")
cargar_demo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cargar_demo)


def _token(client, username, password):
    r = client.post("/auth/login", json={"username": username, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _crear_invitado():
    with SessionLocal() as db:
        if not db.scalar(select(Usuario).where(Usuario.username == "visitante")):
            db.add(Usuario(cedula="V-5000000", nombres="Visi", apellidos="Tante",
                           email="visitante@ejemplo.com", username="visitante",
                           password_hash=hashear_password("Visita2026"), rol_id=4,
                           estado=EstadoUsuario.activo))
            db.commit()


def test_carga_demo_es_idempotente():
    primera = cargar_demo.cargar()
    assert cargar_demo.cargar() == 0
    with SessionLocal() as db:
        from app.models import Documento
        assert db.scalar(select(func.count()).select_from(Documento)) >= primera


def test_listar_y_detalle(client):
    cargar_demo.cargar()
    cab = _token(client, "admin", "Admin2026")
    docs = client.get("/documentos", headers=cab).json()
    assert len(docs) == len(cargar_demo.TRABAJOS)
    assert docs[0]["fecha"] >= docs[-1]["fecha"]  # más recientes primero

    lora = next(d for d in docs if "LoRaWAN" in d["titulo"])
    assert lora["autores"] == ["José Gregorio Salazar"]
    assert lora["etiquetas"] == ["Telecomunicaciones"]
    assert "lorawan" in lora["palabras_clave"]
    assert client.get(f"/documentos/{lora['id']}", headers=cab).json()["id"] == lora["id"]
    assert client.get("/documentos/99999", headers=cab).status_code == 404


def test_descarga_pdf_y_auditoria(client):
    cargar_demo.cargar()
    cab = _token(client, "admin", "Admin2026")
    doc = client.get("/documentos", headers=cab).json()[0]

    with SessionLocal() as db:
        antes = db.scalar(select(func.count()).select_from(Descarga))
    r = client.get(f"/documentos/{doc['id']}/descargar", headers=cab)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF-") and r.content.rstrip().endswith(b"%%EOF")
    assert doc["nombre_archivo"] in r.headers["content-disposition"]
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Descarga)) == antes + 1


def test_permisos(client):
    cargar_demo.cargar()
    assert client.get("/documentos").status_code == 401  # sin sesión

    _crear_invitado()
    cab = _token(client, "visitante", "Visita2026")
    docs = client.get("/documentos", headers=cab)
    assert docs.status_code == 200  # el invitado puede consultar…
    r = client.get(f"/documentos/{docs.json()[0]['id']}/descargar", headers=cab)
    assert r.status_code == 403     # …pero no descargar
