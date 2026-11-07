"use client";

/* ==========================================================================
   Piezas visuales compartidas: etiquetas de estado, modal, encabezados y
   estados vacíos. Mantienen el mismo estilo en todas las vistas.
   ========================================================================== */
import { useEffect } from "react";
import { X } from "lucide-react";

/* Une clases condicionales: cx("a", falso && "b", "c") → "a c" */
export const cx = (...clases) => clases.filter(Boolean).join(" ");

/* Fecha corta en español: "15 oct. 2026" */
const formato = new Intl.DateTimeFormat("es-VE", { day: "numeric", month: "short", year: "numeric" });
export const formatoFecha = (iso) => (iso ? formato.format(new Date(iso.length === 10 ? `${iso}T12:00:00` : iso)) : "—");

/* ---------- Etiqueta de color ---------- */
const TONOS = {
  gris: "bg-slate-100 text-slate-600 ring-slate-500/15 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-400/20",
  violeta: "bg-primary-50 text-primary-700 ring-primary-600/15 dark:bg-primary-500/15 dark:text-primary-300 dark:ring-primary-400/20",
  verde: "bg-emerald-50 text-emerald-700 ring-emerald-600/15 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-400/20",
  ambar: "bg-amber-50 text-amber-700 ring-amber-600/15 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-400/20",
  rojo: "bg-rose-50 text-rose-700 ring-rose-600/15 dark:bg-rose-500/10 dark:text-rose-300 dark:ring-rose-400/20",
};

export function Chip({ tono = "gris", Icono, children, className }) {
  return (
    <span className={cx("inline-flex items-center gap-1 whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset", TONOS[tono], className)}>
      {Icono && <Icono size={12} />}
      {children}
    </span>
  );
}

export const ESTADO_SOLICITUD = {
  pendiente: { texto: "Pendiente", tono: "ambar" },
  aprobada: { texto: "Aprobada", tono: "verde" },
  rechazada: { texto: "Rechazada", tono: "rojo" },
  revocada: { texto: "Revocada", tono: "gris" },
  vencida: { texto: "Vencida", tono: "gris" },
};

export const ESTADO_USUARIO = {
  activo: { texto: "Activo", tono: "verde" },
  pendiente: { texto: "Por aprobar", tono: "ambar" },
  suspendido: { texto: "Bloqueado", tono: "rojo" },
};

export const NOMBRE_ROL = { administrador: "Administrador", docente: "Docente", estudiante: "Estudiante" };

/* ---------- Encabezado de cada vista ---------- */
export function Encabezado({ titulo, subtitulo, children }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl dark:text-white">{titulo}</h2>
        {subtitulo && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{subtitulo}</p>}
      </div>
      {children}
    </div>
  );
}

/* ---------- Estado vacío ---------- */
export function Vacio({ Icono, titulo, texto, children }) {
  return (
    <div className="flex flex-col items-center rounded-2xl border border-dashed border-slate-300 px-6 py-14 text-center dark:border-slate-700">
      <Icono size={40} className="text-slate-400" />
      <p className="mt-4 font-semibold text-slate-700 dark:text-slate-200">{titulo}</p>
      {texto && <p className="mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">{texto}</p>}
      {children}
    </div>
  );
}

/* ---------- Pestañas de filtro (Pendientes / Aprobadas / Todas…) ---------- */
export function Pestanas({ opciones, valor, onCambio }) {
  return (
    <div className="inline-flex rounded-xl bg-slate-200/70 p-1 dark:bg-slate-800">
      {opciones.map(({ id, texto, contador }) => (
        <button
          key={id}
          onClick={() => onCambio(id)}
          className={cx(
            "rounded-lg px-3 py-1.5 text-sm font-medium transition duration-200 ease-suave",
            valor === id
              ? "bg-white text-slate-900 shadow-sm dark:bg-slate-700 dark:text-white"
              : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white",
          )}
        >
          {texto}
          {contador > 0 && <span className="ml-1.5 text-xs text-slate-400">{contador}</span>}
        </button>
      ))}
    </div>
  );
}

/* ---------- Botones ---------- */
const VARIANTES = {
  primario: "bg-primary-600 text-white shadow-sm hover:bg-primary-700",
  exito: "bg-emerald-600 text-white shadow-sm hover:bg-emerald-700",
  peligro: "bg-rose-600 text-white shadow-sm hover:bg-rose-700",
  suave: "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700",
  fantasma: "text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100",
};

export function Boton({ variante = "primario", Icono, children, className, ...props }) {
  return (
    <button
      {...props}
      className={cx(
        "inline-flex items-center justify-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold",
        "transition duration-200 ease-suave disabled:cursor-not-allowed disabled:opacity-50",
        VARIANTES[variante], className,
      )}
    >
      {Icono && <Icono size={16} />}
      {children}
    </button>
  );
}

/* ---------- Ventana modal ---------- */
export function Modal({ titulo, onCerrar, children, acciones }) {
  // Esc cierra la ventana
  useEffect(() => {
    const alPresionar = (e) => e.key === "Escape" && onCerrar();
    window.addEventListener("keydown", alPresionar);
    return () => window.removeEventListener("keydown", alPresionar);
  }, [onCerrar]);

  return (
    <div className="fixed inset-0 z-50 grid place-items-center p-4" role="dialog" aria-modal="true" aria-label={titulo}>
      <div className="absolute inset-0 animate-aparecer bg-slate-950/50 backdrop-blur-sm" onClick={onCerrar} />
      <div className="relative w-full max-w-lg animate-aparecer rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-4 flex items-start justify-between gap-4">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{titulo}</h3>
          <button onClick={onCerrar} aria-label="Cerrar" className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800">
            <X size={20} />
          </button>
        </div>
        {children}
        {acciones && <div className="mt-6 flex justify-end gap-2">{acciones}</div>}
      </div>
    </div>
  );
}
