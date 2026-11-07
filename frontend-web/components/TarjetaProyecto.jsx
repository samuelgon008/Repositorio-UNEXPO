import {
  BookOpen, CalendarDays, Clock, Eye, EyeOff, FileDown, KeyRound, LoaderCircle, Star, Trash2, UserRound,
} from "lucide-react";

import { Chip, formatoFecha } from "@/components/ui";

const NOMBRE_TIPO = { TEG: "Trabajo de Grado", IEI: "Entrenamiento Industrial" };
const TONO_TIPO = { TEG: "violeta", IEI: "ambar" };

/** Distintivo (badge) neutro */
function Badge({ children }) {
  return (
    <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
      {children}
    </span>
  );
}

/** Botón de icono pequeño del pie de la tarjeta */
function BotonIcono({ etiqueta, className = "", children, ...props }) {
  return (
    <button
      {...props}
      aria-label={etiqueta}
      title={etiqueta}
      className={`rounded-lg p-1.5 transition-colors disabled:cursor-wait ${className}`}
    >
      {children}
    </button>
  );
}

/** Línea informativa sobre la solicitud del estudiante (aprobada, rechazada…) */
function EstadoAcceso({ solicitud, puedeLeer }) {
  if (!solicitud) return null;
  const { estado, vence_en, nota_admin } = solicitud;
  if (estado === "aprobada" && puedeLeer) {
    return <p className="mt-3 text-xs font-medium text-emerald-600 dark:text-emerald-400">Acceso aprobado hasta el {formatoFecha(vence_en)}</p>;
  }
  const textos = { rechazada: "Solicitud rechazada", revocada: "Acceso revocado", vencida: "Su acceso venció" };
  if (!textos[estado]) return null;
  return (
    <p className={`mt-3 text-xs ${estado === "rechazada" ? "text-rose-600 dark:text-rose-400" : "text-slate-500 dark:text-slate-400"}`}>
      {textos[estado]}
      {nota_admin && <span className="text-slate-500 dark:text-slate-400"> · «{nota_admin}»</span>}
    </p>
  );
}

/**
 * Tarjeta de una tesis. Lo que muestra depende de lo que el usuario puede
 * hacer con ELLA (calculado por el backend en puede_leer / puede_descargar):
 *   - Leer / PDF            si tiene acceso
 *   - Solicitar acceso      estudiante sin acceso (o "Solicitud pendiente")
 *   - Ocultar / Eliminar    administrador
 */
export default function TarjetaProyecto({
  proyecto, favorito = false, onAlternarFavorito,
  onLeer, onDescargar, onSolicitar, onAlternarPublicado, onEliminar,
  puedeSolicitar = false, puedeAdministrar = false, cargando = null,
}) {
  const {
    titulo, autores, tipo, anio, carrera, area, resumen, fecha,
    publicado, puede_leer, puede_descargar, solicitud,
  } = proyecto;
  const pendiente = solicitud?.estado === "pendiente";

  return (
    /* Profundidad: sombra media en modo claro; al pasar el cursor la tarjeta
       sube 4 px y la sombra se agranda y difumina (efecto "flotar").
       En modo oscuro no hay sombra en reposo (dark:shadow-none). */
    <article
      className={`group flex flex-col rounded-2xl border bg-white p-5 shadow-md
                  transition duration-300 ease-suave hover:-translate-y-1 hover:shadow-xl
                  dark:bg-slate-900 dark:shadow-none dark:hover:shadow-xl dark:hover:shadow-black/30
                  ${publicado
                    ? "border-slate-200 hover:border-primary-300 dark:border-slate-800 dark:hover:border-primary-500/40"
                    : "border-dashed border-slate-300 opacity-80 dark:border-slate-700"}`}
    >
      {/* Tipo de documento, estado y fecha */}
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <Chip tono={TONO_TIPO[tipo]}>{NOMBRE_TIPO[tipo]}</Chip>
          {!publicado && <Chip tono="gris" Icono={EyeOff}>Oculta</Chip>}
        </div>
        <span className="flex shrink-0 items-center gap-1 text-xs text-slate-400">
          <CalendarDays size={13} />
          <time dateTime={fecha}>{formatoFecha(fecha)}</time>
        </span>
      </div>

      {/* Título: máximo 2 líneas */}
      <h3 className="line-clamp-2 text-base font-semibold leading-snug text-slate-900 transition-colors group-hover:text-primary-700 dark:text-white dark:group-hover:text-primary-300">
        {titulo}
      </h3>

      {/* Autor(es) */}
      <p className="mt-2 flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400">
        <UserRound size={15} className="shrink-0" />
        <span className="truncate">{autores.join(", ")}</span>
      </p>

      {/* Resumen: la "descripción" que todos los roles pueden ver (máximo 3 líneas) */}
      <p className="mt-3 line-clamp-3 text-sm leading-relaxed text-slate-600 dark:text-slate-400">{resumen}</p>

      {/* Etiquetas */}
      <div className="mt-4 flex flex-wrap gap-1.5">
        <Badge>{carrera}</Badge>
        <Badge>{area}</Badge>
        <Badge>{anio}</Badge>
      </div>

      <EstadoAcceso solicitud={solicitud} puedeLeer={puede_leer} />

      {/* Acciones: mt-auto las alinea al fondo aunque las tarjetas tengan distinta altura */}
      <div className="mt-auto pt-5">
        <div className="flex items-center justify-between gap-2 border-t border-slate-100 pt-4 dark:border-slate-800">
          {/* Acción principal según el acceso */}
          {puede_leer ? (
            <button
              onClick={onLeer}
              disabled={cargando === "ver"}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary-600 transition-colors
                         hover:text-primary-700 disabled:cursor-wait dark:text-primary-400 dark:hover:text-primary-300"
            >
              {cargando === "ver" ? <LoaderCircle size={16} className="animate-spin" /> : <BookOpen size={16} />}
              Leer tesis
            </button>
          ) : pendiente ? (
            <Chip tono="ambar" Icono={Clock}>Solicitud pendiente</Chip>
          ) : puedeSolicitar ? (
            <button
              onClick={onSolicitar}
              className="inline-flex items-center gap-1.5 rounded-lg bg-primary-50 px-3 py-1.5 text-sm font-semibold
                         text-primary-700 transition-colors hover:bg-primary-100
                         dark:bg-primary-500/15 dark:text-primary-300 dark:hover:bg-primary-500/25"
            >
              <KeyRound size={15} />
              {solicitud ? "Solicitar de nuevo" : "Solicitar acceso"}
            </button>
          ) : (
            <span className="text-xs text-slate-400">Solo ficha</span>
          )}

          <div className="flex items-center gap-0.5">
            {/* Estrella de favorito: rellena y ámbar cuando está marcada */}
            <BotonIcono
              etiqueta={favorito ? "Quitar de Mis Favoritos" : "Agregar a Mis Favoritos"}
              onClick={onAlternarFavorito}
              aria-pressed={favorito}
              className={favorito
                ? "text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-500/10"
                : "text-slate-400 hover:bg-slate-100 hover:text-amber-400 dark:text-slate-500 dark:hover:bg-slate-800"}
            >
              <Star size={18} fill={favorito ? "currentColor" : "none"} />
            </BotonIcono>

            {/* Herramientas del administrador */}
            {puedeAdministrar && (
              <>
                <BotonIcono
                  etiqueta={publicado ? "Ocultar tesis" : "Publicar tesis"}
                  onClick={onAlternarPublicado}
                  className="text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-500 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                >
                  {publicado ? <EyeOff size={18} /> : <Eye size={18} />}
                </BotonIcono>
                <BotonIcono
                  etiqueta={`Eliminar «${titulo}»`}
                  onClick={onEliminar}
                  className="text-slate-400 hover:bg-rose-50 hover:text-rose-600 dark:text-slate-500 dark:hover:bg-rose-500/10 dark:hover:text-rose-400"
                >
                  <Trash2 size={18} />
                </BotonIcono>
              </>
            )}

            {/* Descarga: sólo si este usuario puede descargar esta tesis */}
            {puede_descargar && (
              <button
                onClick={onDescargar}
                disabled={cargando === "descargar"}
                aria-label={`Descargar PDF de «${titulo}»`}
                className="ml-0.5 inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm font-medium text-slate-500
                           transition-colors hover:bg-slate-100 hover:text-slate-800 disabled:cursor-wait
                           dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
              >
                {cargando === "descargar" ? <LoaderCircle size={16} className="animate-spin" /> : <FileDown size={16} />}
                PDF
              </button>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}
