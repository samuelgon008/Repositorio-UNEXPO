"""Configuración central leída desde variables de entorno / archivo .env."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent  # .../backend


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # SQLite para pruebas; en producción:
    # mysql+pymysql://repo_app:CLAVE@127.0.0.1:3306/repositorio_unexpo?charset=utf8mb4
    database_url: str = f"sqlite:///{BASE_DIR / 'repositorio_dev.db'}"

    # Genérala con: python -c "import secrets; print(secrets.token_urlsafe(64))"
    jwt_secret: str = "CAMBIAR-ESTA-CLAVE-EN-PRODUCCION"
    jwt_algoritmo: str = "HS256"
    jwt_minutos_expiracion: int = 60

    max_intentos_fallidos: int = 5
    minutos_bloqueo: int = 15

    storage_dir: Path = BASE_DIR / "storage" / "documentos"


settings = Settings()
