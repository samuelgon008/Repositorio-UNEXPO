from app.config import settings


def _login(client, username, password):
    return client.post("/auth/login", json={"username": username, "password": password})


def test_login_admin_correcto(client):
    r = _login(client, "ADMIN ", "Admin2026")  # normaliza mayúsculas y espacios
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["usuario"]["rol"] == "administrador"
    assert "usuario.gestionar" in cuerpo["usuario"]["permisos"]

    yo = client.get("/auth/yo", headers={"Authorization": f"Bearer {cuerpo['access_token']}"})
    assert yo.status_code == 200 and yo.json()["username"] == "admin"


def test_credenciales_invalidas_mismo_mensaje(client):
    a = _login(client, "admin", "incorrecta")
    b = _login(client, "no_existe", "incorrecta")
    assert a.status_code == b.status_code == 401
    assert a.json()["detail"] == b.json()["detail"]


def test_registro_pendiente_y_aprobacion(client):
    nuevo = {"cedula": "v27123456", "nombres": "Ana", "apellidos": "Pérez",
             "email": "ana@gmail.com", "username": "ana.perez", "password": "Clave2026"}
    assert client.post("/auth/registro", json=nuevo).status_code == 201
    assert client.post("/auth/registro", json=nuevo).status_code == 409

    r = _login(client, "ana.perez", "Clave2026")
    assert r.status_code == 403 and "pendiente" in r.json()["detail"]

    token = _login(client, "admin", "Admin2026").json()["access_token"]
    cab = {"Authorization": f"Bearer {token}"}
    pendientes = client.get("/usuarios/pendientes", headers=cab).json()
    ana = next(u for u in pendientes if u["username"] == "ana.perez")
    assert client.post(f"/usuarios/{ana['id']}/aprobar", json={"rol": "estudiante"},
                       headers=cab).status_code == 200

    r = _login(client, "ana.perez", "Clave2026")
    assert r.status_code == 200
    assert r.json()["usuario"]["permisos"] == ["documento.ver", "solicitud.crear"]

    # Un estudiante no puede gestionar usuarios
    cab_ana = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert client.get("/usuarios/pendientes", headers=cab_ana).status_code == 403


def test_registro_rechaza_password_debil(client):
    r = client.post("/auth/registro", json={
        "cedula": "V-30111222", "nombres": "Luis", "apellidos": "Gil",
        "email": "luis@gmail.com", "username": "lgil", "password": "solamenteletras"})
    assert r.status_code == 422


def test_bloqueo_por_intentos_fallidos(client):
    client.post("/auth/registro", json={
        "cedula": "V-28999888", "nombres": "Bea", "apellidos": "Rojas",
        "email": "bea@gmail.com", "username": "brojas", "password": "Clave2026"})
    for _ in range(settings.max_intentos_fallidos):
        assert _login(client, "brojas", "mala1234").status_code == 401
    # Ahora, aun con la contraseña correcta, la cuenta queda bloqueada
    r = _login(client, "brojas", "Clave2026")
    assert r.status_code == 423


def test_token_invalido(client):
    r = client.get("/auth/yo", headers={"Authorization": "Bearer basura"})
    assert r.status_code == 401
