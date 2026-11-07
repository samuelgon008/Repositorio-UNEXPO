"""Regla central de acceso a los PDF de las tesis.

- Administrador (documento.descargar): lee y descarga cualquier tesis.
- Docente (documento.leer): lee en línea cualquier tesis; no descarga.
- Estudiante: sólo las tesis con una solicitud aprobada y vigente
  (lee y descarga hasta que vence o el administrador la revoca).
"""
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SolicitudAcceso, Usuario


@dataclass(frozen=True)
class Acceso:
    leer: bool
    descargar: bool


def ultimas_solicitudes(db: Session, usuario: Usuario) -> dict[int, SolicitudAcceso]:
    """La solicitud más reciente del usuario para cada tesis: {documento_id: solicitud}."""
    filas = db.scalars(
        select(SolicitudAcceso).where(SolicitudAcceso.usuario_id == usuario.id)
        .order_by(SolicitudAcceso.creada_en.desc(), SolicitudAcceso.id.desc())
    )
    ultimas: dict[int, SolicitudAcceso] = {}
    for s in filas:
        ultimas.setdefault(s.documento_id, s)
    return ultimas


def calcular_acceso(usuario: Usuario, solicitud: SolicitudAcceso | None, ahora: datetime) -> Acceso:
    permisos = usuario.codigos_permiso
    if "documento.descargar" in permisos:
        return Acceso(leer=True, descargar=True)
    if "documento.leer" in permisos:
        return Acceso(leer=True, descargar=False)
    if solicitud is not None and solicitud.vigente(ahora):
        return Acceso(leer=True, descargar=True)
    return Acceso(leer=False, descargar=False)
