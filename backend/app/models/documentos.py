"""Documentos y sus metadatos normalizados (personas, etiquetas, palabras clave)."""
import enum
from datetime import date, datetime

from sqlalchemy import (
    BigInteger, Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer,
    SmallInteger, String, Table, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, SmallId

documento_etiqueta = Table(
    "documento_etiqueta",
    Base.metadata,
    Column("documento_id", ForeignKey("documentos.id", ondelete="CASCADE"), primary_key=True),
    Column("etiqueta_id", ForeignKey("etiquetas.id"), primary_key=True),
)

documento_palabra_clave = Table(
    "documento_palabra_clave",
    Base.metadata,
    Column("documento_id", ForeignKey("documentos.id", ondelete="CASCADE"), primary_key=True),
    Column("palabra_clave_id", ForeignKey("palabras_clave.id"), primary_key=True),
)


class Participacion(str, enum.Enum):
    autor = "autor"
    tutor_academico = "tutor_academico"
    tutor_industrial = "tutor_industrial"
    jurado = "jurado"


class TipoDocumento(Base):
    __tablename__ = "tipos_documento"

    id: Mapped[int] = mapped_column(SmallId, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(10), unique=True)
    nombre: Mapped[str] = mapped_column(String(80))


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(300))
    resumen: Mapped[str | None] = mapped_column(Text)
    tipo_id: Mapped[int] = mapped_column(ForeignKey("tipos_documento.id"))
    anio: Mapped[int] = mapped_column(SmallInteger, index=True)
    fecha_aprobacion: Mapped[date | None] = mapped_column(Date)
    empresa: Mapped[str | None] = mapped_column(String(150))
    ruta_archivo: Mapped[str] = mapped_column(String(255), unique=True)
    nombre_original: Mapped[str] = mapped_column(String(255))
    tamano_bytes: Mapped[int] = mapped_column(BigInteger)
    hash_sha256: Mapped[str] = mapped_column(String(64), unique=True)
    publicado: Mapped[bool] = mapped_column(Boolean, default=False)
    subido_por: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    tipo: Mapped[TipoDocumento] = relationship(lazy="joined")
    participantes: Mapped[list["DocumentoPersona"]] = relationship(
        back_populates="documento", cascade="all, delete-orphan"
    )
    etiquetas: Mapped[list["Etiqueta"]] = relationship(secondary=documento_etiqueta)
    palabras_clave: Mapped[list["PalabraClave"]] = relationship(secondary=documento_palabra_clave)


class Persona(Base):
    """Autores y tutores. Una misma persona puede tener distintos papeles
    en distintos documentos, por eso el papel vive en DocumentoPersona."""
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombres: Mapped[str] = mapped_column(String(80))
    apellidos: Mapped[str] = mapped_column(String(80), index=True)
    cedula: Mapped[str | None] = mapped_column(String(15), unique=True)
    email: Mapped[str | None] = mapped_column(String(120))
    institucion: Mapped[str | None] = mapped_column(String(150))


class DocumentoPersona(Base):
    __tablename__ = "documento_persona"

    documento_id: Mapped[int] = mapped_column(
        ForeignKey("documentos.id", ondelete="CASCADE"), primary_key=True
    )
    persona_id: Mapped[int] = mapped_column(ForeignKey("personas.id"), primary_key=True)
    participacion: Mapped[Participacion] = mapped_column(
        Enum(Participacion, name="participacion"), primary_key=True
    )
    orden: Mapped[int] = mapped_column(SmallInteger, default=1)

    documento: Mapped[Documento] = relationship(back_populates="participantes")
    persona: Mapped[Persona] = relationship(lazy="joined")


class Etiqueta(Base):
    __tablename__ = "etiquetas"

    id: Mapped[int] = mapped_column(SmallId, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True)


class PalabraClave(Base):
    __tablename__ = "palabras_clave"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    termino: Mapped[str] = mapped_column(String(80), unique=True)
