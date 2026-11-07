"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { GraduationCap, Menu, RotateCw, SearchX, Star, TriangleAlert, X } from "lucide-react";

import BarraBusqueda from "@/components/BarraBusqueda";
import ListaNotificaciones from "@/components/ListaNotificaciones";
import Sidebar from "@/components/Sidebar";
import TarjetaProyecto from "@/components/TarjetaProyecto";
import VistaCategorias from "@/components/VistaCategorias";
import {
  MODO_DEMO, cerrarSesionLocal, listarDocumentos, obtenerPdf, obtenerToken, obtenerUsuario,
} from "@/lib/api";
import { notificaciones as notificacionesIniciales } from "@/lib/datos-prueba";
import { useTema } from "@/lib/useTema";

/* Minúsculas y sin acentos, para que "electronica" encuentre "Electrónica" */
const normalizar = (texto) => texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

/* Adapta un documento de la API (GET /documentos) a lo que muestra la tarjeta */
const adaptar = (d) => ({
  ...d,
  area: d.etiquetas[0] ?? "Sin categoría",
  carrera: "Ingeniería Electrónica",
  tutor: d.tutores.join(", "),
  palabrasClave: d.palabras_clave,
});

/* Lectura/escritura segura de localStorage (puede fallar en navegación privada) */
const leerLocal = (clave, porDefecto) => {
  try {
    const v = localStorage.getItem(clave);
    return v === null ? porDefecto : JSON.parse(v);
  } catch {
    return porDefecto;
  }
};
const guardarLocal = (clave, valor) => {
  try {
    localStorage.setItem(clave, JSON.stringify(valor));
  } catch {}
};

/* Entrega un Blob al navegador como archivo descargado */
function guardarArchivo(blob, nombre) {
  const url = URL.createObjectURL(blob);
  const enlace = Object.assign(document.createElement("a"), { href: url, download: nombre });
  enlace.click();
  setTimeout(() => URL.revokeObjectURL(url), 30_000);
}

/* Tarjeta gris animada mientras cargan los documentos */
function TarjetaEsqueleto() {
  return (
    <div className="animate-pulse rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
      <div className="h-5 w-32 rounded-full bg-slate-200 dark:bg-slate-800" />
      <div className="mt-4 h-4 w-full rounded bg-slate-200 dark:bg-slate-800" />
      <div className="mt-2 h-4 w-3/4 rounded bg-slate-200 dark:bg-slate-800" />
      <div className="mt-4 h-3 w-1/2 rounded bg-slate-200 dark:bg-slate-800" />
      <div className="mt-4 space-y-2">
        <div className="h-3 rounded bg-slate-100 dark:bg-slate-800/70" />
        <div className="h-3 rounded bg-slate-100 dark:bg-slate-800/70" />
        <div className="h-3 w-2/3 rounded bg-slate-100 dark:bg-slate-800/70" />
      </div>
    </div>
  );
}

export default function Inicio() {
  const router = useRouter();

  /* ======================= Estado de la interfaz ======================= */
  const [colapsado, setColapsado] = useState(false);       // sidebar sólo iconos
  const [abiertoMovil, setAbiertoMovil] = useState(false); // cajón en móvil
  const [vista, setVista] = useState("principal");         // principal | categorias | favoritos | notificaciones
  const [busqueda, setBusqueda] = useState("");
  const [categoria, setCategoria] = useState(null);        // área elegida en "Explorar Categorías"
  const [favoritos, setFavoritos] = useState([]);          // ids de documentos marcados con estrella
  const [notificaciones, setNotificaciones] = useState(notificacionesIniciales);
  const refBusqueda = useRef(null);
  const { oscuro, alternarTema } = useTema();

  /* ===================== Datos que vienen del backend ===================== */
  const [usuario, setUsuario] = useState(null);       // GET /auth/yo
  const [documentos, setDocumentos] = useState(null); // GET /documentos (null = cargando)
  const [errorCarga, setErrorCarga] = useState("");
  const [aviso, setAviso] = useState("");             // mensaje flotante temporal
  const [descargandoId, setDescargandoId] = useState(null);

  /* Sesión vencida o inválida → volver al login */
  const irAlLogin = useCallback(() => {
    cerrarSesionLocal();
    router.replace("/login");
  }, [router]);

  const manejarError = useCallback(
    (err) => (err.estado === 401 ? irAlLogin() : setAviso(err.message)),
    [irAlLogin],
  );

  const cargarDatos = useCallback(async () => {
    setErrorCarga("");
    setDocumentos(null);
    try {
      const [u, docs] = await Promise.all([obtenerUsuario(), listarDocumentos()]);
      setUsuario(u);
      setDocumentos(docs.map(adaptar));
    } catch (err) {
      if (err.estado === 401) irAlLogin();
      else setErrorCarga(err.message);
    }
  }, [irAlLogin]);

  /* Al entrar: sin token se va directo al login; con token, carga los datos */
  useEffect(() => {
    if (!obtenerToken()) {
      router.replace("/login");
      return;
    }
    setColapsado(leerLocal("sidebar-colapsado", false));
    // TODO: los favoritos deben venir de la API (tabla `favoritos`) en la siguiente fase.
    setFavoritos(leerLocal("favoritos", []));
    cargarDatos();
  }, [router, cargarDatos]);

  /* El aviso flotante se oculta solo a los 5 segundos */
  useEffect(() => {
    if (!aviso) return;
    const t = setTimeout(() => setAviso(""), 5000);
    return () => clearTimeout(t);
  }, [aviso]);

  const alternarColapso = () =>
    setColapsado((c) => {
      guardarLocal("sidebar-colapsado", !c);
      return !c;
    });

  const alternarFavorito = (id) =>
    setFavoritos((actual) => {
      const nuevo = actual.includes(id) ? actual.filter((f) => f !== id) : [...actual, id];
      guardarLocal("favoritos", nuevo);
      return nuevo;
    });

  /* Atajo de teclado: "/" enfoca la barra de búsqueda */
  useEffect(() => {
    const alPresionar = (e) => {
      const escribiendo = ["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName);
      if (e.key === "/" && !escribiendo) {
        e.preventDefault();
        refBusqueda.current?.focus();
      }
    };
    window.addEventListener("keydown", alPresionar);
    return () => window.removeEventListener("keydown", alPresionar);
  }, []);

  /* ============================ Navegación ============================ */
  const navegar = (destino) => {
    setVista(destino);
    setAbiertoMovil(false);
    if (destino !== "principal") setCategoria(null);
    if (destino === "principal" && vista === "principal") setCategoria(null); // 2º clic: quita el filtro
  };

  const elegirCategoria = (nombre) => {
    setCategoria(nombre);
    setVista("principal");
  };

  const cambiarBusqueda = (texto) => {
    setBusqueda(texto);
    // Escribir desde Categorías o Notificaciones lleva a los resultados
    if (texto && (vista === "categorias" || vista === "notificaciones")) setVista("principal");
  };

  const cerrarSesion = () => {
    if (window.confirm("¿Desea cerrar la sesión?")) irAlLogin();
  };

  /* ====================== PDF: ver y descargar ====================== */
  const puedeDescargar = usuario?.permisos.includes("documento.descargar") ?? false;

  const descargar = async (doc) => {
    setDescargandoId(doc.id);
    try {
      guardarArchivo(await obtenerPdf(doc.id), doc.nombre_archivo);
    } catch (err) {
      manejarError(err);
    } finally {
      setDescargandoId(null);
    }
  };

  const ver = async (doc) => {
    if (!puedeDescargar) {
      setAviso("Su rol permite consultar las fichas, pero no abrir el documento completo.");
      return;
    }
    // La pestaña se abre YA (dentro del clic) para que el navegador no la bloquee;
    // el PDF se coloca en ella cuando termina de descargarse.
    const pestana = window.open("", "_blank");
    try {
      const url = URL.createObjectURL(await obtenerPdf(doc.id));
      if (pestana) pestana.location.href = url;
      else window.location.href = url; // ventanas emergentes bloqueadas: abrir aquí
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (err) {
      pestana?.close();
      manejarError(err);
    }
  };

  /* ===================== Filtrado de los documentos ===================== */
  const indice = useMemo(
    () =>
      (documentos ?? []).map((p) => ({
        proyecto: p,
        texto: normalizar([p.titulo, ...p.autores, p.tutor, p.area, ...p.palabrasClave].join(" ")),
      })),
    [documentos],
  );

  const resultados = useMemo(() => {
    const terminos = normalizar(busqueda).split(/\s+/).filter(Boolean);
    return indice
      .filter(({ proyecto }) => vista !== "favoritos" || favoritos.includes(proyecto.id))
      .filter(({ proyecto }) => !categoria || proyecto.area === categoria)
      .filter(({ texto }) => terminos.every((t) => texto.includes(t))) // todas las palabras deben aparecer
      .map(({ proyecto }) => proyecto)
      .sort((a, b) => b.fecha.localeCompare(a.fecha)); // más recientes primero
  }, [indice, busqueda, categoria, vista, favoritos]);

  const pendientes = notificaciones.filter((n) => !n.leida).length;

  /* Encabezado de la sección según la vista, la categoría y la búsqueda */
  const titulo =
    vista === "favoritos" ? "Mis Favoritos" : categoria ?? (busqueda ? "Resultados de búsqueda" : "Proyectos Recientes");
  const cantidad = `${resultados.length} ${resultados.length === 1 ? "trabajo" : "trabajos"}`;
  const subtitulo = busqueda
    ? `${cantidad} para «${busqueda}»`
    : vista === "favoritos" || categoria
      ? cantidad
      : "Trabajos Especiales de Grado e Informes de Entrenamiento Industrial";

  const vacioFavoritos = vista === "favoritos" && favoritos.length === 0;

  /* ============================== Vista ============================== */
  return (
    <div className="flex min-h-screen">
      <Sidebar
        usuario={usuario}
        colapsado={colapsado}
        onAlternarColapso={alternarColapso}
        abiertoMovil={abiertoMovil}
        onCerrarMovil={() => setAbiertoMovil(false)}
        vistaActiva={vista}
        onNavegar={navegar}
        oscuro={oscuro}
        onAlternarTema={alternarTema}
        onCerrarSesion={cerrarSesion}
        pendientes={pendientes}
      />

      {/* min-w-0 evita que textos largos ensanchen la columna principal */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* -------- Barra superior: menú (móvil) + búsqueda, fija al hacer scroll -------- */}
        <header
          className="sticky top-0 z-20 border-b border-slate-200/70 bg-slate-100/80 backdrop-blur-md
                     dark:border-slate-800/70 dark:bg-slate-950/80"
        >
          <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-3 sm:px-6 sm:py-4 lg:px-10">
            <button
              onClick={() => setAbiertoMovil(true)}
              aria-label="Abrir menú"
              className="rounded-xl p-2.5 text-slate-600 hover:bg-slate-200/60 md:hidden dark:text-slate-300 dark:hover:bg-slate-800"
            >
              <Menu size={22} />
            </button>
            <BarraBusqueda ref={refBusqueda} valor={busqueda} onCambio={cambiarBusqueda} />
            {/* Distintivo visible sólo en la versión de demostración (Vercel) */}
            {MODO_DEMO && (
              <span
                title="Datos de prueba: no está conectado a la base de datos real"
                className="hidden shrink-0 rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800
                           lg:inline-block dark:bg-amber-500/15 dark:text-amber-300"
              >
                Demostración
              </span>
            )}
          </div>
        </header>

        {/* -------------------------- Contenido -------------------------- */}
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 sm:py-8 lg:px-10">
          {/* La `key` cambia con la vista o la categoría: React vuelve a montar este
              bloque y la animación de entrada (aparecer + subir) se repite */}
          <div key={`${vista}-${categoria ?? ""}`} className="animate-aparecer">
          {errorCarga ? (
            /* No se pudo hablar con el backend */
            <div className="flex flex-col items-center rounded-2xl border border-rose-200 bg-white px-6 py-16 text-center dark:border-rose-500/30 dark:bg-slate-900">
              <TriangleAlert size={40} className="text-rose-500" />
              <p className="mt-4 font-semibold text-slate-800 dark:text-slate-100">No se pudieron cargar los documentos</p>
              <p className="mt-1 max-w-md text-sm text-slate-500 dark:text-slate-400">{errorCarga}</p>
              <button
                onClick={cargarDatos}
                className="mt-5 inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700"
              >
                <RotateCw size={16} /> Reintentar
              </button>
            </div>
          ) : vista === "notificaciones" ? (
            <ListaNotificaciones
              notificaciones={notificaciones}
              onMarcarTodas={() => setNotificaciones((ns) => ns.map((n) => ({ ...n, leida: true })))}
            />
          ) : vista === "categorias" ? (
            <VistaCategorias proyectos={documentos ?? []} onElegir={elegirCategoria} />
          ) : (
            <section>
              <div className="mb-6">
                <h2 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl dark:text-white">
                  {titulo}
                </h2>
                <div className="mt-1 flex flex-wrap items-center gap-2">
                  <p className="text-sm text-slate-500 dark:text-slate-400">{subtitulo}</p>
                  {/* Distintivo para quitar el filtro de categoría */}
                  {categoria && (
                    <button
                      onClick={() => setCategoria(null)}
                      className="inline-flex items-center gap-1 rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-medium
                                 text-primary-700 hover:bg-primary-100 dark:bg-primary-500/15 dark:text-primary-300"
                    >
                      Quitar filtro <X size={12} />
                    </button>
                  )}
                </div>
              </div>

              {documentos === null ? (
                /* Cargando */
                <div className="grid grid-cols-[repeat(auto-fill,minmax(min(100%,300px),1fr))] gap-5">
                  {Array.from({ length: 6 }, (_, i) => <TarjetaEsqueleto key={i} />)}
                </div>
              ) : resultados.length > 0 ? (
                /* Grid responsivo: tantas columnas de ≥ 300 px como quepan
                   (se adapta solo cuando el sidebar se colapsa o expande) */
                <div className="grid grid-cols-[repeat(auto-fill,minmax(min(100%,300px),1fr))] gap-5">
                  {resultados.map((p) => (
                    <TarjetaProyecto
                      key={p.id}
                      proyecto={p}
                      favorito={favoritos.includes(p.id)}
                      onAlternarFavorito={() => alternarFavorito(p.id)}
                      onVer={() => ver(p)}
                      onDescargar={() => descargar(p)}
                      puedeDescargar={puedeDescargar}
                      descargando={descargandoId === p.id}
                    />
                  ))}
                </div>
              ) : (
                /* Estado vacío */
                <div className="flex flex-col items-center rounded-2xl border border-dashed border-slate-300 px-6 py-16 text-center dark:border-slate-700">
                  {vacioFavoritos ? (
                    <Star size={40} className="text-slate-400" />
                  ) : (
                    <SearchX size={40} className="text-slate-400" />
                  )}
                  <p className="mt-4 font-semibold text-slate-700 dark:text-slate-200">
                    {vacioFavoritos ? "Aún no tiene favoritos" : documentos.length === 0 ? "El repositorio está vacío" : "No encontramos trabajos"}
                  </p>
                  <p className="mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">
                    {vacioFavoritos
                      ? "Marque la estrella de cualquier trabajo para guardarlo aquí."
                      : documentos.length === 0
                        ? "Todavía no se ha publicado ningún documento."
                        : "Pruebe con otras palabras, el apellido de un autor u otra categoría."}
                  </p>
                  {documentos.length > 0 && (
                    <button
                      onClick={() => {
                        setBusqueda("");
                        setCategoria(null);
                        setVista("principal");
                      }}
                      className="mt-5 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700"
                    >
                      Ver todos los trabajos
                    </button>
                  )}
                </div>
              )}
            </section>
          )}
          </div>
        </main>

        <footer className="flex items-center justify-center gap-2 py-6 text-xs text-slate-400">
          <GraduationCap size={14} /> Departamento de Ingeniería Electrónica · UNEXPO
        </footer>
      </div>

      {/* Aviso flotante (errores de descarga, permisos, etc.) */}
      {aviso && (
        <div
          role="status"
          className="fixed inset-x-4 bottom-4 z-50 mx-auto flex max-w-md items-start gap-3 rounded-xl bg-slate-900 px-4 py-3
                     text-sm text-white shadow-2xl dark:bg-slate-700"
        >
          <TriangleAlert size={18} className="mt-0.5 shrink-0 text-amber-400" />
          <p className="flex-1">{aviso}</p>
          <button onClick={() => setAviso("")} aria-label="Cerrar aviso" className="text-slate-400 hover:text-white">
            <X size={18} />
          </button>
        </div>
      )}
    </div>
  );
}
