/* ==========================================================================
   API SIMULADA del modo demostración (Vercel). Reproduce en el navegador las
   reglas del backend (backend/app/services/acceso.py, routes/*.py):
   - 3 cuentas: admin, docente y estudiante (misma contraseña).
   - El estudiante solicita acceso por tesis; el admin aprueba (30 días),
     rechaza o revoca. El docente lee en línea sin descargar.
   El estado (usuarios, solicitudes, cambios) vive en localStorage de cada
   navegador: así se puede probar el flujo completo cambiando de cuenta.
   ========================================================================== */
import documentosBase from "./demo-documentos.json";
import { ErrorApi } from "./errores";

export const CLAVE_DEMO = "unexpo2026";
export const CUENTAS_DEMO = [
  { usuario: "admin", rol: "Administrador" },
  { usuario: "docente", rol: "Docente" },
  { usuario: "estudiante", rol: "Estudiante" },
];

/* Igual que backend/app/core/catalogos.py */
const PERMISOS_POR_ROL = {
  administrador: [
    "auditoria.ver", "documento.descargar", "documento.editar", "documento.eliminar", "documento.leer",
    "documento.ver", "solicitud.gestionar", "usuario.gestionar",
  ],
  docente: ["documento.leer", "documento.ver"],
  estudiante: ["documento.ver", "solicitud.crear"],
};
const DIAS_ACCESO = 30;
const CLAVE_ESTADO = "demo-estado-v1";

const hace = (dias) => new Date(Date.now() - dias * 86_400_000).toISOString();

function estadoInicial() {
  const u = (id, username, nombres, apellidos, rol, estado = "activo") => ({
    id, username, nombres, apellidos, rol, estado, cedula: `V-${10_000_000 + id}`,
    email: `${username}@demo.unexpo`, creado_en: hace(40 - id), ultimo_acceso: null,
  });
  return {
    sigId: 100,
    usuarios: [
      u(1, "admin", "Andrea", "Rodríguez", "administrador"),
      u(2, "docente", "Carlos", "Pérez", "docente"),
      u(3, "estudiante", "María", "Rojas", "estudiante"),
      u(4, "daniela.ruiz", "Daniela", "Ruiz", "estudiante"),
      u(5, "luis.mendez", "Luis", "Méndez", "estudiante", "pendiente"),
    ],
    // Una solicitud de otra estudiante, para que el admin tenga algo que revisar
    solicitudes: [
      {
        id: 1, usuario_id: 4, documento_id: 2, motivo: "La necesito como antecedente para mi TEG sobre IoT.",
        estado: "pendiente", nota_admin: null, creada_en: hace(1), resuelta_en: null, vence_en: null,
      },
    ],
    documentos: {}, // cambios del admin por id: { titulo?, publicado?, eliminado? }
    descargas: [],  // ids de usuario que han descargado (protege su eliminación)
  };
}

/* ---------- Estado persistente en el navegador ---------- */
function leer() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_ESTADO)) ?? estadoInicial();
  } catch {
    return estadoInicial();
  }
}

function guardar(estado) {
  try {
    localStorage.setItem(CLAVE_ESTADO, JSON.stringify(estado));
  } catch {}
}

/** Vuelve la demo a su estado original (botón en la pantalla de login) */
export function reiniciarDemo() {
  try {
    localStorage.removeItem(CLAVE_ESTADO);
  } catch {}
}

const esperar = (ms = 250) => new Promise((r) => setTimeout(r, ms));
const ahora = () => new Date().toISOString();

/* ---------- Sesión y permisos ---------- */
function sesion(estado, token) {
  const id = Number(String(token ?? "").replace("demo:", ""));
  const u = estado.usuarios.find((x) => x.id === id);
  if (!u || u.estado !== "activo") throw new ErrorApi("Sesión inválida o expirada", 401);
  return u;
}

const permisos = (u) => PERMISOS_POR_ROL[u.rol];

function requiere(u, permiso) {
  if (!permisos(u).includes(permiso)) throw new ErrorApi("No tiene permiso para esta acción", 403);
}

const usuarioOut = (u) => ({
  id: u.id, username: u.username, nombres: u.nombres, apellidos: u.apellidos,
  email: u.email, rol: u.rol, estado: u.estado, permisos: permisos(u),
});

/* ---------- Reglas de acceso (= services/acceso.py) ---------- */
const vigente = (s) => s.estado === "aprobada" && new Date(s.vence_en) > new Date();
const estadoVisible = (s) => (s.estado === "aprobada" && !vigente(s) ? "vencida" : s.estado);

function ultimaSolicitud(estado, usuarioId, documentoId) {
  return estado.solicitudes
    .filter((s) => s.usuario_id === usuarioId && s.documento_id === documentoId)
    .sort((a, b) => b.creada_en.localeCompare(a.creada_en) || b.id - a.id)[0];
}

function acceso(u, solicitud) {
  const p = permisos(u);
  if (p.includes("documento.descargar")) return { leer: true, descargar: true };
  if (p.includes("documento.leer")) return { leer: true, descargar: false };
  if (solicitud && vigente(solicitud)) return { leer: true, descargar: true };
  return { leer: false, descargar: false };
}

/* Tesis con los cambios del admin aplicados; las ocultas sólo para quien edita */
function documentos(estado, u) {
  const veOcultos = permisos(u).includes("documento.editar");
  return documentosBase
    .map((d) => ({ ...d, publicado: true, ...estado.documentos[d.id] }))
    .filter((d) => !d.eliminado && (d.publicado || veOcultos));
}

function buscarDocumento(estado, u, id) {
  const d = documentos(estado, u).find((x) => x.id === id);
  if (!d) throw new ErrorApi("Tesis no encontrada", 404);
  return d;
}

const solicitudBreve = (s) => ({
  id: s.id, estado: estadoVisible(s), creada_en: s.creada_en, vence_en: s.vence_en, nota_admin: s.nota_admin,
});

function solicitudOut(estado, s) {
  const u = estado.usuarios.find((x) => x.id === s.usuario_id);
  const d = documentosBase.find((x) => x.id === s.documento_id);
  return {
    ...solicitudBreve(s), motivo: s.motivo, resuelta_en: s.resuelta_en,
    documento_id: s.documento_id, documento_titulo: estado.documentos[d.id]?.titulo ?? d.titulo,
    usuario_id: u.id, usuario_nombre: `${u.nombres} ${u.apellidos}`,
    usuario_username: u.username, usuario_cedula: u.cedula,
  };
}

/* =============================== API =============================== */

export async function iniciarSesion(username, password) {
  await esperar(400);
  const estado = leer();
  const u = estado.usuarios.find((x) => x.username === username.trim().toLowerCase());
  if (!u || password !== CLAVE_DEMO) throw new ErrorApi("Usuario o contraseña incorrectos", 401);
  if (u.estado === "pendiente") throw new ErrorApi("Su cuenta está pendiente de aprobación por un administrador.", 403);
  if (u.estado === "suspendido") throw new ErrorApi("Su cuenta está suspendida. Contacte al departamento.", 403);
  u.ultimo_acceso = ahora();
  guardar(estado);
  return { access_token: `demo:${u.id}`, usuario: usuarioOut(u) };
}

export async function obtenerUsuario(token) {
  return usuarioOut(sesion(leer(), token));
}

/* ---------- Tesis ---------- */
export async function listarDocumentos(token) {
  await esperar(300);
  const estado = leer();
  const u = sesion(estado, token);
  return documentos(estado, u).map((d) => {
    const s = permisos(u).includes("solicitud.crear") ? ultimaSolicitud(estado, u.id, d.id) : undefined;
    const a = acceso(u, s);
    return { ...d, puede_leer: a.leer, puede_descargar: a.descargar, solicitud: s ? solicitudBreve(s) : null };
  });
}

export async function obtenerPdf(token, id, modo) {
  const estado = leer();
  const u = sesion(estado, token);
  const d = buscarDocumento(estado, u, id);
  const a = acceso(u, ultimaSolicitud(estado, u.id, id));
  if (!(modo === "ver" ? a.leer : a.descargar)) {
    throw new ErrorApi(
      permisos(u).includes("solicitud.crear")
        ? "Necesita una solicitud de acceso aprobada para esta tesis"
        : "Su rol no permite descargar las tesis",
      403,
    );
  }
  const r = await fetch(`/demo/${d.nombre_archivo}`).catch(() => null);
  if (!r?.ok) throw new ErrorApi("No se encontró el PDF de demostración.", 404);
  if (modo === "descargar") {
    estado.descargas.push(u.id);
    guardar(estado);
  }
  return r.blob();
}

export async function editarDocumento(token, id, cambios) {
  const estado = leer();
  const u = sesion(estado, token);
  requiere(u, "documento.editar");
  buscarDocumento(estado, u, id);
  estado.documentos[id] = { ...estado.documentos[id], ...cambios };
  guardar(estado);
  return buscarDocumento(estado, u, id);
}

export async function eliminarDocumento(token, id) {
  const estado = leer();
  const u = sesion(estado, token);
  requiere(u, "documento.eliminar");
  const d = buscarDocumento(estado, u, id);
  estado.documentos[id] = { ...estado.documentos[id], eliminado: true };
  estado.solicitudes = estado.solicitudes.filter((s) => s.documento_id !== id);
  guardar(estado);
  return { detail: `Tesis eliminada: «${d.titulo}»` };
}

/* ---------- Solicitudes ---------- */
export async function crearSolicitud(token, documentoId, motivo) {
  await esperar();
  const estado = leer();
  const u = sesion(estado, token);
  requiere(u, "solicitud.crear");
  const d = buscarDocumento(estado, u, documentoId);
  if (!d.publicado) throw new ErrorApi("Tesis no encontrada", 404);
  for (const s of estado.solicitudes.filter((x) => x.usuario_id === u.id && x.documento_id === documentoId)) {
    if (s.estado === "pendiente") throw new ErrorApi("Ya tiene una solicitud pendiente para esta tesis", 409);
    if (vigente(s)) throw new ErrorApi("Ya tiene acceso a esta tesis", 409);
  }
  const s = {
    id: estado.sigId++, usuario_id: u.id, documento_id: documentoId, motivo: motivo?.trim() || null,
    estado: "pendiente", nota_admin: null, creada_en: ahora(), resuelta_en: null, vence_en: null,
  };
  estado.solicitudes.push(s);
  guardar(estado);
  return solicitudOut(estado, s);
}

export async function misSolicitudes(token) {
  await esperar();
  const estado = leer();
  const u = sesion(estado, token);
  requiere(u, "solicitud.crear");
  return estado.solicitudes
    .filter((s) => s.usuario_id === u.id)
    .sort((a, b) => b.creada_en.localeCompare(a.creada_en))
    .map((s) => solicitudOut(estado, s));
}

export async function listarSolicitudes(token) {
  await esperar();
  const estado = leer();
  requiere(sesion(estado, token), "solicitud.gestionar");
  return [...estado.solicitudes]
    .sort((a, b) => (a.estado !== "pendiente") - (b.estado !== "pendiente") || b.creada_en.localeCompare(a.creada_en))
    .map((s) => solicitudOut(estado, s));
}

const TRANSICIONES = {
  aprobar: ["pendiente", "aprobada"],
  rechazar: ["pendiente", "rechazada"],
  revocar: ["aprobada", "revocada"],
};

export async function resolverSolicitud(token, id, accion, nota) {
  await esperar();
  const estado = leer();
  requiere(sesion(estado, token), "solicitud.gestionar");
  const s = estado.solicitudes.find((x) => x.id === id);
  if (!s) throw new ErrorApi("Solicitud no encontrada", 404);
  const [desde, hacia] = TRANSICIONES[accion];
  if (s.estado !== desde) throw new ErrorApi(`La solicitud está ${estadoVisible(s)}; no se puede cambiar así`, 409);
  s.estado = hacia;
  s.resuelta_en = ahora();
  s.nota_admin = nota?.trim() || null;
  if (hacia === "aprobada") s.vence_en = new Date(Date.now() + DIAS_ACCESO * 86_400_000).toISOString();
  guardar(estado);
  return solicitudOut(estado, s);
}

/* ---------- Usuarios ---------- */
const usuarioAdminOut = ({ id, username, nombres, apellidos, cedula, email, rol, estado, creado_en, ultimo_acceso }) =>
  ({ id, username, nombres, apellidos, cedula, email, rol, estado, creado_en, ultimo_acceso });

function otroUsuario(estado, token, id) {
  const admin = sesion(estado, token);
  requiere(admin, "usuario.gestionar");
  if (admin.id === id) throw new ErrorApi("No puede aplicarse esta acción a su propia cuenta", 400);
  const u = estado.usuarios.find((x) => x.id === id);
  if (!u) throw new ErrorApi("Usuario no encontrado", 404);
  return u;
}

export async function listarUsuarios(token) {
  await esperar();
  const estado = leer();
  requiere(sesion(estado, token), "usuario.gestionar");
  return [...estado.usuarios]
    .sort((a, b) => (a.estado !== "pendiente") - (b.estado !== "pendiente") || a.apellidos.localeCompare(b.apellidos))
    .map(usuarioAdminOut);
}

export async function cambiarEstadoUsuario(token, id, accion) {
  const estado = leer();
  const u = otroUsuario(estado, token, id);
  if (accion === "desbloquear" && u.estado !== "suspendido") throw new ErrorApi("La cuenta no está bloqueada", 409);
  u.estado = accion === "bloquear" ? "suspendido" : "activo";
  guardar(estado);
  return usuarioAdminOut(u);
}

export async function aprobarUsuario(token, id, rol) {
  const estado = leer();
  const u = otroUsuario(estado, token, id);
  if (u.estado !== "pendiente") throw new ErrorApi("La cuenta no está pendiente de aprobación", 409);
  Object.assign(u, { estado: "activo", rol });
  guardar(estado);
  return usuarioAdminOut(u);
}

export async function cambiarRolUsuario(token, id, rol) {
  const estado = leer();
  const u = otroUsuario(estado, token, id);
  u.rol = rol;
  guardar(estado);
  return usuarioAdminOut(u);
}

export async function eliminarUsuario(token, id) {
  const estado = leer();
  const u = otroUsuario(estado, token, id);
  if (estado.descargas.includes(u.id)) {
    throw new ErrorApi("Este usuario tiene historial de descargas o tesis cargadas; bloquéelo en lugar de eliminarlo", 409);
  }
  estado.usuarios = estado.usuarios.filter((x) => x.id !== id);
  estado.solicitudes = estado.solicitudes.filter((s) => s.usuario_id !== id);
  guardar(estado);
  return { detail: `Usuario «${u.username}» eliminado` };
}
