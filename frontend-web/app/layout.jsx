import "./globals.css";

export const metadata = {
  title: "Repositorio Digital · Ing. Electrónica UNEXPO",
  description: "Trabajos Especiales de Grado e Informes de Entrenamiento Industrial",
};

/* Se ejecuta ANTES de pintar la página: aplica el tema guardado (o el del
   sistema operativo la primera vez) para evitar un destello blanco al
   cargar en modo oscuro. */
const scriptTema = `
(function () {
  try {
    var t = localStorage.getItem("tema");
    var oscuro = t ? t === "oscuro" : matchMedia("(prefers-color-scheme: dark)").matches;
    if (oscuro) document.documentElement.classList.add("dark");
  } catch (e) {}
})();`;

export default function RootLayout({ children }) {
  return (
    // suppressHydrationWarning: el script anterior modifica la clase de <html>
    // antes de que React se hidrate; es intencional.
    <html lang="es" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: scriptTema }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
