import importlib.util
from pathlib import Path

from sqlalchemy import func, select

from app.config import settings
from app.database import SessionLocal
from app.models import Descarga, Documento
from conftest import cabecera, crear_usuario

_spec = importlib.util.spec_from_file_location(
    "cargar_demo", Path(__file__).resolve().parents[2] / "database" / "cargar_demo.py")
cargar_demo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cargar_demo)


def _primer_doc(client, cab):
    return client.get("/documentos", headers=cab).json()[0]


def test_carga_demo_es_idempotente():
    cargar_demo.cargar()
    assert cargar_demo.cargar() == 0
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Documento)) >= len(cargar_demo.TRABAJOS)


def test_listar_y_detalle(client):
    cargar_demo.cargar()
    cab = cabecera(client, "admin", "Admin2026")
    docs = client.get("/documentos", headers=cab).json()
    assert len(docs) == len(cargar_demo.TRABAJOS)
    assert docs[0]["fecha"] >= docs[-1]["fecha"]  # más recientes primero

    lora = next(d for d in docs if "LoRaWAN" in d["titulo"])
    assert lora["autores"] == ["José Gregorio Salazar"]
    assert lora["etiquetas"] == ["Telecomunicaciones"]
    assert "lorawan" in lora["palabras_clave"]
    assert client.get(f"/documentos/{lora['id']}", headers=cab).json()["id"] == lora["id"]
    assert client.get("/documentos/99999", headers=cab).status_code == 404


def test_administrador_lee_y_descarga_con_auditoria(client):
    cargar_demo.cargar()
    cab = cabecera(client, "admin", "Admin2026")
    doc = _primer_doc(client, cab)
    assert doc["puede_leer"] and doc["puede_descargar"]

    ver = client.get(f"/documentos/{doc['id']}/ver", headers=cab)
    assert ver.status_code == 200 and ver.headers["content-disposition"].startswith("inline")

    with SessionLocal() as db:
        antes = db.scalar(select(func.count()).select_from(Descarga))
    r = client.get(f"/documentos/{doc['id']}/descargar", headers=cab)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.headers["content-disposition"].startswith("attachment")
    assert r.content.startswith(b"%PDF-") and r.content.rstrip().endswith(b"%%EOF")
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Descarga)) == antes + 1


def test_docente_lee_pero_no_descarga(client):
    cargar_demo.cargar()
    crear_usuario("docente1", "docente")
    cab = cabecera(client, "docente1")
    doc = _primer_doc(client, cab)
    assert doc["puede_leer"] and not doc["puede_descargar"]
    assert client.get(f"/documentos/{doc['id']}/ver", headers=cab).status_code == 200
    assert client.get(f"/documentos/{doc['id']}/descargar", headers=cab).status_code == 403
    assert client.post("/solicitudes", json={"documento_id": doc["id"]}, headers=cab).status_code == 403


def test_estudiante_sin_solicitud_solo_ve_la_ficha(client):
    cargar_demo.cargar()
    assert client.get("/documentos").status_code == 401  # sin sesión
    crear_usuario("estudiante1", "estudiante")
    cab = cabecera(client, "estudiante1")
    doc = _primer_doc(client, cab)
    assert doc["resumen"] and not doc["puede_leer"] and not doc["puede_descargar"]
    for accion in ("ver", "descargar"):
        r = client.get(f"/documentos/{doc['id']}/{accion}", headers=cab)
        assert r.status_code == 403 and "solicitud" in r.json()["detail"]


def test_admin_oculta_edita_y_elimina_tesis(client):
    cargar_demo.cargar()
    crear_usuario("estudiante2", "estudiante")
    adm, est = cabecera(client, "admin", "Admin2026"), cabecera(client, "estudiante2")
    doc = _primer_doc(client, adm)

    # Ocultar: el estudiante deja de verla, el administrador no
    r = client.patch(f"/documentos/{doc['id']}", json={"publicado": False, "titulo": "Título corregido"}, headers=adm)
    assert r.status_code == 200 and r.json()["titulo"] == "Título corregido" and not r.json()["publicado"]
    assert doc["id"] not in [d["id"] for d in client.get("/documentos", headers=est).json()]
    assert doc["id"] in [d["id"] for d in client.get("/documentos", headers=adm).json()]
    # Sólo el administrador puede editar
    assert client.patch(f"/documentos/{doc['id']}", json={"publicado": True}, headers=est).status_code == 403

    # Eliminar: desaparece el registro y el archivo
    with SessionLocal() as db:
        archivo = settings.storage_dir / db.get(Documento, doc["id"]).ruta_archivo
    assert client.delete(f"/documentos/{doc['id']}", headers=est).status_code == 403
    assert client.delete(f"/documentos/{doc['id']}", headers=adm).status_code == 200
    assert client.get(f"/documentos/{doc['id']}", headers=adm).status_code == 404
    assert not archivo.exists()
