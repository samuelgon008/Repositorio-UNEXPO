"""Cliente HTTP asíncrono hacia el backend. La interfaz nunca toca la base de
datos directamente: toda validación de credenciales ocurre en el servidor."""
import httpx

from app.config import API_URL, TIEMPO_ESPERA_S


class ApiError(Exception):
    def __init__(self, mensaje: str, status_code: int | None = None):
        self.mensaje = mensaje
        self.status_code = status_code
        super().__init__(mensaje)


def _mensaje_de_error(r: httpx.Response) -> str:
    try:
        detalle = r.json().get("detail")
    except ValueError:
        return f"Error del servidor ({r.status_code})"
    if isinstance(detalle, list) and detalle:  # errores de validación 422
        campo = detalle[0].get("loc", ["", ""])[-1]
        msg = detalle[0].get("msg", "dato inválido").removeprefix("Value error, ")
        return f"{campo}: {msg}"
    return detalle or f"Error del servidor ({r.status_code})"


class ApiClient:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.token: str | None = None

    async def _peticion(self, metodo: str, ruta: str, **kwargs) -> dict:
        cabeceras = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=TIEMPO_ESPERA_S) as c:
                r = await c.request(metodo, ruta, headers=cabeceras, **kwargs)
        except httpx.RequestError:
            raise ApiError("No se pudo conectar con el servidor. "
                           "Verifique su conexión a Internet y que Tailscale esté activo.")
        if r.is_error:
            raise ApiError(_mensaje_de_error(r), r.status_code)
        return r.json()

    async def login(self, username: str, password: str) -> dict:
        datos = await self._peticion("POST", "/auth/login",
                                     json={"username": username, "password": password})
        self.token = datos["access_token"]
        return datos["usuario"]

    async def registro(self, datos: dict) -> str:
        return (await self._peticion("POST", "/auth/registro", json=datos))["detail"]

    def cerrar_sesion(self) -> None:
        self.token = None
