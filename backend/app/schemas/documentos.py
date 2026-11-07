"""Contratos de salida del módulo de documentos."""
from datetime import date

from pydantic import BaseModel

from app.models import Documento, Participacion


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

    @classmethod
    def desde_modelo(cls, d: Documento) -> "DocumentoOut":
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
            nombre_archivo=d.nombre_original, tamano_bytes=d.tamano_bytes,
        )
