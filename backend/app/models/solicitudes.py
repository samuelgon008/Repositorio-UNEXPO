"""Solicitudes de acceso: un estudiante pide leer/descargar una tesis concreta
y el administrador la aprueba (con vencimiento), la rechaza o la revoca."""
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.documentos import Documento
from app.models.seguridad import Usuario


class EstadoSolicitud(str, enum.Enum):
    pendiente = "pendiente"
    aprobada = "aprobada"
    rechazada = "rechazada"
    revocada = "revocada"


class SolicitudAcceso(Base):
    __tablename__ = "solicitudes_acceso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id", ondelete="CASCADE"), index=True)
    motivo: Mapped[str | None] = mapped_column(String(500))
    estado: Mapped[EstadoSolicitud] = mapped_column(
        Enum(EstadoSolicitud, name="estado_solicitud"), default=EstadoSolicitud.pendiente, index=True
    )
    nota_admin: Mapped[str | None] = mapped_column(String(300))
    creada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    resuelta_en: Mapped[datetime | None] = mapped_column(DateTime)
    resuelta_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"))
    vence_en: Mapped[datetime | None] = mapped_column(DateTime)

    usuario: Mapped[Usuario] = relationship(foreign_keys=[usuario_id], lazy="joined")
    documento: Mapped[Documento] = relationship(lazy="joined")

    def vigente(self, ahora: datetime) -> bool:
        """Aprobada y todavía no vencida: da acceso al PDF."""
        return self.estado == EstadoSolicitud.aprobada and self.vence_en is not None and self.vence_en > ahora

    def estado_visible(self, ahora: datetime) -> str:
        """Estado para mostrar: una aprobada cuyo plazo pasó se informa como "vencida"."""
        if self.estado == EstadoSolicitud.aprobada and not self.vigente(ahora):
            return "vencida"
        return self.estado.value
