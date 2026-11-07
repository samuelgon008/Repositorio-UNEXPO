"use client";

import { useState } from "react";
import { Ban, Check, LoaderCircle, Search, ShieldCheck, Trash2, Users } from "lucide-react";

import { Boton, Chip, Encabezado, ESTADO_USUARIO, formatoFecha, NOMBRE_ROL, Pestanas, Vacio } from "@/components/ui";

const ROLES = ["estudiante", "docente", "administrador"];

const normalizar = (t) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

/**
 * Panel del ADMINISTRADOR: aprobar registros, bloquear/desbloquear, cambiar
 * el rol y eliminar cuentas. Su propia cuenta aparece sin acciones.
 */
export default function VistaUsuarios({ usuarios, yo, onAccion }) {
  const [filtro, setFiltro] = useState("todos");
  const [texto, setTexto] = useState("");
  const [ocupado, setOcupado] = useState(null);
  const [rolAprobar, setRolAprobar] = useState({}); // rol elegido para cada cuenta por aprobar

  if (usuarios === null) return <p className="text-sm text-slate-500">Cargando usuarios…</p>;

  const cuenta = (estado) => usuarios.filter((u) => u.estado === estado).length;
  const visibles = usuarios
    .filter((u) => filtro === "todos" || u.estado === filtro)
    .filter((u) => normalizar(`${u.nombres} ${u.apellidos} ${u.username} ${u.cedula} ${u.email}`).includes(normalizar(texto)));

  async function accion(u, tipo, valor) {
    setOcupado(u.id);
    try {
      await onAccion(u, tipo, valor);
    } finally {
      setOcupado(null);
    }
  }

  return (
    <section>
      <Encabezado titulo="Usuarios" subtitulo={`${usuarios.length} cuentas registradas`}>
        <Pestanas
          valor={filtro}
          onCambio={setFiltro}
          opciones={[
            { id: "todos", texto: "Todos" },
            { id: "pendiente", texto: "Por aprobar", contador: cuenta("pendiente") },
            { id: "suspendido", texto: "Bloqueados", contador: cuenta("suspendido") },
          ]}
        />
      </Encabezado>

      {/* Filtro rápido por nombre, usuario, cédula o correo */}
      <div className="relative mb-4 max-w-sm">
        <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Filtrar por nombre, cédula o correo…"
          aria-label="Filtrar usuarios"
          className="h-10 w-full rounded-xl border border-slate-200 bg-white pl-9 pr-3 text-sm shadow-sm outline-none
                     focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15
                     dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100 dark:shadow-none"
        />
      </div>

      {visibles.length === 0 ? (
        <Vacio Icono={Users} titulo="No hay usuarios en esta lista" />
      ) : (
        <ul className="divide-y divide-slate-200 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-md dark:divide-slate-800 dark:border-slate-800 dark:bg-slate-900 dark:shadow-none">
          {visibles.map((u) => {
            const esYo = u.id === yo?.id;
            const enProceso = ocupado === u.id;
            const { texto: textoEstado, tono } = ESTADO_USUARIO[u.estado];
            return (
              <li key={u.id} className="flex flex-wrap items-center gap-x-4 gap-y-3 p-4 sm:p-5">
                {/* Avatar + datos */}
                <div className="flex min-w-0 flex-1 basis-64 items-center gap-3">
                  <span className="grid size-10 shrink-0 place-items-center rounded-full bg-linear-to-br from-primary-500 to-primary-700 text-sm font-bold text-white">
                    {(u.nombres[0] + u.apellidos[0]).toUpperCase()}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-900 dark:text-white">
                      {u.nombres} {u.apellidos} {esYo && <span className="text-xs font-normal text-slate-400">(usted)</span>}
                    </p>
                    <p className="truncate text-xs text-slate-500 dark:text-slate-400">
                      @{u.username} · {u.cedula} · último acceso: {u.ultimo_acceso ? formatoFecha(u.ultimo_acceso) : "nunca"}
                    </p>
                  </div>
                </div>

                <Chip tono={tono}>{textoEstado}</Chip>

                {/* Rol: selector (o el rol a asignar, si la cuenta está por aprobar) */}
                <select
                  aria-label={`Rol de ${u.username}`}
                  value={u.estado === "pendiente" ? (rolAprobar[u.id] ?? u.rol) : u.rol}
                  disabled={esYo || enProceso}
                  onChange={(e) =>
                    u.estado === "pendiente"
                      ? setRolAprobar((r) => ({ ...r, [u.id]: e.target.value }))
                      : accion(u, "rol", e.target.value)
                  }
                  className="h-9 rounded-lg border border-slate-200 bg-white px-2 text-sm text-slate-700 outline-none
                             focus:border-primary-500 disabled:opacity-60
                             dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
                >
                  {ROLES.map((r) => <option key={r} value={r}>{NOMBRE_ROL[r]}</option>)}
                </select>

                {/* Acciones */}
                <div className="ml-auto flex items-center justify-end gap-1 sm:w-48">
                  {enProceso && <LoaderCircle size={18} className="animate-spin text-slate-400" />}
                  {!esYo && u.estado === "pendiente" && (
                    <Boton variante="exito" Icono={Check} disabled={enProceso} onClick={() => accion(u, "aprobar", rolAprobar[u.id] ?? u.rol)}>
                      Aprobar
                    </Boton>
                  )}
                  {!esYo && u.estado === "activo" && (
                    <Boton variante="fantasma" Icono={Ban} disabled={enProceso} onClick={() => accion(u, "bloquear")}>
                      Bloquear
                    </Boton>
                  )}
                  {!esYo && u.estado === "suspendido" && (
                    <Boton variante="fantasma" Icono={ShieldCheck} disabled={enProceso} onClick={() => accion(u, "desbloquear")}>
                      Desbloquear
                    </Boton>
                  )}
                  {!esYo && (
                    <button
                      aria-label={`Eliminar a ${u.username}`}
                      title="Eliminar cuenta"
                      disabled={enProceso}
                      onClick={() => window.confirm(`¿Eliminar la cuenta de ${u.nombres} ${u.apellidos}? No se puede deshacer.`) && accion(u, "eliminar")}
                      className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-500/10 dark:hover:text-rose-400"
                    >
                      <Trash2 size={18} />
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
