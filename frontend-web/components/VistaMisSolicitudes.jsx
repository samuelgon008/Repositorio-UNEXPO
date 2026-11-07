import { BookOpen, Send } from "lucide-react";

import { Boton, Chip, Encabezado, ESTADO_SOLICITUD, formatoFecha, Vacio } from "@/components/ui";

/** Vista del ESTUDIANTE: el estado de cada solicitud que ha hecho. */
export default function VistaMisSolicitudes({ solicitudes, onLeer }) {
  if (solicitudes === null) return <p className="text-sm text-slate-500">Cargando sus solicitudes…</p>;

  return (
    <section>
      <Encabezado
        titulo="Mis Solicitudes"
        subtitulo="Pida acceso desde la tarjeta de cada tesis; si se aprueba, podrá leerla y descargarla durante 30 días."
      />

      {solicitudes.length === 0 ? (
        <Vacio
          Icono={Send}
          titulo="Todavía no ha solicitado acceso a ninguna tesis"
          texto="Use el botón «Solicitar acceso» en la tarjeta de la tesis que necesite."
        />
      ) : (
        <ul className="divide-y divide-slate-200 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-md dark:divide-slate-800 dark:border-slate-800 dark:bg-slate-900 dark:shadow-none">
          {solicitudes.map((s) => {
            const { texto, tono } = ESTADO_SOLICITUD[s.estado];
            return (
              <li key={s.id} className="flex flex-wrap items-center gap-4 p-4 sm:p-5">
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-slate-900 dark:text-white">{s.documento_titulo}</p>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    Solicitada el {formatoFecha(s.creada_en)}
                    {s.estado === "aprobada" && <> · acceso hasta el {formatoFecha(s.vence_en)}</>}
                  </p>
                  {s.nota_admin && <p className="mt-1 text-xs text-slate-500">Respuesta: «{s.nota_admin}»</p>}
                </div>
                <Chip tono={tono}>{texto}</Chip>
                {s.estado === "aprobada" && (
                  <Boton variante="suave" Icono={BookOpen} onClick={() => onLeer(s.documento_id)}>
                    Leer
                  </Boton>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
