"use client";

import { useState } from "react";
import { KeyRound, LoaderCircle } from "lucide-react";

import { Boton, Modal } from "@/components/ui";

const MAX_MOTIVO = 500;

/** Ventana para que el estudiante pida acceso al PDF de una tesis. */
export default function ModalSolicitud({ proyecto, onEnviar, onCerrar }) {
  const [motivo, setMotivo] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState("");

  async function enviar() {
    setEnviando(true);
    setError("");
    try {
      await onEnviar(motivo);
    } catch (err) {
      setError(err.message);
      setEnviando(false);
    }
  }

  return (
    <Modal
      titulo="Solicitar acceso a la tesis"
      onCerrar={onCerrar}
      acciones={
        <>
          <Boton variante="suave" onClick={onCerrar}>Cancelar</Boton>
          <Boton onClick={enviar} disabled={enviando} Icono={enviando ? undefined : KeyRound}>
            {enviando && <LoaderCircle size={16} className="animate-spin" />}
            Enviar solicitud
          </Boton>
        </>
      }
    >
      <p className="rounded-xl bg-slate-50 p-3 text-sm font-medium text-slate-800 dark:bg-slate-800/60 dark:text-slate-100">
        {proyecto.titulo}
      </p>
      <p className="mt-3 text-sm text-slate-600 dark:text-slate-400">
        Un administrador revisará su solicitud. Si la aprueba, podrá leer y descargar esta tesis durante <strong>30 días</strong>.
      </p>

      <label className="mt-4 block text-sm font-medium text-slate-700 dark:text-slate-200" htmlFor="motivo">
        Motivo <span className="font-normal text-slate-400">(opcional, ayuda a que la aprueben)</span>
      </label>
      <textarea
        id="motivo"
        value={motivo}
        onChange={(e) => setMotivo(e.target.value.slice(0, MAX_MOTIVO))}
        rows={3}
        autoFocus
        placeholder="Ej.: La necesito como antecedente para mi Trabajo Especial de Grado."
        className="mt-1.5 w-full resize-none rounded-xl border border-slate-200 bg-white p-3 text-sm outline-none transition
                   focus:border-primary-500 focus:ring-4 focus:ring-primary-500/15
                   dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
      />
      <p className="mt-1 text-right text-xs text-slate-400">{motivo.length}/{MAX_MOTIVO}</p>

      {error && (
        <p role="alert" className="mt-2 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700 dark:bg-rose-500/10 dark:text-rose-300">
          {error}
        </p>
      )}
    </Modal>
  );
}
