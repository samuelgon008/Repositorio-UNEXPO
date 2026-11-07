"""Punto de entrada del servidor.

Desarrollo:   uvicorn app.main:app --reload
Producción:   uvicorn app.main:app --host <IP-Tailscale-del-servidor> --port 8000
"""
from fastapi import FastAPI

from app.api.routes import auth, documentos, usuarios

app = FastAPI(
    title="Repositorio Digital - Ing. Electrónica UNEXPO",
    description="API de TEG e Informes de Entrenamiento Industrial",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(documentos.router)


@app.get("/salud", tags=["Sistema"])
def salud():
    return {"estado": "ok"}
