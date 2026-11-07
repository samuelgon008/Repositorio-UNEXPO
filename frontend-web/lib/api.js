/* ==========================================================================
   Cliente de la API del repositorio. Todas las rutas van a /api/... y
   next.config.mjs las reenvía al backend FastAPI.

   MODO DEMOSTRACIÓN (NEXT_PUBLIC_MODO_DEMO=1, p. ej. en Vercel): no hay
   backend; el login usa una cuenta fija y los documentos/PDFs salen de
   lib/demo-documentos.json y public/demo/ (generados con
   `python ../database/cargar_demo.py --exportar-web`).
   ========================================================================== */
import documentosDemo from "./demo-documentos.json";

const CLAVE_TOKEN = "token";

export const MODO_DEMO = process.env.NEXT_PUBLIC_MODO_DEMO === "1";

/* Cuenta única del modo demostración (se muestra en la pantalla de login) */
export const CREDENCIALES_DEMO = { usuario: "tutor", clave: "unexpo2026" };
const USUARIO_DEMO = {
  id: 0,
  username: "tutor",
  nombres: "Tutor",
  apellidos: "Evaluador",
  email: "demo@repositorio.local",
  rol: "evaluador",
  estado: "activo",
  permisos: ["documento.descargar", "documento.ver"],
};

/* Pequeña espera para que la demo se sienta como una red real */
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

export class ErrorApi extends Error {
  constructor(mensaje, estado) {
    super(mensaje);
    this.estado = estado; // código HTTP (0 = sin conexión)
  }
}

/* ---------- Token de sesión (JWT) guardado en el navegador ---------- */
export function obtenerToken() {
  try {
    return localStorage.getItem(CLAVE_TOKEN);
  } catch {
    return null;
  }
}

export function cerrarSesionLocal() {
  try {
    localStorage.removeItem(CLAVE_TOKEN);
  } catch {}
}

/* ---------- Petición genérica con manejo de errores ---------- */
async function pedir(ruta, opciones = {}) {
  const token = obtenerToken();
  let respuesta;
  try {
    respuesta = await fetch(`/api${ruta}`, {
      ...opciones,
      headers: {
        ...(opciones.body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
  } catch {
    throw new ErrorApi("No se pudo conectar. Verifique su conexión a Internet o a Tailscale.", 0);
  }

  if (!respuesta.ok) {
    let detalle;
    try {
      detalle = (await respuesta.json()).detail;
    } catch {}
    if (Array.isArray(detalle)) detalle = detalle[0]?.msg; // errores de validación 422
    const mensaje =
      typeof detalle === "string"
        ? detalle
        : respuesta.status >= 500
          ? "El servidor del repositorio no responde. ¿Está encendido el backend?"
          : `Error inesperado (${respuesta.status})`;
    throw new ErrorApi(mensaje, respuesta.status);
  }
  return respuesta;
}

/* ---------- Autenticación ---------- */
export async function iniciarSesion(username, password) {
  if (MODO_DEMO) {
    await esperar(400);
    if (username.toLowerCase() !== CREDENCIALES_DEMO.usuario || password !== CREDENCIALES_DEMO.clave) {
      throw new ErrorApi("Usuario o contraseña incorrectos", 401);
    }
    localStorage.setItem(CLAVE_TOKEN, "demo");
    return USUARIO_DEMO;
  }
  const r = await pedir("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) });
  const datos = await r.json();
  localStorage.setItem(CLAVE_TOKEN, datos.access_token);
  return datos.usuario;
}

export async function obtenerUsuario() {
  if (MODO_DEMO) return USUARIO_DEMO;
  return (await pedir("/auth/yo")).json();
}

/* ---------- Documentos ---------- */
export async function listarDocumentos() {
  if (MODO_DEMO) {
    await esperar(300);
    return documentosDemo;
  }
  return (await pedir("/documentos")).json();
}

/** Descarga el PDF (con el token) y lo devuelve como Blob */
export async function obtenerPdf(id) {
  if (MODO_DEMO) {
    const doc = documentosDemo.find((d) => d.id === id);
    const r = doc && (await fetch(`/demo/${doc.nombre_archivo}`).catch(() => null));
    if (!r?.ok) throw new ErrorApi("No se encontró el PDF de demostración.", 404);
    return r.blob();
  }
  return (await pedir(`/documentos/${id}/descargar`)).blob();
}
