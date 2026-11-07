"use client";

import { Search, X } from "lucide-react";

/**
 * Barra de búsqueda principal. Controlada: el texto vive en page.jsx.
 * Recibe `ref` (React 19 lo permite como prop normal) para que el menú
 * "Buscar" y el atajo de teclado "/" puedan darle el foco.
 */
export default function BarraBusqueda({ valor, onCambio, ref }) {
  return (
    <div className="group relative w-full">
      <Search
        size={20}
        className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400
                   transition-colors group-focus-within:text-primary-600 dark:group-focus-within:text-primary-400"
      />
      <input
        ref={ref}
        type="search"
        value={valor}
        onChange={(e) => onCambio(e.target.value)}
        placeholder="Buscar trabajos por título, autor o palabras clave..."
        aria-label="Buscar trabajos"
        className="h-12 w-full rounded-2xl border border-slate-200 bg-white pl-12 pr-12 text-sm
                   text-slate-800 shadow-md outline-none transition duration-300 ease-suave placeholder:text-slate-400
                   focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15
                   sm:h-14 sm:text-base
                   dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100 dark:shadow-none dark:placeholder:text-slate-500
                   [&::-webkit-search-cancel-button]:hidden"
      />

      {/* Botón para limpiar, o pista del atajo "/" cuando está vacío */}
      {valor ? (
        <button
          onClick={() => onCambio("")}
          aria-label="Limpiar búsqueda"
          className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-slate-400
                     hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-200"
        >
          <X size={18} />
        </button>
      ) : (
        <kbd
          className="pointer-events-none absolute right-4 top-1/2 hidden -translate-y-1/2 rounded-md border
                     border-slate-200 px-2 py-0.5 font-sans text-xs text-slate-400 sm:block dark:border-slate-700"
        >
          /
        </kbd>
      )}
    </div>
  );
}
