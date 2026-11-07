"""Inicializa la base de datos y crea el administrador.

    python database/init_db.py                 # crea tablas + catálogos (SQLite/MySQL)
    python database/init_db.py --crear-admin   # además pide datos del administrador
    python database/init_db.py --restablecer-password USUARIO   # olvidó la contraseña

Crea las tablas que falten y sincroniza roles, permisos y catálogos con
backend/app/core/catalogos.py (lo mismo hace el servidor al arrancar).
En MySQL también puede ejecutar schema_mysql.sql y seed_mysql.sql a mano.
Este script es idempotente y no duplica datos.
"""
import argparse
import getpass
import re
import sys
from pathlib import Path

DIR_DB = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR_DB.parent / "backend"))

from pydantic import ValidationError  # noqa: E402
from sqlalchemy import or_, select  # noqa: E402

from app.config import settings  # noqa: E402
from app.core.security import hashear_password  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models import EstadoUsuario, Rol, Usuario  # noqa: E402
from app.schemas.auth import RegistroIn  # noqa: E402
from app.services.catalogos import preparar_base_de_datos  # noqa: E402


def crear_esquema_y_catalogos() -> None:
    preparar_base_de_datos()
    print("✓ Tablas, roles (administrador, docente, estudiante), permisos y catálogos al día.")


def crear_admin() -> None:
    print("\n== Nuevo administrador ==")
    datos = {
        "cedula": input("Cédula (V-12345678): ").strip(),
        "nombres": input("Nombres: ").strip(),
        "apellidos": input("Apellidos: ").strip(),
        "email": input("Correo: ").strip(),
        "username": input("Usuario: ").strip(),
    }
    datos["password"] = pedir_password()

    # Mismas reglas que el registro desde la aplicación (normaliza la cédula, etc.)
    try:
        valido = RegistroIn(**datos)
    except ValidationError as e:
        for err in e.errors():
            print(f"✗ {err['loc'][-1]}: {err['msg'].removeprefix('Value error, ')}")
        sys.exit("No se creó el administrador. Corrija los datos y vuelva a intentarlo.")

    with SessionLocal() as db:
        if db.scalar(select(Usuario).where(or_(
            Usuario.username == valido.username,
            Usuario.email == valido.email,
            Usuario.cedula == valido.cedula,
        ))):
            sys.exit("✗ Ya existe un usuario con ese nombre de usuario, correo o cédula.")
        rol = db.scalar(select(Rol).where(Rol.nombre == "administrador"))
        db.add(Usuario(**valido.model_dump(exclude={"password"}),
                       password_hash=hashear_password(valido.password),
                       rol_id=rol.id, estado=EstadoUsuario.activo))
        db.commit()
    print(f"✓ Administrador '{valido.username}' (cédula {valido.cedula}) creado.")


def pedir_password(intentos: int = 3) -> str:
    print("\n  Por seguridad, la contraseña NO se muestra mientras la escribe")
    print("  (no aparecen letras ni asteriscos). Escríbala y presione Enter.")
    print("  Requisitos: mínimo 8 caracteres, con letras y números.\n")
    for _ in range(intentos):
        password = getpass.getpass("Contraseña: ")
        if not password:
            print("✗ No se escribió nada. Intente de nuevo.")
        elif len(password) < 8:
            print(f"✗ Tiene {len(password)} caracteres; se requieren al menos 8.")
        elif not (re.search(r"[A-Za-z]", password) and re.search(r"\d", password)):
            print("✗ Debe combinar letras y números.")
        elif password != getpass.getpass("Repita la contraseña: "):
            print("✗ Las dos contraseñas no coinciden.")
        else:
            return password
    sys.exit("No se guardó ningún cambio. Ejecute el comando otra vez.")


def restablecer_password(username: str) -> None:
    with SessionLocal() as db:
        usuario = db.scalar(select(Usuario).where(Usuario.username == username.strip().lower()))
        if usuario is None:
            print(f"✗ No existe el usuario '{username}'. Usuarios registrados:")
            for u in db.scalars(select(Usuario).order_by(Usuario.username)):
                print(f"   - {u.username}  ({u.nombres} {u.apellidos}, {u.rol.nombre}, {u.estado.value})")
            sys.exit(1)

        print(f"\nNueva contraseña para '{usuario.username}' ({usuario.nombres} {usuario.apellidos})")
        usuario.password_hash = hashear_password(pedir_password())
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None  # también lo desbloquea si estaba bloqueado
        db.commit()
    print(f"✓ Contraseña de '{usuario.username}' actualizada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--crear-admin", action="store_true")
    parser.add_argument("--restablecer-password", metavar="USUARIO",
                        help="cambia la contraseña de un usuario y lo desbloquea")
    args = parser.parse_args()

    print(f"Base de datos: {settings.database_url.split('@')[-1]}")
    crear_esquema_y_catalogos()
    if args.crear_admin:
        crear_admin()
    if args.restablecer_password:
        restablecer_password(args.restablecer_password)
