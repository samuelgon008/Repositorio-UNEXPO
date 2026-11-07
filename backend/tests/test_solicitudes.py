from datetime import timedelta

from app.core.security import ahora_utc
from app.database import SessionLocal
from app.models import SolicitudAcceso
from conftest import cabecera, crear_usuario
from test_documentos import cargar_demo


def _preparar(client, estudiante):
    cargar_demo.cargar()
    crear_usuario(estudiante, "estudiante")
    adm, est = cabecera(client, "admin", "Admin2026"), cabecera(client, estudiante)
    doc = client.get("/documentos", headers=est).json()[1]
    return adm, est, doc


def _doc(client, cab, doc_id):
    return next(d for d in client.get("/documentos", headers=cab).json() if d["id"] == doc_id)


def test_flujo_completo_solicitar_aprobar_y_acceder(client):
    adm, est, doc = _preparar(client, "est.flujo")

    r = client.post("/solicitudes", json={"documento_id": doc["id"], "motivo": "Antecedente para mi TEG"}, headers=est)
    assert r.status_code == 201 and r.json()["estado"] == "pendiente"
    sid = r.json()["id"]
    # Duplicado mientras está pendiente
    assert client.post("/solicitudes", json={"documento_id": doc["id"]}, headers=est).status_code == 409
    # La tarjeta muestra la solicitud y sigue sin acceso
    tarjeta = _doc(client, est, doc["id"])
    assert tarjeta["solicitud"]["estado"] == "pendiente" and not tarjeta["puede_leer"]

    # El estudiante no puede aprobarse a sí mismo
    assert client.post(f"/solicitudes/{sid}/aprobar", headers=est).status_code == 403
    # El administrador la ve entre las pendientes y la aprueba
    pendientes = client.get("/solicitudes?estado=pendiente", headers=adm).json()
    assert any(s["id"] == sid and s["motivo"] == "Antecedente para mi TEG" for s in pendientes)
    r = client.post(f"/solicitudes/{sid}/aprobar", json={"nota": "Aprobado"}, headers=adm)
    assert r.status_code == 200 and r.json()["estado"] == "aprobada"
    vence = r.json()["vence_en"]
    assert vence[:10] == (ahora_utc() + timedelta(days=30)).date().isoformat()

    # Ahora puede leer y descargar ESA tesis…
    tarjeta = _doc(client, est, doc["id"])
    assert tarjeta["puede_leer"] and tarjeta["puede_descargar"]
    assert client.get(f"/documentos/{doc['id']}/ver", headers=est).status_code == 200
    assert client.get(f"/documentos/{doc['id']}/descargar", headers=est).status_code == 200
    # …pero no las demás
    otra = next(d for d in client.get("/documentos", headers=est).json() if d["id"] != doc["id"])
    assert not otra["puede_leer"]
    # Con acceso vigente no puede volver a solicitar
    assert client.post("/solicitudes", json={"documento_id": doc["id"]}, headers=est).status_code == 409
    # Aparece en "Mis solicitudes"
    assert client.get("/solicitudes/mias", headers=est).json()[0]["id"] == sid


def test_rechazo_con_nota_y_nueva_solicitud(client):
    adm, est, doc = _preparar(client, "est.rechazo")
    sid = client.post("/solicitudes", json={"documento_id": doc["id"]}, headers=est).json()["id"]
    r = client.post(f"/solicitudes/{sid}/rechazar", json={"nota": "Indique el motivo"}, headers=adm)
    assert r.json()["estado"] == "rechazada" and r.json()["nota_admin"] == "Indique el motivo"
    # No se puede aprobar una solicitud ya rechazada
    assert client.post(f"/solicitudes/{sid}/aprobar", headers=adm).status_code == 409
    assert not _doc(client, est, doc["id"])["puede_leer"]
    # Puede volver a pedirlo
    assert client.post("/solicitudes", json={"documento_id": doc["id"], "motivo": "Revisión"},
                       headers=est).status_code == 201


def test_revocar_quita_el_acceso(client):
    adm, est, doc = _preparar(client, "est.revocar")
    sid = client.post("/solicitudes", json={"documento_id": doc["id"]}, headers=est).json()["id"]
    client.post(f"/solicitudes/{sid}/aprobar", headers=adm)
    assert client.post(f"/solicitudes/{sid}/revocar", headers=adm).json()["estado"] == "revocada"
    assert client.get(f"/documentos/{doc['id']}/ver", headers=est).status_code == 403


def test_acceso_vencido(client):
    adm, est, doc = _preparar(client, "est.vence")
    sid = client.post("/solicitudes", json={"documento_id": doc["id"]}, headers=est).json()["id"]
    client.post(f"/solicitudes/{sid}/aprobar", headers=adm)
    with SessionLocal() as db:  # simula que pasaron los 30 días
        db.get(SolicitudAcceso, sid).vence_en = ahora_utc() - timedelta(minutes=1)
        db.commit()
    tarjeta = _doc(client, est, doc["id"])
    assert tarjeta["solicitud"]["estado"] == "vencida" and not tarjeta["puede_leer"]
    assert client.get(f"/documentos/{doc['id']}/descargar", headers=est).status_code == 403
    assert client.post("/solicitudes", json={"documento_id": doc["id"]}, headers=est).status_code == 201
