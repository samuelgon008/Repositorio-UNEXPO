"""Motor SQLAlchemy y sesión por petición. Cambiar de SQLite a MySQL sólo
requiere modificar DATABASE_URL en el .env."""
from collections.abc import Generator

from sqlalchemy import BigInteger, Integer, SmallInteger, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

_es_sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if _es_sqlite else {},
)

if _es_sqlite:
    # SQLite no aplica claves foráneas a menos que se active por conexión.
    @event.listens_for(engine, "connect")
    def _activar_fk(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")


# SQLite sólo autoincrementa claves "INTEGER PRIMARY KEY"; en MySQL se
# conservan los tipos compactos (SMALLINT/BIGINT) del esquema.
SmallId = SmallInteger().with_variant(Integer, "sqlite")
BigId = BigInteger().with_variant(Integer, "sqlite")

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
