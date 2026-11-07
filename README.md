# Repositorio Digital de TEG e Informes de Entrenamiento Industrial

Departamento de Ingeniería Electrónica — UNEXPO.

| Capa | Tecnología |
|---|---|
| Interfaz | Python + **Flet 1.0** (escritorio, web o móvil con el mismo código) |
| API | **FastAPI** + SQLAlchemy 2 |
| Base de datos | **MySQL 8** en producción · **SQLite** en pruebas (sólo cambia `DATABASE_URL`) |
| Seguridad | bcrypt, JWT, control de acceso por roles y permisos, bloqueo por intentos fallidos |
| Red | Servidor local publicado únicamente dentro de una red **Tailscale** |

## Documentación

1. [Modelo Entidad-Relación](docs/01_modelo_entidad_relacion.md)
2. [Arquitectura de carpetas](#2-arquitectura-de-carpetas) (abajo)
3. [Despliegue con Tailscale](docs/03_despliegue_tailscale.md)

## 2. Arquitectura de carpetas

```
repositorio-unexpo/
├── backend/                     ← SERVIDOR (único que toca la BD y los PDF)
│   ├── app/
│   │   ├── main.py              punto de entrada FastAPI
│   │   ├── config.py            variables de entorno (.env)
│   │   ├── database.py          motor SQLAlchemy y sesión por petición
│   │   ├── models/              tablas ORM (seguridad, documentos, auditoría)
│   │   ├── schemas/             validación de entradas/salidas (Pydantic)
│   │   ├── core/security.py     bcrypt + JWT
│   │   ├── services/            reglas de negocio (auth_service.py, …)
│   │   └── api/
│   │       ├── deps.py          usuario actual y requiere_permiso("…")
│   │       └── routes/          endpoints: auth.py, usuarios.py, (documentos.py)
│   ├── storage/documentos/      PDFs (fuera de la BD, fuera de Git)
│   ├── tests/                   pruebas automáticas (pytest)
│   ├── requirements.txt
│   └── .env.example
│
├── frontend-web/                ← INTERFAZ WEB Next.js (ver frontend-web/README.md)
├── frontend/                    ← CLIENTE FLET de escritorio (nunca se conecta a MySQL)
│   ├── main.py                  arranque y navegación entre vistas
│   ├── app/
│   │   ├── config.py            REPO_API_URL (dirección Tailscale del servidor)
│   │   ├── state.py             sesión del usuario y sus permisos
│   │   ├── services/api_client.py   llamadas HTTP asíncronas a la API
│   │   ├── components/ui.py     piezas visuales reutilizables
│   │   └── views/               login, registro, inicio, (búsqueda, documento…)
│   └── requirements.txt
│
├── database/                    ← SCRIPTS DE BASE DE DATOS
│   ├── schema_mysql.sql         DDL de producción
│   ├── seed_mysql.sql           roles, permisos, tipos, etiquetas
│   ├── init_db.py               crea tablas + catálogos + administrador
│   └── cargar_demo.py           genera y registra PDFs de prueba
│
└── docs/                        ← modelo ER, despliegue
```

**Por qué esta separación:** el cliente sólo habla HTTP con la API. Las credenciales de
MySQL viven únicamente en el servidor, y cada permiso se verifica en el backend, por lo que
modificar o descompilar el cliente no da acceso a nada. El mismo `frontend/` puede
compilarse como app de escritorio, web o Android sin tocar el backend.

## Inicio rápido (pruebas locales con SQLite)

Terminal 1 — servidor:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python ../database/init_db.py --crear-admin
python ../database/cargar_demo.py --usuarios-prueba   # 8 tesis de prueba + un docente y un estudiante
uvicorn app.main:app --reload
```

Documentación interactiva de la API: <http://127.0.0.1:8000/docs>

Terminal 2 — interfaz web (Next.js, requiere Node.js 20.9+):

```bash
cd frontend-web
npm install
npm run dev                            # http://localhost:3000
```

Interfaz de escritorio alternativa (Flet): `cd frontend && python main.py`.

Pruebas automáticas:

```bash
cd backend && pytest -q
```

## Roles

| | Ver fichas y resumen | Leer el PDF en línea | Descargar | Administrar |
|---|:-:|:-:|:-:|---|
| **Administrador** | ✔ | ✔ | ✔ | Usuarios (aprobar, bloquear, cambiar rol, eliminar), solicitudes y tesis (ocultar, editar, eliminar) |
| **Docente** | ✔ | ✔ | — | — |
| **Estudiante** | ✔ | con solicitud aprobada | con solicitud aprobada | Sólo solicita acceso |

**Solicitud de acceso:** el estudiante pide acceso a una tesis concreta (con un motivo opcional);
el administrador la aprueba —habilita leer y descargar **esa** tesis durante 30 días—, la rechaza
con una nota, o revoca un acceso vigente. Los roles y permisos se definen en
`backend/app/core/catalogos.py` y el servidor los sincroniza con la base de datos al arrancar
(una base de datos de la versión anterior se actualiza sola).

### Probar los roles en su computadora
`cargar_demo.py --usuarios-prueba` crea dos cuentas de prueba (contraseña `Prueba2026`):
`docente.prueba` y `estudiante.prueba`. El administrador es el suyo (`init_db.py --crear-admin`).

1. Entre como **estudiante.prueba** → pulse «Solicitar acceso» en una tesis.
2. Entre como **administrador** → *Solicitudes* → «Aprobar 30 días».
3. Vuelva como estudiante → esa tesis ya muestra «Leer tesis» y «PDF».
4. Entre como **docente.prueba** → puede leer cualquier tesis, pero no descargar.
5. Como administrador, en *Usuarios*, bloquee a alguien: no podrá volver a entrar.

## Flujo de autenticación

1. **Registro** → la cuenta se crea con rol `estudiante` y estado `pendiente`.
2. El **administrador** la aprueba (`POST /usuarios/{id}/aprobar`), pudiendo asignar otro rol.
3. **Login** → el servidor valida contra la BD y devuelve un JWT (60 min) con rol y permisos.
4. Cada petición posterior relee al usuario: una suspensión o un cambio de rol surte efecto de inmediato.
5. Tras 5 contraseñas erróneas la cuenta se bloquea 15 minutos. Todos los intentos quedan en `registro_accesos`.

Para no revelar qué usuarios existen, "usuario inexistente" y "contraseña incorrecta"
devuelven el mismo mensaje y tardan lo mismo; el estado *pendiente/suspendido* sólo se informa
cuando la contraseña es correcta.
