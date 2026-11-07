"""Configuración del cliente. En cada equipo cliente se define la dirección
del servidor dentro de la red Tailscale, p. ej.:

    REPO_API_URL=http://repositorio-unexpo:8000     (nombre MagicDNS)
    REPO_API_URL=http://100.101.102.103:8000        (IP Tailscale)
"""
import os

API_URL = os.getenv("REPO_API_URL", "http://127.0.0.1:8000").rstrip("/")
TIEMPO_ESPERA_S = 10

NOMBRE_APP = "Repositorio Digital"
SUBTITULO_APP = "Ingeniería Electrónica · UNEXPO"
