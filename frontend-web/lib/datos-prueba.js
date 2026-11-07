/* ==========================================================================
   Datos de prueba que aún no vienen del backend.
   (Los proyectos ya se leen de la API: GET /documentos.)
   TODO: reemplazar por GET /notificaciones cuando exista la tabla.
   ========================================================================== */

export const notificaciones = [
  {
    id: 1,
    titulo: "Nuevo trabajo publicado",
    detalle: "«Sistema mecatrónico embebido para clasificación automática de piezas…» ya está disponible.",
    hace: "Hace 2 horas",
    leida: false,
  },
  {
    id: 2,
    titulo: "Tu solicitud de registro fue aprobada",
    detalle: "Ya puedes descargar los documentos completos en PDF.",
    hace: "Ayer",
    leida: false,
  },
  {
    id: 3,
    titulo: "Nuevo trabajo en Telecomunicaciones",
    detalle: "«Red de sensores LoRaWAN para el monitoreo de la calidad del agua…» coincide con tus intereses.",
    hace: "Hace 3 días",
    leida: true,
  },
];
