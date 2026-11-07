"""Solicitudes de acceso a los PDF.

Estudiante:     POST /solicitudes, GET /solicitudes/mias
Administrador:  GET /solicitudes, POST /solicitudes/{id}/aprobar | rechazar | revocar
"""
from datetime import timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import requiere_permiso
from app.core.catalogos import DIAS_ACCESO_SOLICITUD
from app.core.security import ahora_utc
from app.database import get_db
from app.models import Documento, EstadoSolicitud, SolicitudAcceso, Usuario
from app.schemas.solicitudes import ResolucionIn, SolicitudIn, SolicitudOut

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes de acceso"])
solo_estudiante = requiere_permiso("solicitud.crear")
solo_gestor = requiere_permiso("solicitud.gestionar")


def _salida(solicitudes) -> list[SolicitudOut]:
    ahora = ahora_utc()
    return [SolicitudOut.desde_modelo(s, ahora) for s in solicitudes]


# ------------------------------ Estudiante ------------------------------
@router.post("", response_model=SolicitudOut, status_code=status.HTTP_201_CREATED)
def crear(datos: SolicitudIn, db: Session = Depends(get_db), usuario: Usuario = Depends(solo_estudiante)):
    doc = db.get(Documento, datos.documento_id)
    if doc is None or not doc.publicado:
        raise HTTPException(404, "Tesis no encontrada")

    ahora = ahora_utc()
    previas = db.scalars(select(SolicitudAcceso).where(
        SolicitudAcceso.usuario_id == usuario.id, SolicitudAcceso.documento_id == doc.id))
    for s in previas:
        if s.estado == EstadoSolicitud.pendiente:
            raise HTTPException(409, "Ya tiene una solicitud pendiente para esta tesis")
        if s.vigente(ahora):
            raise HTTPException(409, "Ya tiene acceso a esta tesis")

    motivo = (datos.motivo or "").strip() or None
    solicitud = SolicitudAcceso(usuario_id=usuario.id, documento_id=doc.id, motivo=motivo)
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return _salida([solicitud])[0]


@router.get("/mias", response_model=list[SolicitudOut])
def mias(db: Session = Depends(get_db), usuario: Usuario = Depends(solo_estudiante)):
    return _salida(db.scalars(
        select(SolicitudAcceso).where(SolicitudAcceso.usuario_id == usuario.id)
        .order_by(SolicitudAcceso.creada_en.desc(), SolicitudAcceso.id.desc())
    ))


# ---------------------------- Administrador ----------------------------
@router.get("", response_model=list[SolicitudOut])
def listar(estado: Literal["pendiente", "aprobada", "rechazada", "revocada"] | None = None,
           db: Session = Depends(get_db), _: Usuario = Depends(solo_gestor)):
    """Todas las solicitudes (o sólo las de un estado); pendientes primero."""
    consulta = select(SolicitudAcceso)
    if estado:
        consulta = consulta.where(SolicitudAcceso.estado == EstadoSolicitud(estado))
    filas = db.scalars(consulta.order_by(SolicitudAcceso.creada_en.desc(), SolicitudAcceso.id.desc())).all()
    filas.sort(key=lambda s: s.estado != EstadoSolicitud.pendiente)  # orden estable: pendientes arriba
    return _salida(filas)


def _resolver(db: Session, solicitud_id: int, admin: Usuario, desde: EstadoSolicitud,
              hacia: EstadoSolicitud, nota: str | None) -> SolicitudOut:
    s = db.get(SolicitudAcceso, solicitud_id)
    if s is None:
        raise HTTPException(404, "Solicitud no encontrada")
    if s.estado != desde:
        raise HTTPException(409, f"La solicitud está {s.estado_visible(ahora_utc())}; no se puede cambiar así")
    ahora = ahora_utc()
    s.estado = hacia
    s.resuelta_en = ahora
    s.resuelta_por = admin.id
    s.nota_admin = (nota or "").strip() or None
    if hacia == EstadoSolicitud.aprobada:
        s.vence_en = ahora + timedelta(days=DIAS_ACCESO_SOLICITUD)
    db.commit()
    return _salida([s])[0]


@router.post("/{solicitud_id}/aprobar", response_model=SolicitudOut)
def aprobar(solicitud_id: int, datos: ResolucionIn | None = None, db: Session = Depends(get_db),
            admin: Usuario = Depends(solo_gestor)):
    """Habilita lectura y descarga de esa tesis durante DIAS_ACCESO_SOLICITUD días."""
    return _resolver(db, solicitud_id, admin, EstadoSolicitud.pendiente, EstadoSolicitud.aprobada,
                     datos.nota if datos else None)


@router.post("/{solicitud_id}/rechazar", response_model=SolicitudOut)
def rechazar(solicitud_id: int, datos: ResolucionIn | None = None, db: Session = Depends(get_db),
             admin: Usuario = Depends(solo_gestor)):
    return _resolver(db, solicitud_id, admin, EstadoSolicitud.pendiente, EstadoSolicitud.rechazada,
                     datos.nota if datos else None)


@router.post("/{solicitud_id}/revocar", response_model=SolicitudOut)
def revocar(solicitud_id: int, datos: ResolucionIn | None = None, db: Session = Depends(get_db),
            admin: Usuario = Depends(solo_gestor)):
    """Quita antes de tiempo un acceso aprobado."""
    return _resolver(db, solicitud_id, admin, EstadoSolicitud.aprobada, EstadoSolicitud.revocada,
                     datos.nota if datos else None)
