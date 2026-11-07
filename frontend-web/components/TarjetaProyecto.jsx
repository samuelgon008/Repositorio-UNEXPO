import { ArrowUpRight, CalendarDays, FileDown, LoaderCircle, Star, UserRound } from "lucide-react";

/* Color del distintivo según el tipo de documento */
const ESTILO_TIPO = {
  TEG: "bg-primary-50 text-primary-700 ring-primary-600/15 dark:bg-primary-500/15 dark:text-primary-300 dark:ring-primary-400/20",
  IEI: "bg-amber-50 text-amber-700 ring-amber-600/15 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-400/20",
};

const NOMBRE_TIPO = { TEG: "Trabajo de Grado", IEI: "Entrenamiento Industrial" };

/* Formato de fecha corto en español: "15 oct 2026" */
const formatoFecha = new Intl.DateTimeFormat("es-VE", { day: "numeric", month: "short", year: "numeric" });

/** Distintivo (badge) neutro */
function Badge({ children }) {
  return (
    <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
      {children}
    </span>
  );
}

/**
 * Tarjeta de un trabajo del repositorio.
 * `proyecto`: documento de GET /documentos ya adaptado en page.jsx.
 * `favorito` / `onAlternarFavorito`: estrella de "Mis Favoritos".
 * `onVer` abre el PDF en otra pestaña; `onDescargar` lo descarga.
 * `puedeDescargar`: el rol tiene el permiso documento.descargar.
 */
export default function TarjetaProyecto({
  proyecto, favorito = false, onAlternarFavorito, onVer, onDescargar, puedeDescargar = true, descargando = false,
}) {
  const { titulo, autores, tipo, anio, carrera, area, resumen, fecha } = proyecto;

  return (
    <article
      /* Profundidad: sombra media en modo claro; al pasar el cursor la tarjeta
         sube 4 px y la sombra se agranda y difumina (efecto "flotar").
         En modo oscuro no hay sombra en reposo (dark:shadow-none). */
      className="group flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-md
                 transition duration-300 ease-suave
                 hover:-translate-y-1 hover:border-primary-300 hover:shadow-xl
                 dark:border-slate-800 dark:bg-slate-900 dark:shadow-none
                 dark:hover:border-primary-500/40 dark:hover:shadow-xl dark:hover:shadow-black/30"
    >
      {/* Tipo de documento y fecha de publicación */}
      <div className="mb-3 flex items-center justify-between gap-2">
        <span className={`whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${ESTILO_TIPO[tipo]}`}>
          {NOMBRE_TIPO[tipo]}
        </span>
        <span className="flex shrink-0 items-center gap-1 text-xs text-slate-400">
          <CalendarDays size={13} />
          <time dateTime={fecha}>{formatoFecha.format(new Date(`${fecha}T12:00:00`))}</time>
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

      {/* Resumen: máximo 3 líneas, el resto se trunca con "…" */}
      <p className="mt-3 line-clamp-3 text-sm leading-relaxed text-slate-600 dark:text-slate-400">{resumen}</p>

      {/* Etiquetas */}
      <div className="mt-4 flex flex-wrap gap-1.5">
        <Badge>{carrera}</Badge>
        <Badge>{area}</Badge>
        <Badge>{anio}</Badge>
      </div>

      {/* Acciones: mt-auto las alinea al fondo aunque las tarjetas tengan distinta altura */}
      <div className="mt-auto pt-5">
        <div className="flex items-center justify-between gap-2 border-t border-slate-100 pt-4 dark:border-slate-800">
          {/* Abre el PDF en una pestaña nueva (o la ficha, si el rol no puede descargar) */}
          <button
            onClick={onVer}
            className="inline-flex items-center gap-1 text-sm font-semibold text-primary-600 transition-colors
                       hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
          >
            Ver detalles
            <ArrowUpRight size={16} className="transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
          </button>

          <div className="flex items-center gap-1">
            {/* Estrella de favorito: rellena y ámbar cuando está marcada */}
            <button
              onClick={onAlternarFavorito}
              aria-pressed={favorito}
              aria-label={favorito ? "Quitar de Mis Favoritos" : "Agregar a Mis Favoritos"}
              title={favorito ? "Quitar de Mis Favoritos" : "Agregar a Mis Favoritos"}
              className={`rounded-lg p-1.5 transition-colors ${
                favorito
                  ? "text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-500/10"
                  : "text-slate-400 hover:bg-slate-100 hover:text-amber-400 dark:text-slate-500 dark:hover:bg-slate-800"
              }`}
            >
              <Star size={18} fill={favorito ? "currentColor" : "none"} />
            </button>

            {/* Descarga: GET /documentos/{id}/descargar (sólo roles con permiso) */}
            {puedeDescargar && (
              <button
                onClick={onDescargar}
                disabled={descargando}
                aria-label={`Descargar PDF de «${titulo}»`}
                className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm font-medium text-slate-500
                           transition-colors hover:bg-slate-100 hover:text-slate-800 disabled:cursor-wait
                           dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
              >
                {descargando ? <LoaderCircle size={16} className="animate-spin" /> : <FileDown size={16} />}
                PDF
              </button>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}
