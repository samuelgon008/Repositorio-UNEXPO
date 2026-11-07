"""Bitácoras de inicio de sesión y descargas."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, BigId


class RegistroAcceso(Base):
    __tablename__ = "registro_accesos"

    id: Mapped[int] = mapped_column(BigId, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"))
    username: Mapped[str] = mapped_column(String(40))
    exitoso: Mapped[bool] = mapped_column(Boolean)
    motivo: Mapped[str | None] = mapped_column(String(60))
    ip: Mapped[str | None] = mapped_column(String(45))
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class Descarga(Base):
    __tablename__ = "descargas"

    id: Mapped[int] = mapped_column(BigId, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    documento_id: Mapped[int] = mapped_column(
        ForeignKey("documentos.id", ondelete="CASCADE"), index=True
    )
    ip: Mapped[str | None] = mapped_column(String(45))
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
