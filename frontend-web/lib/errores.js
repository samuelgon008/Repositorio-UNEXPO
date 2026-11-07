/** Error de la API con su código HTTP (0 = sin conexión). */
export class ErrorApi extends Error {
  constructor(mensaje, estado) {
    super(mensaje);
    this.estado = estado;
  }
}
