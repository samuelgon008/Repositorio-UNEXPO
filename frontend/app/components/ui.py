"""Piezas visuales reutilizables."""
import flet as ft

from app.config import NOMBRE_APP, SUBTITULO_APP

COLOR_PRIMARIO = ft.Colors.BLUE_900


def encabezado() -> ft.Column:
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
        controls=[
            ft.Icon(ft.Icons.SCHOOL, size=56, color=COLOR_PRIMARIO),
            ft.Text(NOMBRE_APP, size=24, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO),
            ft.Text(SUBTITULO_APP, size=13, color=ft.Colors.GREY_700),
        ],
    )


def tarjeta(controles: list[ft.Control], ancho: int = 400) -> ft.Container:
    """Formulario centrado; se adapta al ancho de la ventana o del teléfono."""
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=16,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[ft.Card(
                elevation=4,
                content=ft.Container(
                    width=ancho,
                    padding=ft.Padding.symmetric(horizontal=28, vertical=24),
                    content=ft.Column(
                        controls=controles,
                        tight=True,
                        spacing=14,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    ),
                ),
            )],
        ),
    )


def texto_error() -> ft.Text:
    return ft.Text("", color=ft.Colors.RED_700, size=13, visible=False,
                   text_align=ft.TextAlign.CENTER)


def mostrar_error(control: ft.Text, mensaje: str | None) -> None:
    control.value = mensaje or ""
    control.visible = bool(mensaje)
