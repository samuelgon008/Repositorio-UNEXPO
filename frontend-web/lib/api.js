/* ==========================================================================
   Cliente de la API del repositorio. Todas las rutas van a /api/... y
   next.config.mjs las reenvía al backend FastAPI.

   MODO DEMOSTRACIÓN (Vercel o NEXT_PUBLIC_MODO_DEMO=1): no hay backend;
   cada función delega en lib/demo-api.js, que simula la API en el navegador.
   ========================================================================== */
import * as demo from "./demo-api";
import { ErrorApi } from "./errores";

export { ErrorApi };
export const MODO_DEMO = process.env.NEXT_PUBLIC_MODO_DEMO === "1";
export const { CUENTAS_DEMO, CLAVE_DEMO, reiniciarDemo } = demo;

const CLAVE_TOKEN = "token";

/* ---------- Token de sesión guardado en el navegador ---------- */
export function obtenerToken() {
  try {
    return localStorage.getItem(CLAVE_TOKEN);
  } catch {
    return null;
  }
}

function guardarToken(token) {
  localStorage.setItem(CLAVE_TOKEN, token);
}

export function cerrarSesionLocal() {
  try {
    localStorage.removeItem(CLAVE_TOKEN);
  } catch {}
}

/* ---------- Petición genérica con manejo de errores ---------- */
async function pedir(ruta, { metodo = "GET", cuerpo } = {}) {
  const token = obtenerToken();
  let respuesta;
  try {
    respuesta = await fetch(`/api${ruta}`, {
      method: metodo,
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
      headers: {
        ...(cuerpo === undefined ? {} : { "Content-Type": "application/json" }),
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

const json = async (ruta, opciones) => (await pedir(ruta, opciones)).json();

/* ---------- Autenticación ---------- */
export async function iniciarSesion(username, password) {
  const datos = MODO_DEMO
    ? await demo.iniciarSesion(username, password)
    : await json("/auth/login", { metodo: "POST", cuerpo: { username, password } });
  guardarToken(datos.access_token);
  return datos.usuario;
}

export const obtenerUsuario = () => (MODO_DEMO ? demo.obtenerUsuario(obtenerToken()) : json("/auth/yo"));

/* ---------- Tesis ---------- */
export const listarDocumentos = () => (MODO_DEMO ? demo.listarDocumentos(obtenerToken()) : json("/documentos"));

/** PDF como Blob. modo "ver" = leer en línea; "descargar" = archivo (queda auditado) */
export async function obtenerPdf(id, modo = "descargar") {
  if (MODO_DEMO) return demo.obtenerPdf(obtenerToken(), id, modo);
  return (await pedir(`/documentos/${id}/${modo}`)).blob();
}

export const editarDocumento = (id, cambios) =>
  MODO_DEMO ? demo.editarDocumento(obtenerToken(), id, cambios) : json(`/documentos/${id}`, { metodo: "PATCH", cuerpo: cambios });

export const eliminarDocumento = (id) =>
  MODO_DEMO ? demo.eliminarDocumento(obtenerToken(), id) : json(`/documentos/${id}`, { metodo: "DELETE" });

/* ---------- Solicitudes de acceso ---------- */
export const crearSolicitud = (documentoId, motivo) =>
  MODO_DEMO
    ? demo.crearSolicitud(obtenerToken(), documentoId, motivo)
    : json("/solicitudes", { metodo: "POST", cuerpo: { documento_id: documentoId, motivo } });

export const misSolicitudes = () => (MODO_DEMO ? demo.misSolicitudes(obtenerToken()) : json("/solicitudes/mias"));

export const listarSolicitudes = () => (MODO_DEMO ? demo.listarSolicitudes(obtenerToken()) : json("/solicitudes"));

/** accion: "aprobar" | "rechazar" | "revocar" */
export const resolverSolicitud = (id, accion, nota) =>
  MODO_DEMO
    ? demo.resolverSolicitud(obtenerToken(), id, accion, nota)
    : json(`/solicitudes/${id}/${accion}`, { metodo: "POST", cuerpo: { nota: nota || null } });

/* ---------- Usuarios (administrador) ---------- */
export const listarUsuarios = () => (MODO_DEMO ? demo.listarUsuarios(obtenerToken()) : json("/usuarios"));

/** accion: "bloquear" | "desbloquear" */
export const cambiarEstadoUsuario = (id, accion) =>
  MODO_DEMO ? demo.cambiarEstadoUsuario(obtenerToken(), id, accion) : json(`/usuarios/${id}/${accion}`, { metodo: "POST" });

export const aprobarUsuario = (id, rol) =>
  MODO_DEMO ? demo.aprobarUsuario(obtenerToken(), id, rol) : json(`/usuarios/${id}/aprobar`, { metodo: "POST", cuerpo: { rol } });

export const cambiarRolUsuario = (id, rol) =>
  MODO_DEMO ? demo.cambiarRolUsuario(obtenerToken(), id, rol) : json(`/usuarios/${id}/rol`, { metodo: "PATCH", cuerpo: { rol } });

export const eliminarUsuario = (id) =>
  MODO_DEMO ? demo.eliminarUsuario(obtenerToken(), id) : json(`/usuarios/${id}`, { metodo: "DELETE" });
