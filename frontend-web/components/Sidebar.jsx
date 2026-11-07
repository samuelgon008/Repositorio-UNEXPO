"use client";

import {
  Bell, FolderOpen, GraduationCap, LayoutDashboard, LogOut, Moon, PanelLeftClose,
  PanelLeftOpen, Star, Sun, X,
} from "lucide-react";

/* Opciones de navegación principal. `id` coincide con la vista que muestra
   page.jsx. (La búsqueda vive en la barra superior, no en el menú.) */
const OPCIONES = [
  { id: "principal", etiqueta: "Principal", Icono: LayoutDashboard },
  { id: "categorias", etiqueta: "Explorar Categorías", Icono: FolderOpen },
  { id: "favoritos", etiqueta: "Mis Favoritos", Icono: Star },
  { id: "notificaciones", etiqueta: "Notificaciones", Icono: Bell },
];

/* Une clases condicionales: cx("a", falso && "b", "c") → "a c" */
const cx = (...clases) => clases.filter(Boolean).join(" ");

/**
 * Texto de un elemento del menú. Al colapsar (sólo en escritorio) se
 * desvanece y su ancho máximo se anima a 0, lo que da la transición suave.
 */
function Etiqueta({ colapsado, children }) {
  return (
    <span
      className={cx(
        "overflow-hidden whitespace-nowrap transition-all duration-300 ease-in-out",
        colapsado ? "md:max-w-0 md:opacity-0" : "max-w-48 opacity-100",
      )}
    >
      {children}
    </span>
  );
}

/** Globo con el nombre de la opción; sólo aparece en hover con el menú colapsado. */
function Tooltip({ colapsado, children }) {
  if (!colapsado) return null;
  return (
    // aria-hidden: es sólo visual; el botón ya tiene su nombre accesible
    <span
      aria-hidden="true"
      className="pointer-events-none absolute left-full z-50 ml-3 hidden whitespace-nowrap rounded-md
                 bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-white opacity-0 shadow-lg
                 transition-opacity duration-150 group-hover:opacity-100 md:block
                 dark:bg-slate-700"
    >
      {children}
    </span>
  );
}

const NOMBRE_ROL = {
  administrador: "Administrador",
  bibliotecario: "Bibliotecario",
  estudiante: "Estudiante",
  invitado: "Invitado",
  evaluador: "Evaluador (demo)", // cuenta del modo demostración
};

/**
 * Bloque de perfil: avatar con iniciales, nombre corto y rol.
 * "Samuel David" + "González López" → "Samuel González", iniciales "SG".
 * Con el menú colapsado sólo queda el avatar (el nombre sale en el tooltip).
 */
function Perfil({ usuario, colapsado }) {
  if (!usuario) {
    // Esqueleto mientras se carga la sesión
    return (
      <div className="flex items-center gap-3 px-1.5 py-2" aria-hidden="true">
        <span className="size-8 shrink-0 animate-pulse rounded-full bg-slate-200 dark:bg-slate-700" />
        <span className={cx("h-3 w-28 animate-pulse rounded bg-slate-200 dark:bg-slate-700", colapsado && "md:hidden")} />
      </div>
    );
  }

  const nombre = `${usuario.nombres.split(" ")[0]} ${usuario.apellidos.split(" ")[0]}`;
  const iniciales = (usuario.nombres[0] + usuario.apellidos[0]).toUpperCase();
  const rol = NOMBRE_ROL[usuario.rol] ?? usuario.rol;

  return (
    <div className="group relative flex items-center gap-3 rounded-xl px-1.5 py-2" title={colapsado ? undefined : usuario.email}>
      <span
        aria-hidden="true"
        className="grid size-8 shrink-0 place-items-center rounded-full bg-linear-to-br from-primary-500 to-primary-700
                   text-xs font-bold text-white shadow-sm ring-2 ring-white dark:ring-slate-900"
      >
        {iniciales}
      </span>
      <Etiqueta colapsado={colapsado}>
        <span className="block truncate text-sm font-semibold leading-tight text-slate-900 dark:text-white">{nombre}</span>
        <span className="block text-xs text-slate-500 dark:text-slate-400">{rol}</span>
      </Etiqueta>
      <Tooltip colapsado={colapsado}>
        {nombre} · {rol}
      </Tooltip>
    </div>
  );
}

export default function Sidebar({
  usuario,          // { nombres, apellidos, rol, email } de GET /auth/yo (null mientras carga)
  colapsado,        // true = sólo iconos (escritorio)
  onAlternarColapso,
  abiertoMovil,     // true = cajón visible en pantallas pequeñas
  onCerrarMovil,
  vistaActiva,
  onNavegar,
  oscuro,
  onAlternarTema,
  onCerrarSesion,
  pendientes = 0,   // notificaciones sin leer
}) {
  return (
    <>
      {/* ---------- Fondo oscuro detrás del cajón (sólo móvil) ---------- */}
      <div
        onClick={onCerrarMovil}
        aria-hidden="true"
        className={cx(
          "fixed inset-0 z-30 bg-slate-950/50 backdrop-blur-sm transition-opacity duration-300 md:hidden",
          abiertoMovil ? "opacity-100" : "pointer-events-none opacity-0",
        )}
      />

      {/* ---------- Panel lateral ----------
          Móvil: cajón fijo que entra desde la izquierda (translate-x).
          Escritorio: columna fija cuyo ANCHO se anima entre w-64 y w-20. */}
      <aside
        className={cx(
          "fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r",
          "border-slate-200 bg-white shadow-md dark:border-slate-800 dark:bg-slate-900 dark:shadow-none",
          "transition-[width,translate] duration-300 ease-in-out",
          "md:sticky md:top-0 md:h-screen md:translate-x-0",
          abiertoMovil ? "translate-x-0" : "-translate-x-full",
          colapsado ? "md:w-20" : "md:w-64",
        )}
      >
        {/* Encabezado: logo + botón de colapsar */}
        <div className="flex h-16 shrink-0 items-center gap-3 border-b border-slate-200 px-5 dark:border-slate-800">
          <div className="grid size-10 shrink-0 place-items-center rounded-xl bg-primary-600 text-white shadow-md shadow-primary-600/30">
            <GraduationCap size={22} />
          </div>
          <Etiqueta colapsado={colapsado}>
            <span className="block text-sm font-bold leading-tight text-slate-900 dark:text-white">
              Repositorio Digital
            </span>
            <span className="block text-xs text-slate-500 dark:text-slate-400">Ing. Electrónica · UNEXPO</span>
          </Etiqueta>

          {/* Cerrar cajón (móvil) */}
          <button
            onClick={onCerrarMovil}
            aria-label="Cerrar menú"
            className="ml-auto rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 md:hidden dark:hover:bg-slate-800"
          >
            <X size={20} />
          </button>
        </div>

        {/* Botón colapsar/expandir (escritorio): pestaña sobre el borde */}
        <button
          onClick={onAlternarColapso}
          aria-label={colapsado ? "Expandir menú" : "Colapsar menú"}
          aria-expanded={!colapsado}
          className="absolute -right-3.5 top-20 z-50 hidden size-7 place-items-center rounded-full border
                     border-slate-200 bg-white text-slate-500 shadow-sm transition-colors
                     hover:border-primary-400 hover:text-primary-600 md:grid
                     dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400 dark:hover:text-primary-300"
        >
          {colapsado ? <PanelLeftOpen size={15} /> : <PanelLeftClose size={15} />}
        </button>

        {/* ---------- Navegación ---------- */}
        {/* Sin overflow-auto a propósito: recortaría los tooltips del menú colapsado */}
        <nav className="flex-1 space-y-1 px-3 py-5">
          <p
            className={cx(
              "mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 transition-opacity duration-300",
              colapsado && "md:opacity-0",
            )}
          >
            Menú
          </p>

          {OPCIONES.map(({ id, etiqueta, Icono }) => {
            const activa = vistaActiva === id;
            return (
              <button
                key={id}
                onClick={() => onNavegar(id)}
                aria-current={activa ? "page" : undefined}
                className={cx(
                  "group relative flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium",
                  "transition-colors duration-200",
                  activa
                    ? "bg-primary-50 text-primary-700 dark:bg-primary-500/15 dark:text-primary-300"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-primary-300",
                )}
              >
                {/* Barra indicadora del elemento activo */}
                <span
                  className={cx(
                    "absolute -left-3 h-6 w-1 rounded-r-full bg-primary-600 transition-opacity dark:bg-primary-400",
                    activa ? "opacity-100" : "opacity-0",
                  )}
                />
                <span className="relative shrink-0">
                  <Icono size={20} />
                  {/* Contador rojo sobre el icono cuando el menú está colapsado */}
                  {id === "notificaciones" && pendientes > 0 && colapsado && (
                    <span className="absolute -right-2 -top-2 hidden h-4 min-w-4 place-items-center rounded-full bg-rose-500 px-1 text-[10px] font-bold leading-none text-white ring-2 ring-white md:grid dark:ring-slate-900">
                      {pendientes > 9 ? "9+" : pendientes}
                    </span>
                  )}
                </span>
                <Etiqueta colapsado={colapsado}>{etiqueta}</Etiqueta>
                {/* Contador de pendientes cuando el menú está expandido */}
                {id === "notificaciones" && pendientes > 0 && (
                  <span
                    className={cx(
                      "ml-auto rounded-full bg-rose-500 px-2 py-0.5 text-[11px] font-semibold text-white transition-opacity duration-300",
                      colapsado && "md:hidden",
                    )}
                  >
                    {pendientes}
                  </span>
                )}
                <Tooltip colapsado={colapsado}>{etiqueta}</Tooltip>
              </button>
            );
          })}
        </nav>

        {/* ---------- Parte inferior: tema y cerrar sesión ---------- */}
        <div className="space-y-1 border-t border-slate-200 p-3 dark:border-slate-800">
          {/* Interruptor Modo Claro / Modo Oscuro */}
          <button
            onClick={onAlternarTema}
            role="switch"
            aria-checked={oscuro}
            aria-label="Modo oscuro"
            className="group relative flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium
                       text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          >
            <span className="shrink-0">{oscuro ? <Moon size={20} /> : <Sun size={20} />}</span>
            <Etiqueta colapsado={colapsado}>{oscuro ? "Modo Oscuro" : "Modo Claro"}</Etiqueta>
            {/* Pista del interruptor; se oculta cuando el menú está colapsado */}
            <span
              className={cx(
                "relative ml-auto h-6 w-11 shrink-0 rounded-full transition-colors duration-300",
                oscuro ? "bg-primary-600" : "bg-slate-300",
                colapsado && "md:hidden",
              )}
            >
              <span
                className={cx(
                  "absolute left-0.5 top-0.5 size-5 rounded-full bg-white shadow transition-transform duration-300",
                  oscuro && "translate-x-5",
                )}
              />
            </span>
            <Tooltip colapsado={colapsado}>{oscuro ? "Cambiar a modo claro" : "Cambiar a modo oscuro"}</Tooltip>
          </button>

          {/* Perfil del usuario, justo encima de "Cerrar Sesión" */}
          <div className="mt-2! border-t border-slate-200 pt-2 dark:border-slate-800">
            <Perfil usuario={usuario} colapsado={colapsado} />
          </div>

          {/* Cerrar sesión */}
          <button
            onClick={onCerrarSesion}
            className="group relative flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium
                       text-slate-600 transition-colors hover:bg-rose-50 hover:text-rose-600
                       dark:text-slate-400 dark:hover:bg-rose-500/10 dark:hover:text-rose-400"
          >
            <LogOut size={20} className="shrink-0" />
            <Etiqueta colapsado={colapsado}>Cerrar Sesión</Etiqueta>
            <Tooltip colapsado={colapsado}>Cerrar Sesión</Tooltip>
          </button>
        </div>
      </aside>
    </>
  );
}
