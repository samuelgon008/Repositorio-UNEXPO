"""Consulta y descarga de documentos."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import requiere_permiso
from app.config import settings
from app.database import get_db
from app.models import Descarga, Documento, DocumentoPersona, Usuario
from app.schemas.documentos import DocumentoOut

router = APIRouter(prefix="/documentos", tags=["Documentos"])

_con_metadatos = (
    selectinload(Documento.participantes).joinedload(DocumentoPersona.persona),
    selectinload(Documento.etiquetas),
    selectinload(Documento.palabras_clave),
)


def _publicado(db: Session, documento_id: int) -> Documento:
    doc = db.scalar(
        select(Documento).options(*_con_metadatos)
        .where(Documento.id == documento_id, Documento.publicado.is_(True))
    )
    if doc is None:
        raise HTTPException(404, "Documento no encontrado")
    return doc


@router.get("", response_model=list[DocumentoOut])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(requiere_permiso("documento.ver"))):
    """Documentos publicados, del más reciente al más antiguo."""
    docs = db.scalars(
        select(Documento).options(*_con_metadatos)
        .where(Documento.publicado.is_(True))
        .order_by(Documento.fecha_aprobacion.desc(), Documento.id.desc())
    )
    return [DocumentoOut.desde_modelo(d) for d in docs]


@router.get("/{documento_id}", response_model=DocumentoOut)
def detalle(documento_id: int, db: Session = Depends(get_db),
            _: Usuario = Depends(requiere_permiso("documento.ver"))):
    return DocumentoOut.desde_modelo(_publicado(db, documento_id))


@router.get("/{documento_id}/descargar", response_class=FileResponse)
def descargar(documento_id: int, request: Request, db: Session = Depends(get_db),
              usuario: Usuario = Depends(requiere_permiso("documento.descargar"))):
    doc = _publicado(db, documento_id)

    base = settings.storage_dir.resolve()
    ruta = (base / doc.ruta_archivo).resolve()
    # Defensa ante rutas manipuladas en la BD: el archivo debe estar dentro de storage/
    if not ruta.is_relative_to(base) or not ruta.is_file():
        raise HTTPException(404, "El archivo de este documento no está disponible")

    db.add(Descarga(usuario_id=usuario.id, documento_id=doc.id,
                    ip=request.client.host if request.client else None))
    db.commit()
    return FileResponse(ruta, media_type="application/pdf", filename=doc.nombre_original)
