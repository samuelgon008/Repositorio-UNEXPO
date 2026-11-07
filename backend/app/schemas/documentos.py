"""Contratos de entrada/salida del módulo de documentos."""
from datetime import date

from pydantic import BaseModel, Field

from app.models import Documento, Participacion
from app.schemas.solicitudes import SolicitudBreve


class DocumentoOut(BaseModel):
    id: int
    titulo: str
    resumen: str | None
    tipo: str                  # "TEG" o "IEI"
    anio: int
    fecha: date                # fecha de aprobación (o de carga si no se registró)
    empresa: str | None
    autores: list[str]
    tutores: list[str]
    etiquetas: list[str]
    palabras_clave: list[str]
    nombre_archivo: str
    tamano_bytes: int
    publicado: bool
    # Lo que puede hacer QUIEN CONSULTA con esta tesis (ver services/acceso.py)
    puede_leer: bool = False
    puede_descargar: bool = False
    solicitud: SolicitudBreve | None = None   # última solicitud del estudiante, si hizo alguna

    @classmethod
    def desde_modelo(cls, d: Documento, **acceso) -> "DocumentoOut":
        def personas(*papeles: Participacion) -> list[str]:
            filas = sorted((p for p in d.participantes if p.participacion in papeles), key=lambda p: p.orden)
            return [f"{p.persona.nombres} {p.persona.apellidos}" for p in filas]

        return cls(
            id=d.id, titulo=d.titulo, resumen=d.resumen, tipo=d.tipo.codigo, anio=d.anio,
            fecha=d.fecha_aprobacion or d.creado_en.date(), empresa=d.empresa,
            autores=personas(Participacion.autor),
            tutores=personas(Participacion.tutor_academico, Participacion.tutor_industrial),
            etiquetas=[e.nombre for e in d.etiquetas],
            palabras_clave=[p.termino for p in d.palabras_clave],
            nombre_archivo=d.nombre_original, tamano_bytes=d.tamano_bytes, publicado=d.publicado,
            **acceso,
        )


class DocumentoEdicionIn(BaseModel):
    """Cambios que el administrador puede hacer (sólo se aplican los enviados)."""
    titulo: str | None = Field(default=None, min_length=5, max_length=300)
    resumen: str | None = Field(default=None, max_length=5000)
    publicado: bool | None = None
