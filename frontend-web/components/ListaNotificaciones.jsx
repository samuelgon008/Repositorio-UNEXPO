import { Bell, CheckCheck } from "lucide-react";

/** Vista "Notificaciones": lista simple con indicador de no leídas. */
export default function ListaNotificaciones({ notificaciones, onMarcarTodas }) {
  const pendientes = notificaciones.filter((n) => !n.leida).length;

  return (
    <section>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Notificaciones</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {pendientes ? `Tienes ${pendientes} sin leer` : "Estás al día"}
          </p>
        </div>
        {pendientes > 0 && (
          <button
            onClick={onMarcarTodas}
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-primary-600
                       hover:bg-primary-50 dark:text-primary-400 dark:hover:bg-primary-500/10"
          >
            <CheckCheck size={16} /> Marcar todas como leídas
          </button>
        )}
      </div>

      <ul className="divide-y divide-slate-200 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-md dark:divide-slate-800 dark:border-slate-800 dark:bg-slate-900 dark:shadow-none">
        {notificaciones.map((n) => (
          <li key={n.id} className="flex gap-4 p-4 sm:p-5">
            <div
              className={`grid size-10 shrink-0 place-items-center rounded-full ${
                n.leida
                  ? "bg-slate-100 text-slate-400 dark:bg-slate-800"
                  : "bg-primary-50 text-primary-600 dark:bg-primary-500/15 dark:text-primary-300"
              }`}
            >
              <Bell size={18} />
            </div>
            <div className="min-w-0 flex-1">
              <p className="flex items-center gap-2 text-sm font-semibold text-slate-900 dark:text-white">
                {n.titulo}
                {!n.leida && <span className="size-2 rounded-full bg-primary-500" aria-label="sin leer" />}
              </p>
              <p className="mt-0.5 text-sm text-slate-600 dark:text-slate-400">{n.detalle}</p>
              <p className="mt-1 text-xs text-slate-400">{n.hace}</p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
