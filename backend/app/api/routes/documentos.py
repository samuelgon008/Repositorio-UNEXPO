"""Consulta, lectura, descarga y administración de las tesis."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_usuario_actual, requiere_permiso
from app.config import settings
from app.core.security import ahora_utc
from app.database import get_db
from app.models import Descarga, Documento, DocumentoPersona, Usuario
from app.schemas.auth import MensajeOut
from app.schemas.documentos import DocumentoEdicionIn, DocumentoOut
from app.schemas.solicitudes import SolicitudBreve
from app.services.acceso import calcular_acceso, ultimas_solicitudes

router = APIRouter(prefix="/documentos", tags=["Documentos"])

_con_metadatos = (
    selectinload(Documento.participantes).joinedload(DocumentoPersona.persona),
    selectinload(Documento.etiquetas),
    selectinload(Documento.palabras_clave),
)


def _ve_ocultos(usuario: Usuario) -> bool:
    """Quien edita las tesis también ve las ocultas (no publicadas)."""
    return "documento.editar" in usuario.codigos_permiso


def _buscar(db: Session, documento_id: int, usuario: Usuario) -> Documento:
    consulta = select(Documento).options(*_con_metadatos).where(Documento.id == documento_id)
    if not _ve_ocultos(usuario):
        consulta = consulta.where(Documento.publicado.is_(True))
    doc = db.scalar(consulta)
    if doc is None:
        raise HTTPException(404, "Tesis no encontrada")
    return doc


def _salida(db: Session, docs: list[Documento], usuario: Usuario) -> list[DocumentoOut]:
    """Agrega a cada tesis lo que este usuario puede hacer con ella."""
    ahora = ahora_utc()
    solicitudes = ultimas_solicitudes(db, usuario) if "solicitud.crear" in usuario.codigos_permiso else {}
    salida = []
    for d in docs:
        s = solicitudes.get(d.id)
        acceso = calcular_acceso(usuario, s, ahora)
        salida.append(DocumentoOut.desde_modelo(
            d, puede_leer=acceso.leer, puede_descargar=acceso.descargar,
            solicitud=SolicitudBreve.desde_modelo(s, ahora) if s else None,
        ))
    return salida


def _archivo(doc: Documento):
    base = settings.storage_dir.resolve()
    ruta = (base / doc.ruta_archivo).resolve()
    # Defensa ante rutas manipuladas en la BD: el archivo debe estar dentro de storage/
    if not ruta.is_relative_to(base) or not ruta.is_file():
        raise HTTPException(404, "El archivo de esta tesis no está disponible")
    return ruta


def _verificar_acceso(db: Session, doc: Documento, usuario: Usuario, descargar: bool) -> None:
    s = ultimas_solicitudes(db, usuario).get(doc.id) if "solicitud.crear" in usuario.codigos_permiso else None
    acceso = calcular_acceso(usuario, s, ahora_utc())
    permitido = acceso.descargar if descargar else acceso.leer
    if not permitido:
        if "solicitud.crear" in usuario.codigos_permiso:
            raise HTTPException(403, "Necesita una solicitud de acceso aprobada para esta tesis")
        raise HTTPException(403, "Su rol no permite descargar las tesis" if descargar
                            else "Su rol no permite abrir las tesis")


# ------------------------------ Consulta ------------------------------
@router.get("", response_model=list[DocumentoOut])
def listar(db: Session = Depends(get_db), usuario: Usuario = Depends(requiere_permiso("documento.ver"))):
    """Tesis del más reciente al más antiguo (el administrador ve también las ocultas)."""
    consulta = select(Documento).options(*_con_metadatos)
    if not _ve_ocultos(usuario):
        consulta = consulta.where(Documento.publicado.is_(True))
    docs = db.scalars(consulta.order_by(Documento.fecha_aprobacion.desc(), Documento.id.desc())).all()
    return _salida(db, docs, usuario)


@router.get("/{documento_id}", response_model=DocumentoOut)
def detalle(documento_id: int, db: Session = Depends(get_db),
            usuario: Usuario = Depends(requiere_permiso("documento.ver"))):
    return _salida(db, [_buscar(db, documento_id, usuario)], usuario)[0]


# ------------------------ Lectura y descarga ------------------------
@router.get("/{documento_id}/ver", response_class=FileResponse)
def ver(documento_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_usuario_actual)):
    """PDF para leer en el navegador (administrador, docente o estudiante autorizado)."""
    doc = _buscar(db, documento_id, usuario)
    _verificar_acceso(db, doc, usuario, descargar=False)
    return FileResponse(_archivo(doc), media_type="application/pdf",
                        filename=doc.nombre_original, content_disposition_type="inline")


@router.get("/{documento_id}/descargar", response_class=FileResponse)
def descargar(documento_id: int, request: Request, db: Session = Depends(get_db),
              usuario: Usuario = Depends(get_usuario_actual)):
    """PDF como archivo descargable (administrador o estudiante autorizado). Queda auditado."""
    doc = _buscar(db, documento_id, usuario)
    _verificar_acceso(db, doc, usuario, descargar=True)
    ruta = _archivo(doc)
    db.add(Descarga(usuario_id=usuario.id, documento_id=doc.id,
                    ip=request.client.host if request.client else None))
    db.commit()
    return FileResponse(ruta, media_type="application/pdf", filename=doc.nombre_original)


# -------------------------- Administración --------------------------
@router.patch("/{documento_id}", response_model=DocumentoOut)
def editar(documento_id: int, cambios: DocumentoEdicionIn, db: Session = Depends(get_db),
           usuario: Usuario = Depends(requiere_permiso("documento.editar"))):
    doc = _buscar(db, documento_id, usuario)
    for campo, valor in cambios.model_dump(exclude_unset=True).items():
        setattr(doc, campo, valor)
    db.commit()
    return _salida(db, [doc], usuario)[0]


@router.delete("/{documento_id}", response_model=MensajeOut)
def eliminar(documento_id: int, db: Session = Depends(get_db),
             usuario: Usuario = Depends(requiere_permiso("documento.eliminar"))):
    """Borra la tesis, su PDF, sus solicitudes y su historial de descargas."""
    doc = _buscar(db, documento_id, usuario)
    try:
        ruta = _archivo(doc)
    except HTTPException:
        ruta = None  # el archivo ya no existe: igual se borra el registro
    titulo = doc.titulo
    db.delete(doc)
    db.commit()
    if ruta:
        ruta.unlink(missing_ok=True)
    return MensajeOut(detail=f"Tesis eliminada: «{titulo}»")
