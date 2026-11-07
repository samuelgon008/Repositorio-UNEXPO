"""Punto de entrada del servidor.

Desarrollo:   uvicorn app.main:app --reload
Producción:   uvicorn app.main:app --host <IP-Tailscale-del-servidor> --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, documentos, solicitudes, usuarios
from app.services.catalogos import preparar_base_de_datos


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    # Al arrancar: crea las tablas nuevas y sincroniza roles/permisos.
    # Así una base de datos de una versión anterior se actualiza sola.
    preparar_base_de_datos()
    yield


app = FastAPI(
    title="Repositorio Digital - Ing. Electrónica UNEXPO",
    description="API de TEG e Informes de Entrenamiento Industrial",
    version="0.2.0",
    lifespan=ciclo_de_vida,
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(documentos.router)
app.include_router(solicitudes.router)


@app.get("/salud", tags=["Sistema"])
def salud():
    return {"estado": "ok"}
