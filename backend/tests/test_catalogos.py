"""Roles y permisos: migración desde la versión anterior y coherencia con seed_mysql.sql."""
import re
from pathlib import Path

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from app.core.catalogos import PERMISOS, ROLES
from app.core.security import hashear_password
from app.database import Base
from app.models import EstadoUsuario, Permiso, Rol, Usuario
from app.services.catalogos import sincronizar_catalogos

SEED = Path(__file__).resolve().parents[2] / "database" / "seed_mysql.sql"


def test_migra_una_bd_de_la_version_anterior(tmp_path):
    motor = create_engine(f"sqlite:///{tmp_path / 'vieja.db'}")
    event.listen(motor, "connect", lambda c, _: c.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(motor)
    with Session(motor) as db:
        # Estado de la versión anterior: 4 roles y otros permisos
        viejo = Permiso(codigo="documento.subir", descripcion="obsoleto")
        roles = [Rol(id=i, nombre=n, nivel=i) for i, n in
                 enumerate(["administrador", "bibliotecario", "estudiante", "invitado"], start=1)]
        roles[1].permisos = [viejo]
        db.add_all(roles)
        for i, rol in enumerate([2, 4], start=1):
            db.add(Usuario(cedula=f"V-{i}", nombres="X", apellidos="Y", email=f"{i}@x", username=f"u{i}",
                           password_hash=hashear_password("Clave2026"), rol_id=rol, estado=EstadoUsuario.activo))
        db.commit()

        sincronizar_catalogos(db)
        sincronizar_catalogos(db)  # idempotente

        assert set(db.scalars(select(Rol.nombre))) == set(ROLES)
        assert set(db.scalars(select(Permiso.codigo))) == set(PERMISOS)
        u1 = db.scalar(select(Usuario).where(Usuario.username == "u1"))
        u2 = db.scalar(select(Usuario).where(Usuario.username == "u2"))
        assert u1.rol.nombre == "docente" and u1.rol_id == 2      # bibliotecario → docente (mismo id)
        assert u2.rol.nombre == "estudiante"                        # invitado → estudiante
        assert u1.codigos_permiso == sorted(ROLES["docente"][2])


def test_seed_mysql_coincide_con_catalogos():
    # Separa el archivo en sus INSERT: {"roles": "...", "permisos": "...", ...}
    bloques = dict(re.findall(r"INSERT INTO (\w+) .*?VALUES(.*?);", SEED.read_text(encoding="utf-8"), re.S))
    roles_sql = dict(re.findall(r"\((\d+), '(\w+)'", bloques["roles"]))          # id -> nombre
    permisos_sql = dict(re.findall(r"\((\d+), '([\w.]+)'", bloques["permisos"]))  # id -> código
    pares = re.findall(r"\((\d+),(\d+)\)", bloques["rol_permiso"])

    assert set(roles_sql.values()) == set(ROLES)
    assert set(permisos_sql.values()) == set(PERMISOS)
    for id_rol, nombre in roles_sql.items():
        esperados = set(ROLES[nombre][2])
        en_sql = {permisos_sql[p] for r, p in pares if r == id_rol}
        assert en_sql == esperados, nombre
