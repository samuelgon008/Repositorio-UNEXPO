# Interfaz web — Repositorio Digital

Next.js 16 · React 19 · Tailwind CSS 4 · íconos lucide-react.

La web no se conecta a la base de datos: pide todo a la API (backend FastAPI).
Next.js reenvía las rutas `/api/...` al backend (ver `next.config.mjs`), así que
**sólo hace falta exponer el puerto 3000**.

## Requisitos
- **Node.js 20.9 o superior** (nodejs.org, versión LTS).
- El **backend encendido** (`uvicorn app.main:app` en la carpeta `backend`).

## Ejecutar en su computadora
```bash
cd frontend-web
npm install        # sólo la primera vez
npm run dev        # http://localhost:3000
```

## Acceder desde otros dispositivos (Tailscale)
1. Instale Tailscale en la computadora servidor y en el otro dispositivo (laptop o teléfono),
   con la misma cuenta.
2. En el servidor use el modo de producción (más rápido y sin restricciones de desarrollo):
   ```bash
   npm run produccion
   ```
3. Desde el otro dispositivo abra `http://NOMBRE-DEL-SERVIDOR:3000`
   (el nombre aparece en la app de Tailscale; también sirve la IP `100.x.y.z`).
4. Si Windows pregunta por el Firewall, permita el acceso en **redes privadas**.

El backend puede seguir escuchando sólo en `127.0.0.1`: Next.js le reenvía las peticiones.
Si el backend está en otra máquina, indique su dirección con la variable `API_URL`.

## Versión de demostración en Vercel (para tutores)
Vercel no puede llegar al backend de la computadora local, así que allí la web
corre en **modo demostración**: sin base de datos, con los PDFs de prueba de
`public/demo/` y tres cuentas, una por rol: `admin`, `docente` y `estudiante`
(contraseña `unexpo2026`). `lib/demo-api.js` simula en el navegador las mismas reglas
del backend, así que el flujo completo se puede probar: el estudiante solicita
acceso, el administrador lo aprueba y el estudiante ya puede leer la tesis. Los
cambios se guardan en el navegador; «Reiniciar datos de la demo» los borra.

1. En vercel.com → **Add New… → Project** → importe el repositorio de GitHub.
2. **Root Directory:** `frontend-web` (botón *Edit*). Vercel detecta Next.js solo.
3. **Deploy.** El modo demostración se activa solo en Vercel (no hace falta
   configurar variables). Cada `git push` a `main` vuelve a publicar automáticamente.

Para regenerar los datos de la demo tras cambiar los trabajos de prueba:
```bash
cd backend
python ../database/cargar_demo.py --exportar-web
```

## Estructura
```
frontend-web/
├── app/
│   ├── layout.jsx          HTML base + script que aplica el tema antes de pintar
│   ├── page.jsx            panel principal: sesión, documentos, vistas y búsqueda
│   ├── login/page.jsx      inicio de sesión
│   └── globals.css         Tailwind, modo oscuro y color primario (violeta)
├── components/
│   ├── Sidebar.jsx         menú colapsable + modo oscuro + perfil + cerrar sesión
│   ├── BarraBusqueda.jsx   buscador superior (atajo de teclado: /)
│   ├── TarjetaProyecto.jsx tarjeta de cada tesis (acciones según el rol y el acceso)
│   ├── ModalSolicitud.jsx  estudiante: pedir acceso a una tesis
│   ├── VistaMisSolicitudes.jsx  estudiante: estado de sus solicitudes
│   ├── VistaSolicitudes.jsx     administrador: aprobar / rechazar / revocar
│   ├── VistaUsuarios.jsx        administrador: aprobar, bloquear, rol, eliminar
│   ├── VistaCategorias.jsx áreas temáticas para explorar
│   ├── ListaNotificaciones.jsx
│   └── ui.jsx              piezas compartidas (etiquetas, modal, botones…)
├── lib/
│   ├── api.js              llamadas a la API y token de sesión
│   ├── demo-api.js         API simulada del modo demostración
│   ├── datos-prueba.js     notificaciones de ejemplo (aún sin backend)
│   ├── demo-documentos.json trabajos del modo demostración (Vercel)
│   └── useTema.js          lógica del modo claro/oscuro
├── public/demo/            PDFs del modo demostración
└── next.config.mjs         reenvío /api → backend
```

## Personalizar
- **Color primario:** cambie `violet` por `blue`, `indigo`, etc. en `app/globals.css` (bloque `@theme`).
