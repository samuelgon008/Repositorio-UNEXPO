import { Activity, ChevronRight, Cpu, Gauge, Network, Radio, Sun, Workflow, Zap } from "lucide-react";

/* Áreas temáticas del departamento (tabla `etiquetas` de la base de datos)
   con su icono y una descripción breve. */
export const CATEGORIAS = [
  { nombre: "Telecomunicaciones", Icono: Radio, descripcion: "Radiofrecuencia, antenas, SDR e IoT" },
  { nombre: "Control y Automatización", Icono: Workflow, descripcion: "PLC, SCADA, robótica y control clásico" },
  { nombre: "Electrónica de Potencia", Icono: Zap, descripcion: "Convertidores, inversores y máquinas eléctricas" },
  { nombre: "Instrumentación", Icono: Gauge, descripcion: "Sensores, medición y adquisición de datos" },
  { nombre: "Sistemas Digitales y Embebidos", Icono: Cpu, descripcion: "Microcontroladores, FPGA y firmware" },
  { nombre: "Procesamiento de Señales", Icono: Activity, descripcion: "DSP, bioseñales e inteligencia artificial" },
  { nombre: "Energías Renovables", Icono: Sun, descripcion: "Solar, eólica y eficiencia energética" },
  { nombre: "Redes y Comunicaciones de Datos", Icono: Network, descripcion: "Redes, protocolos y ciberseguridad" },
];

/** Vista "Explorar Categorías": una tarjeta por área con su número de trabajos. */
export default function VistaCategorias({ proyectos, onElegir }) {
  const conteo = (nombre) => proyectos.filter((p) => p.area === nombre).length;

  return (
    <section>
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl dark:text-white">
          Explorar Categorías
        </h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Elija un área para ver sus trabajos de grado e informes
        </p>
      </div>

      <div className="grid grid-cols-[repeat(auto-fill,minmax(min(100%,260px),1fr))] gap-4">
        {CATEGORIAS.map(({ nombre, Icono, descripcion }) => {
          const total = conteo(nombre);
          return (
            <button
              key={nombre}
              onClick={() => onElegir(nombre)}
              className="group flex items-start gap-4 rounded-2xl border border-slate-200 bg-white p-5 text-left
                         shadow-md transition duration-300 ease-suave hover:-translate-y-1 hover:border-primary-300 hover:shadow-xl
                         dark:border-slate-800 dark:bg-slate-900 dark:shadow-none dark:hover:border-primary-500/40"
            >
              <span
                className="grid size-11 shrink-0 place-items-center rounded-xl bg-primary-50 text-primary-600
                           transition-colors group-hover:bg-primary-600 group-hover:text-white
                           dark:bg-primary-500/15 dark:text-primary-300"
              >
                <Icono size={22} />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block font-semibold text-slate-900 dark:text-white">{nombre}</span>
                <span className="mt-0.5 block text-sm text-slate-500 dark:text-slate-400">{descripcion}</span>
                <span className="mt-2 block text-xs font-medium text-slate-400">
                  {total} {total === 1 ? "trabajo" : "trabajos"}
                </span>
              </span>
              <ChevronRight
                size={18}
                className="mt-1 shrink-0 text-slate-300 transition-transform group-hover:translate-x-0.5 group-hover:text-primary-500"
              />
            </button>
          );
        })}
      </div>
    </section>
  );
}
