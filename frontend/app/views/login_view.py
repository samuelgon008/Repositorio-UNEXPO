"""Pantalla de inicio de sesión."""
from collections.abc import Callable

import flet as ft

from app.components.ui import COLOR_PRIMARIO, encabezado, mostrar_error, tarjeta, texto_error
from app.services.api_client import ApiError
from app.state import SesionApp


def login_view(page: ft.Page, sesion: SesionApp, navegar: Callable[[str], None]) -> ft.Control:
    usuario = ft.TextField(
        label="Usuario", prefix_icon=ft.Icons.PERSON_OUTLINE, autofocus=True,
        max_length=40, counter="",
    )
    clave = ft.TextField(
        label="Contraseña", prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True, can_reveal_password=True, max_length=128, counter="",
    )
    error = texto_error()
    cargando = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)
    boton = ft.Button(
        content="Ingresar", icon=ft.Icons.LOGIN, height=46,
        bgcolor=COLOR_PRIMARIO, color=ft.Colors.WHITE,
    )

    def campo_invalido() -> ft.TextField | None:
        """Marca los campos vacíos y devuelve el primero para darle el foco."""
        usuario.error = "Ingrese su usuario" if not usuario.value.strip() else None
        clave.error = "Ingrese su contraseña" if not clave.value else None
        return next((c for c in (usuario, clave) if c.error), None)

    def ocupado(estado: bool) -> None:
        # Sólo se bloquea el botón: deshabilitar los campos les quita el foco.
        boton.disabled = estado
        cargando.visible = estado
        page.update()

    async def iniciar_sesion(e):
        if boton.disabled:  # evita envíos dobles con Enter
            return
        await _iniciar_sesion()

    async def _iniciar_sesion():
        mostrar_error(error, None)
        if vacio := campo_invalido():
            page.update()
            await vacio.focus()
            return

        ocupado(True)
        try:
            sesion.usuario = await sesion.api.login(usuario.value.strip(), clave.value)
        except ApiError as e:
            mostrar_error(error, e.mensaje)
            clave.value = ""
            ocupado(False)
            await clave.focus()
            return

        ocupado(False)
        navegar("inicio")

    boton.on_click = iniciar_sesion
    usuario.on_submit = iniciar_sesion  # Enter en el teclado
    clave.on_submit = iniciar_sesion

    return tarjeta([
        encabezado(),
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        usuario,
        clave,
        error,
        boton,
        ft.Row([cargando], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("¿No tiene cuenta?", size=13),
                ft.TextButton(content="Regístrese aquí", on_click=lambda _: navegar("registro")),
            ],
        ),
    ])
