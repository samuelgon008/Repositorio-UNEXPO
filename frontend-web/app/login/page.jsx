"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, FlaskConical, GraduationCap, LoaderCircle, LockKeyhole, UserRound } from "lucide-react";

import { CLAVE_DEMO, CUENTAS_DEMO, MODO_DEMO, iniciarSesion, reiniciarDemo } from "@/lib/api";

/* Campo de texto con icono a la izquierda */
function Campo({ Icono, children }) {
  return (
    <div className="group relative">
      <Icono
        size={18}
        className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400
                   transition-colors group-focus-within:text-primary-600 dark:group-focus-within:text-primary-400"
      />
      {children}
    </div>
  );
}

const estiloInput =
  "h-12 w-full rounded-xl border border-slate-200 bg-white pl-11 pr-11 text-sm text-slate-800 outline-none " +
  "transition placeholder:text-slate-400 focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15 " +
  "dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100";

export default function Login() {
  const router = useRouter();
  const [usuario, setUsuario] = useState("");
  const [clave, setClave] = useState("");
  const [verClave, setVerClave] = useState(false);
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function enviar(e) {
    e.preventDefault();
    if (!usuario.trim() || !clave) {
      setError("Ingrese su usuario y contraseña.");
      return;
    }
    setEnviando(true);
    setError("");
    try {
      await iniciarSesion(usuario.trim(), clave);
      router.replace("/"); // al panel principal
    } catch (err) {
      setError(err.message);
      setClave("");
      setEnviando(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center px-4 py-10">
      <div className="w-full max-w-sm">
        {/* Encabezado */}
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="grid size-14 place-items-center rounded-2xl bg-primary-600 text-white shadow-lg shadow-primary-600/30">
            <GraduationCap size={30} />
          </div>
          <h1 className="mt-4 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Repositorio Digital</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Ingeniería Electrónica · UNEXPO</p>
        </div>

        {/* Modo demostración: una cuenta por rol para probar los permisos */}
        {MODO_DEMO && (
          <div className="mb-4 rounded-2xl border border-primary-200 bg-primary-50 p-4 text-sm
                          dark:border-primary-500/30 dark:bg-primary-500/10">
            <div className="flex items-start gap-3">
              <FlaskConical size={20} className="mt-0.5 shrink-0 text-primary-600 dark:text-primary-300" />
              <div className="min-w-0 flex-1 text-slate-700 dark:text-slate-200">
                <p className="font-semibold">Versión de demostración</p>
                <p className="mt-0.5 text-slate-600 dark:text-slate-300">
                  Elija un rol para probarlo (contraseña <code className="font-semibold">{CLAVE_DEMO}</code>):
                </p>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-2">
              {CUENTAS_DEMO.map(({ usuario: u, rol }) => (
                <button
                  key={u}
                  type="button"
                  onClick={() => {
                    setUsuario(u);
                    setClave(CLAVE_DEMO);
                    setError("");
                  }}
                  className={`rounded-lg border px-2 py-1.5 text-xs font-semibold transition-colors ${
                    usuario === u
                      ? "border-primary-500 bg-primary-600 text-white"
                      : "border-primary-200 bg-white text-primary-700 hover:bg-primary-100 dark:border-primary-500/30 dark:bg-slate-900 dark:text-primary-300"
                  }`}
                >
                  {rol}
                </button>
              ))}
            </div>
            <button
              type="button"
              onClick={() => {
                if (window.confirm("¿Volver la demo a su estado inicial? Se borran las solicitudes y cambios de prueba.")) {
                  reiniciarDemo();
                  setError("");
                }
              }}
              className="mt-3 text-xs text-slate-500 hover:text-slate-700 hover:underline dark:text-slate-400"
            >
              Reiniciar datos de la demo
            </button>
          </div>
        )}

        {/* Formulario */}
        <form
          onSubmit={enviar}
          noValidate
          className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-md sm:p-8
                     dark:border-slate-800 dark:bg-slate-900 dark:shadow-none"
        >
          <Campo Icono={UserRound}>
            <input
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
              placeholder="Usuario"
              aria-label="Usuario"
              autoComplete="username"
              autoCapitalize="none"
              autoFocus
              className={estiloInput}
            />
          </Campo>

          <Campo Icono={LockKeyhole}>
            <input
              type={verClave ? "text" : "password"}
              value={clave}
              onChange={(e) => setClave(e.target.value)}
              placeholder="Contraseña"
              aria-label="Contraseña"
              autoComplete="current-password"
              className={estiloInput}
            />
            <button
              type="button"
              onClick={() => setVerClave((v) => !v)}
              aria-label={verClave ? "Ocultar contraseña" : "Mostrar contraseña"}
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              {verClave ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </Campo>

          {error && (
            <p role="alert" className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700 dark:bg-rose-500/10 dark:text-rose-300">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={enviando}
            className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-primary-600 text-sm font-semibold
                       text-white shadow-sm transition hover:bg-primary-700 disabled:cursor-wait disabled:opacity-70"
          >
            {enviando && <LoaderCircle size={18} className="animate-spin" />}
            {enviando ? "Ingresando…" : "Ingresar"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-slate-400">
          {MODO_DEMO
            ? "Los trabajos y documentos de esta versión son datos de prueba."
            : "¿No tiene cuenta? Solicítela al administrador del departamento."}
        </p>
      </div>
    </main>
  );
}
