# Despliegue: servidor local + Tailscale

```
 Casa del estudiante                    Departamento de Electrónica (servidor)
┌──────────────────┐   túnel WireGuard  ┌───────────────────────────────────────┐
│ Cliente Flet     │ ═════════════════► │ tailscale serve (HTTPS :443)          │
│ + Tailscale      │   (cifrado E2E)    │   └─► uvicorn/FastAPI 127.0.0.1:8000  │
└──────────────────┘                    │         └─► MySQL 127.0.0.1:3306      │
                                        │         └─► storage/documentos/*.pdf  │
                                        └───────────────────────────────────────┘
```

Principio: **sólo la API es alcanzable, y sólo dentro de la tailnet.** MySQL y los PDF
nunca se exponen; ni siquiera a la red local de la universidad.

## 1. Base de datos (en el servidor)

```bash
sudo mysql < database/schema_mysql.sql
sudo mysql < database/seed_mysql.sql
```

Cree un usuario de aplicación **sin privilegios administrativos**:

```sql
CREATE USER 'repo_app'@'localhost' IDENTIFIED BY 'una-clave-larga';
GRANT SELECT, INSERT, UPDATE, DELETE ON repositorio_unexpo.* TO 'repo_app'@'localhost';
```

Verifique en `/etc/mysql/mysql.conf.d/mysqld.cnf` que `bind-address = 127.0.0.1`.

## 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edite DATABASE_URL y JWT_SECRET
python ../database/init_db.py --crear-admin
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Para producción, regístrelo como servicio `systemd` (`/etc/systemd/system/repositorio.service`):

```ini
[Unit]
Description=Repositorio Digital UNEXPO
After=network.target mysql.service

[Service]
User=repositorio
WorkingDirectory=/opt/repositorio-unexpo/backend
ExecStart=/opt/repositorio-unexpo/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## 3. Tailscale en el servidor

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --hostname=repositorio-unexpo
sudo tailscale serve --bg 8000        # publica la API con HTTPS sólo dentro de la tailnet
```

La API queda en `https://repositorio-unexpo.<su-tailnet>.ts.net`.
(Requiere tener activados MagicDNS y los certificados HTTPS en la consola de Tailscale.)

## 4. Control de acceso de red (ACL de Tailscale)

En la consola de administración → *Access controls*, limite qué puede alcanzar cada grupo:

```json
{
  "tagOwners": { "tag:repositorio": ["autogroup:admin"] },
  "groups": {
    "group:admins":   ["admin@ejemplo.com"],
    "group:usuarios": ["estudiante1@ejemplo.com", "profesor1@ejemplo.com"]
  },
  "acls": [
    { "action": "accept", "src": ["group:usuarios"], "dst": ["tag:repositorio:443"] },
    { "action": "accept", "src": ["group:admins"],   "dst": ["tag:repositorio:*"] }
  ]
}
```

Los usuarios sólo llegan al puerto 443 del servidor; no pueden ver otros equipos de la tailnet
ni entre ellos. Recuerde etiquetar el servidor: `sudo tailscale up --advertise-tags=tag:repositorio`.

> Revise el límite de usuarios de su plan de Tailscale. Si el número de estudiantes lo excede,
> alternativas: el programa educativo de Tailscale, *node sharing* o un servidor de control
> autoalojado (Headscale).

## 5. Equipos cliente

1. Instalar Tailscale y entrar con la cuenta invitada a la tailnet.
2. Instalar el cliente:
   ```bash
   cd frontend && pip install -r requirements.txt
   ```
3. Indicar la dirección del servidor y ejecutar:
   ```bash
   export REPO_API_URL=https://repositorio-unexpo.<su-tailnet>.ts.net   # Windows: set REPO_API_URL=...
   python main.py
   ```

Para distribuir un ejecutable sin que el usuario instale Python: `flet build windows`
(o `macos`, `linux`, `apk`) desde la carpeta `frontend/`.
