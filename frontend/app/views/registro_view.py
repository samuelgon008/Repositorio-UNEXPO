"""Pantalla de registro. La cuenta queda pendiente de aprobación."""
from collections.abc import Callable

import flet as ft

from app.components.ui import COLOR_PRIMARIO, mostrar_error, tarjeta, texto_error
from app.services.api_client import ApiError
from app.state import SesionApp


def registro_view(page: ft.Page, sesion: SesionApp, navegar: Callable[[str], None]) -> ft.Control:
    campos = {
        "cedula": ft.TextField(label="Cédula (V-12345678)", prefix_icon=ft.Icons.BADGE_OUTLINED),
        "nombres": ft.TextField(label="Nombres", capitalization=ft.TextCapitalization.WORDS),
        "apellidos": ft.TextField(label="Apellidos", capitalization=ft.TextCapitalization.WORDS),
        "email": ft.TextField(label="Correo electrónico", prefix_icon=ft.Icons.EMAIL_OUTLINED,
                              keyboard_type=ft.KeyboardType.EMAIL),
        "username": ft.TextField(label="Usuario", prefix_icon=ft.Icons.PERSON_OUTLINE),
        "password": ft.TextField(label="Contraseña (mín. 8, letras y números)",
                                 password=True, can_reveal_password=True),
    }
    confirmar = ft.TextField(label="Repita la contraseña", password=True, can_reveal_password=True)
    error = texto_error()
    boton = ft.Button(content="Crear cuenta", icon=ft.Icons.PERSON_ADD, height=46,
                      bgcolor=COLOR_PRIMARIO, color=ft.Colors.WHITE)

    def validar() -> bool:
        ok = True
        for campo in (*campos.values(), confirmar):
            campo.error = None
            if not campo.value.strip():
                campo.error, ok = "Campo obligatorio", False
        if ok and campos["password"].value != confirmar.value:
            confirmar.error, ok = "Las contraseñas no coinciden", False
        return ok

    async def enviar(_):
        mostrar_error(error, None)
        if not validar():
            page.update()
            return
        boton.disabled = True
        page.update()
        try:
            mensaje = await sesion.api.registro({k: c.value.strip() if k != "password" else c.value
                                                 for k, c in campos.items()})
        except ApiError as e:
            mostrar_error(error, e.mensaje)
            boton.disabled = False
            page.update()
            return

        page.show_dialog(ft.SnackBar(ft.Text(mensaje), duration=6000))
        navegar("login")

    boton.on_click = enviar

    return tarjeta([
        ft.Text("Solicitud de registro", size=20, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO),
        ft.Text("Su cuenta será revisada por un administrador antes de poder ingresar.",
                size=12, color=ft.Colors.GREY_700),
        *campos.values(),
        confirmar,
        error,
        boton,
        ft.TextButton(content="Volver al inicio de sesión", on_click=lambda _: navegar("login")),
    ], ancho=440)
