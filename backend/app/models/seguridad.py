"""Usuarios, roles y permisos (RBAC)."""
import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, SmallInteger, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, SmallId

rol_permiso = Table(
    "rol_permiso",
    Base.metadata,
    Column("rol_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True),
)


class EstadoUsuario(str, enum.Enum):
    pendiente = "pendiente"
    activo = "activo"
    suspendido = "suspendido"


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(SmallId, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))
    nivel: Mapped[int] = mapped_column(SmallInteger)

    permisos: Mapped[list["Permiso"]] = relationship(secondary=rol_permiso, lazy="selectin")


class Permiso(Base):
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(SmallId, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cedula: Mapped[str] = mapped_column(String(15), unique=True)
    nombres: Mapped[str] = mapped_column(String(80))
    apellidos: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    username: Mapped[str] = mapped_column(String(40), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    estado: Mapped[EstadoUsuario] = mapped_column(
        Enum(EstadoUsuario, name="estado_usuario"), default=EstadoUsuario.pendiente
    )
    intentos_fallidos: Mapped[int] = mapped_column(SmallInteger, default=0)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime)
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime)
    aprobado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"))
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    rol: Mapped[Rol] = relationship(lazy="joined")

    @property
    def codigos_permiso(self) -> list[str]:
        return sorted(p.codigo for p in self.rol.permisos)
