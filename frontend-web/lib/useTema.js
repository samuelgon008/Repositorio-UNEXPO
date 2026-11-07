"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const DURACION_TRANSICION_MS = 450; // igual que .tema-transicion en globals.css

/**
 * Estado del modo claro/oscuro.
 * - La fuente de verdad es la clase `.dark` en <html> (la usa Tailwind).
 * - La preferencia se guarda en localStorage para la próxima visita.
 * - Durante el cambio se activa `.tema-transicion` para que todos los
 *   colores se desvanezcan suavemente en vez de cambiar de golpe.
 */
export function useTema() {
  const [oscuro, setOscuro] = useState(false);
  const temporizador = useRef(null);

  // Al montar, lee el tema que ya aplicó el script de layout.jsx
  useEffect(() => {
    setOscuro(document.documentElement.classList.contains("dark"));
    return () => clearTimeout(temporizador.current);
  }, []);

  const alternarTema = useCallback(() => {
    const raiz = document.documentElement;
    const nuevo = !raiz.classList.contains("dark");

    raiz.classList.add("tema-transicion");
    raiz.classList.toggle("dark", nuevo);
    clearTimeout(temporizador.current);
    temporizador.current = setTimeout(() => raiz.classList.remove("tema-transicion"), DURACION_TRANSICION_MS);

    try {
      localStorage.setItem("tema", nuevo ? "oscuro" : "claro");
    } catch {
      /* navegación privada: el tema funciona, sólo no se recuerda */
    }
    setOscuro(nuevo);
  }, []);

  return { oscuro, alternarTema };
}
