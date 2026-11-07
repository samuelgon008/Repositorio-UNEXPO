"""Prepara la base de datos: crea las tablas que falten y sincroniza roles,
permisos y catálogos con app/core/catalogos.py. Es idempotente y se ejecuta
al arrancar el servidor, así una BD existente se actualiza sola."""
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.catalogos import ETIQUETAS, PERMISOS, ROL_POR_DEFECTO, ROLES, TIPOS_DOCUMENTO
from app.database import Base, SessionLocal, engine
from app.models import Etiqueta, Permiso, Rol, TipoDocumento, Usuario

# Roles de versiones anteriores que se convierten en uno actual (conservan id y usuarios)
RENOMBRAR = {"bibliotecario": "docente"}


def sincronizar_catalogos(db: Session) -> None:
    # 1. Permisos: crear o actualizar
    permisos = {p.codigo: p for p in db.scalars(select(Permiso))}
    for codigo, descripcion in PERMISOS.items():
        p = permisos.get(codigo) or Permiso(codigo=codigo)
        p.descripcion = descripcion
        permisos[codigo] = p
        db.add(p)
    db.flush()

    # 2. Roles: renombrar los antiguos, crear o actualizar los actuales
    roles = {r.nombre: r for r in db.scalars(select(Rol))}
    for viejo, nuevo in RENOMBRAR.items():
        if viejo in roles and nuevo not in roles:
            roles[nuevo] = roles.pop(viejo)
            roles[nuevo].nombre = nuevo
    for nombre, (nivel, descripcion, codigos) in ROLES.items():
        r = roles.get(nombre) or Rol(nombre=nombre)
        r.nivel, r.descripcion = nivel, descripcion
        r.permisos = [permisos[c] for c in codigos]
        roles[nombre] = r
        db.add(r)
    db.flush()

    # 3. Roles obsoletos: sus usuarios pasan al rol por defecto
    por_defecto = roles[ROL_POR_DEFECTO]
    for nombre, r in list(roles.items()):
        if nombre not in ROLES:
            db.execute(update(Usuario).where(Usuario.rol_id == r.id).values(rol_id=por_defecto.id))
            db.delete(r)

    # 4. Permisos obsoletos
    for codigo, p in permisos.items():
        if codigo not in PERMISOS:
            db.delete(p)

    # 5. Tipos de documento y etiquetas que falten
    tipos = set(db.scalars(select(TipoDocumento.codigo)))
    db.add_all(TipoDocumento(codigo=c, nombre=n) for c, n in TIPOS_DOCUMENTO if c not in tipos)
    etiquetas = set(db.scalars(select(Etiqueta.nombre)))
    db.add_all(Etiqueta(nombre=e) for e in ETIQUETAS if e not in etiquetas)
    db.commit()


def preparar_base_de_datos() -> None:
    Base.metadata.create_all(engine)  # sólo crea las tablas que no existen
    with SessionLocal() as db:
        sincronizar_catalogos(db)
