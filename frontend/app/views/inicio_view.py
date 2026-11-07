"""Panel principal tras iniciar sesión. Los módulos se habilitan según los
permisos del rol (los módulos en sí se implementarán en la siguiente fase)."""
from collections.abc import Callable

import flet as ft

from app.components.ui import COLOR_PRIMARIO
from app.state import SesionApp

MODULOS = [
    # (permiso requerido, ícono, título, descripción)
    ("documento.ver", ft.Icons.SEARCH, "Buscar documentos", "Consultar TEG e informes"),
    ("documento.descargar", ft.Icons.DOWNLOAD, "Descargas", "Descargar archivos PDF"),
    ("documento.subir", ft.Icons.UPLOAD_FILE, "Cargar documento", "Subir y clasificar"),
    ("usuario.gestionar", ft.Icons.MANAGE_ACCOUNTS, "Usuarios", "Aprobar y asignar roles"),
    ("auditoria.ver", ft.Icons.HISTORY, "Auditoría", "Accesos y descargas"),
]


def inicio_view(page: ft.Page, sesion: SesionApp, navegar: Callable[[str], None]) -> ft.Control:
    u = sesion.usuario

    def cerrar_sesion(_):
        sesion.cerrar()
        navegar("login")

    def tarjeta_modulo(permiso, icono, titulo, descripcion) -> ft.Container:
        habilitado = sesion.puede(permiso)
        return ft.Container(
            col={"xs": 12, "sm": 6, "md": 4},
            opacity=1.0 if habilitado else 0.4,
            tooltip=None if habilitado else "Su rol no tiene acceso a este módulo",
            content=ft.Card(content=ft.ListTile(
                leading=ft.Icon(icono, color=COLOR_PRIMARIO),
                title=ft.Text(titulo, weight=ft.FontWeight.W_600),
                subtitle=ft.Text(descripcion),
                disabled=not habilitado,
                on_click=lambda _: page.show_dialog(
                    ft.SnackBar(ft.Text(f"Módulo «{titulo}»: próximamente"))),
            )),
        )

    barra = ft.Container(
        bgcolor=COLOR_PRIMARIO,
        padding=ft.Padding.symmetric(horizontal=16, vertical=10),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row([ft.Icon(ft.Icons.SCHOOL, color=ft.Colors.WHITE),
                        ft.Text("Repositorio Digital", color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD, size=16)]),
                ft.IconButton(ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE,
                              tooltip="Cerrar sesión", on_click=cerrar_sesion),
            ],
        ),
    )

    return ft.Column(
        expand=True,
        spacing=0,
        controls=[
            barra,
            ft.Container(
                expand=True,
                padding=16,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text(f"Bienvenido(a), {u['nombres']} {u['apellidos']}",
                                size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Rol: {u['rol'].capitalize()}", color=ft.Colors.GREY_700),
                        ft.ResponsiveRow([tarjeta_modulo(*m) for m in MODULOS]),
                    ],
                ),
            ),
        ],
    )
