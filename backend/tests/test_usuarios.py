from app.models import EstadoUsuario
from conftest import cabecera, crear_usuario
from test_documentos import cargar_demo


def _adm(client):
    return cabecera(client, "admin", "Admin2026")


def test_listar_usuarios_solo_admin(client):
    crear_usuario("doc.lista", "docente")
    adm = _adm(client)
    usuarios = client.get("/usuarios", headers=adm).json()
    assert {"admin", "doc.lista"} <= {u["username"] for u in usuarios}
    assert client.get("/usuarios", headers=cabecera(client, "doc.lista")).status_code == 403


def test_bloquear_corta_el_acceso_al_instante(client):
    uid = crear_usuario("est.bloqueo", "estudiante")
    adm, est = _adm(client), cabecera(client, "est.bloqueo")
    assert client.get("/auth/yo", headers=est).status_code == 200

    assert client.post(f"/usuarios/{uid}/bloquear", headers=adm).json()["estado"] == "suspendido"
    assert client.get("/auth/yo", headers=est).status_code == 401          # su sesión abierta muere
    r = client.post("/auth/login", json={"username": "est.bloqueo", "password": "Clave2026"})
    assert r.status_code == 403 and "suspendida" in r.json()["detail"]

    assert client.post(f"/usuarios/{uid}/desbloquear", headers=adm).json()["estado"] == "activo"
    assert client.get("/auth/yo", headers=cabecera(client, "est.bloqueo")).status_code == 200


def test_cambiar_rol(client):
    uid = crear_usuario("est.ascenso", "estudiante")
    r = client.patch(f"/usuarios/{uid}/rol", json={"rol": "docente"}, headers=_adm(client))
    assert r.json()["rol"] == "docente"
    yo = client.get("/auth/yo", headers=cabecera(client, "est.ascenso")).json()
    assert yo["permisos"] == ["documento.leer", "documento.ver"]
    assert client.patch(f"/usuarios/{uid}/rol", json={"rol": "bibliotecario"}, headers=_adm(client)).status_code == 422


def test_aprobar_registro_con_rol(client):
    uid = crear_usuario("doc.nuevo", "estudiante", estado=EstadoUsuario.pendiente)
    r = client.post(f"/usuarios/{uid}/aprobar", json={"rol": "docente"}, headers=_adm(client))
    assert r.json()["estado"] == "activo" and r.json()["rol"] == "docente"


def test_el_admin_no_puede_modificarse_a_si_mismo(client):
    adm = _adm(client)
    yo = client.get("/auth/yo", headers=adm).json()["id"]
    for metodo, ruta, cuerpo in [("post", "bloquear", None), ("patch", "rol", {"rol": "estudiante"}),
                                 ("delete", "", None)]:
        r = client.request(metodo.upper(), f"/usuarios/{yo}/{ruta}".rstrip("/"), json=cuerpo, headers=adm)
        assert r.status_code == 400


def test_eliminar_usuario(client):
    adm = _adm(client)
    sin_historial = crear_usuario("borrable", "estudiante")
    assert client.delete(f"/usuarios/{sin_historial}", headers=adm).status_code == 200
    assert client.post("/auth/login", json={"username": "borrable", "password": "Clave2026"}).status_code == 401

    # Con descargas registradas no se borra (se protege la auditoría): hay que bloquearlo
    cargar_demo.cargar()
    con_historial = crear_usuario("descargador", "docente")
    client.patch(f"/usuarios/{con_historial}/rol", json={"rol": "administrador"}, headers=adm)
    cab = cabecera(client, "descargador")
    doc = client.get("/documentos", headers=cab).json()[0]
    client.get(f"/documentos/{doc['id']}/descargar", headers=cab)
    r = client.delete(f"/usuarios/{con_historial}", headers=adm)
    assert r.status_code == 409 and "bloquéelo" in r.json()["detail"]
