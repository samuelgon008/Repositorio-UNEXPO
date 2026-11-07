/* Dirección del backend FastAPI vista DESDE ESTE SERVIDOR (normalmente la
   misma computadora). El navegador nunca habla directo con el backend:
   pide /api/... a Next.js y Next.js lo reenvía. Así sólo hace falta exponer
   un puerto (3000) y el backend puede quedarse escuchando en 127.0.0.1. */
const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

/* Modo demostración (sin backend, con datos de prueba). Se activa con
   NEXT_PUBLIC_MODO_DEMO=1, y AUTOMÁTICAMENTE al compilar en Vercel (que
   define la variable VERCEL), porque allí no hay backend al que llegar.
   Para forzar el modo real en Vercel: NEXT_PUBLIC_MODO_DEMO=0. */
const MODO_DEMO = process.env.NEXT_PUBLIC_MODO_DEMO ?? (process.env.VERCEL ? "1" : "0");

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Deja el valor disponible para el código del navegador (lib/api.js)
  env: { NEXT_PUBLIC_MODO_DEMO: MODO_DEMO },

  async rewrites() {
    // En modo demostración no hay backend: no se reenvía nada.
    if (MODO_DEMO === "1") return [];
    return [{ source: "/api/:ruta*", destination: `${API_URL}/:ruta*` }];
  },
};

export default nextConfig;
