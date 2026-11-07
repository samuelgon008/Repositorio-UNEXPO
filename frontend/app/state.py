"""Estado de la sesión del usuario en el cliente."""
from dataclasses import dataclass, field

from app.services.api_client import ApiClient


@dataclass
class SesionApp:
    api: ApiClient = field(default_factory=ApiClient)
    usuario: dict | None = None

    @property
    def autenticado(self) -> bool:
        return self.usuario is not None

    def puede(self, permiso: str) -> bool:
        """Sólo decide qué botones mostrar; el servidor vuelve a verificar
        el permiso en cada petición."""
        return bool(self.usuario) and permiso in self.usuario["permisos"]

    def cerrar(self) -> None:
        self.api.cerrar_sesion()
        self.usuario = None
