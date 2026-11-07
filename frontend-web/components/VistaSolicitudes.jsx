"use client";

import { useState } from "react";
import { Check, Inbox, LoaderCircle, Undo2, X } from "lucide-react";

import { Boton, Chip, Encabezado, ESTADO_SOLICITUD, formatoFecha, Modal, Pestanas, Vacio } from "@/components/ui";

/**
 * Panel del ADMINISTRADOR: solicitudes de acceso de los estudiantes.
 * Aprobar (30 días), rechazar (con nota opcional) o revocar un acceso vigente.
 */
export default function VistaSolicitudes({ solicitudes, onResolver }) {
  const [filtro, setFiltro] = useState("pendiente");
  const [ocupada, setOcupada] = useState(null);   // id de la solicitud en proceso
  const [rechazando, setRechazando] = useState(null);
  const [nota, setNota] = useState("");

  if (solicitudes === null) return <p className="text-sm text-slate-500">Cargando solicitudes…</p>;

  const cuenta = (estado) => solicitudes.filter((s) => s.estado === estado).length;
  const visibles = filtro === "todas" ? solicitudes : solicitudes.filter((s) => s.estado === filtro);

  async function resolver(s, accion, textoNota) {
    setOcupada(s.id);
    try {
      await onResolver(s.id, accion, textoNota);
    } finally {
      setOcupada(null);
    }
  }

  return (
    <section>
      <Encabezado titulo="Solicitudes de acceso" subtitulo="Estudiantes que piden leer y descargar una tesis">
        <Pestanas
          valor={filtro}
          onCambio={setFiltro}
          opciones={[
            { id: "pendiente", texto: "Pendientes", contador: cuenta("pendiente") },
            { id: "aprobada", texto: "Aprobadas", contador: cuenta("aprobada") },
            { id: "todas", texto: "Todas" },
          ]}
        />
      </Encabezado>

      {visibles.length === 0 ? (
        <Vacio
          Icono={Inbox}
          titulo={filtro === "pendiente" ? "No hay solicitudes pendientes" : "No hay solicitudes aquí"}
          texto="Cuando un estudiante pida acceso a una tesis, aparecerá en esta lista."
        />
      ) : (
        <ul className="space-y-3">
          {visibles.map((s) => {
            const { texto, tono } = ESTADO_SOLICITUD[s.estado];
            const enProceso = ocupada === s.id;
            return (
              <li
                key={s.id}
                className="rounded-2xl border border-slate-200 bg-white p-4 shadow-md sm:p-5 dark:border-slate-800 dark:bg-slate-900 dark:shadow-none"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold text-slate-900 dark:text-white">{s.documento_titulo}</p>
                    <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                      <span className="font-medium text-slate-700 dark:text-slate-200">{s.usuario_nombre}</span>
                      {" · "}@{s.usuario_username} · {s.usuario_cedula} · {formatoFecha(s.creada_en)}
                    </p>
                  </div>
                  <Chip tono={tono}>{texto}</Chip>
                </div>

                {s.motivo && (
                  <p className="mt-3 border-l-2 border-primary-300 pl-3 text-sm italic text-slate-600 dark:border-primary-500/50 dark:text-slate-300">
                    «{s.motivo}»
                  </p>
                )}
                {s.estado === "aprobada" && (
                  <p className="mt-2 text-xs text-emerald-600 dark:text-emerald-400">Acceso hasta el {formatoFecha(s.vence_en)}</p>
                )}
                {s.nota_admin && <p className="mt-2 text-xs text-slate-500">Nota: «{s.nota_admin}»</p>}

                {/* Acciones */}
                {(s.estado === "pendiente" || s.estado === "aprobada") && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {enProceso && <LoaderCircle size={20} className="animate-spin text-slate-400" />}
                    {s.estado === "pendiente" ? (
                      <>
                        <Boton variante="exito" Icono={Check} disabled={enProceso} onClick={() => resolver(s, "aprobar")}>
                          Aprobar 30 días
                        </Boton>
                        <Boton variante="suave" Icono={X} disabled={enProceso} onClick={() => { setRechazando(s); setNota(""); }}>
                          Rechazar
                        </Boton>
                      </>
                    ) : (
                      <Boton
                        variante="suave"
                        Icono={Undo2}
                        disabled={enProceso}
                        onClick={() => window.confirm(`¿Revocar el acceso de ${s.usuario_nombre} a esta tesis?`) && resolver(s, "revocar")}
                      >
                        Revocar acceso
                      </Boton>
                    )}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}

      {/* Rechazo con nota opcional para el estudiante */}
      {rechazando && (
        <Modal
          titulo="Rechazar solicitud"
          onCerrar={() => setRechazando(null)}
          acciones={
            <>
              <Boton variante="suave" onClick={() => setRechazando(null)}>Cancelar</Boton>
              <Boton
                variante="peligro"
                onClick={async () => {
                  const s = rechazando;
                  setRechazando(null);
                  await resolver(s, "rechazar", nota);
                }}
              >
                Rechazar
              </Boton>
            </>
          }
        >
          <p className="text-sm text-slate-600 dark:text-slate-300">
            {rechazando.usuario_nombre} — «{rechazando.documento_titulo}»
          </p>
          <label htmlFor="nota" className="mt-4 block text-sm font-medium text-slate-700 dark:text-slate-200">
            Nota para el estudiante <span className="font-normal text-slate-400">(opcional)</span>
          </label>
          <input
            id="nota"
            value={nota}
            onChange={(e) => setNota(e.target.value.slice(0, 300))}
            autoFocus
            placeholder="Ej.: Indique para qué necesita el documento."
            className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none
                       focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15
                       dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          />
        </Modal>
      )}
    </section>
  );
}
