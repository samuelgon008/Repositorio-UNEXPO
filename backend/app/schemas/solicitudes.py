"""Contratos del módulo de solicitudes de acceso."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models import SolicitudAcceso


class SolicitudIn(BaseModel):
    documento_id: int
    motivo: str | None = Field(default=None, max_length=500)


class ResolucionIn(BaseModel):
    nota: str | None = Field(default=None, max_length=300)  # mensaje opcional al estudiante


class SolicitudBreve(BaseModel):
    """Lo que ve el estudiante dentro de cada tarjeta de tesis."""
    id: int
    estado: str          # pendiente | aprobada | rechazada | revocada | vencida
    creada_en: datetime
    vence_en: datetime | None
    nota_admin: str | None

    @classmethod
    def desde_modelo(cls, s: SolicitudAcceso, ahora: datetime) -> "SolicitudBreve":
        return cls(id=s.id, estado=s.estado_visible(ahora), creada_en=s.creada_en,
                   vence_en=s.vence_en, nota_admin=s.nota_admin)


class SolicitudOut(SolicitudBreve):
    """Vista completa (lista del estudiante y panel del administrador)."""
    motivo: str | None
    resuelta_en: datetime | None
    documento_id: int
    documento_titulo: str
    usuario_id: int
    usuario_nombre: str
    usuario_username: str
    usuario_cedula: str

    @classmethod
    def desde_modelo(cls, s: SolicitudAcceso, ahora: datetime) -> "SolicitudOut":
        return cls(
            **SolicitudBreve.desde_modelo(s, ahora).model_dump(),
            motivo=s.motivo, resuelta_en=s.resuelta_en,
            documento_id=s.documento_id, documento_titulo=s.documento.titulo,
            usuario_id=s.usuario_id, usuario_nombre=f"{s.usuario.nombres} {s.usuario.apellidos}",
            usuario_username=s.usuario.username, usuario_cedula=s.usuario.cedula,
        )
