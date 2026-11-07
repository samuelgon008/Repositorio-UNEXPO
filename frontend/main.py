"""Cliente de escritorio del Repositorio Digital.

    python main.py                 # ventana de escritorio
    flet run --web main.py         # misma app en el navegador
"""
import flet as ft

from app.state import SesionApp
from app.views.inicio_view import inicio_view
from app.views.login_view import login_view
from app.views.registro_view import registro_view

VISTAS = {"login": login_view, "registro": registro_view, "inicio": inicio_view}
REQUIEREN_SESION = {"inicio"}


def main(page: ft.Page):
    page.title = "Repositorio Digital · Ing. Electrónica UNEXPO"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_900)
    page.padding = 0
    page.window.min_width, page.window.min_height = 380, 600

    sesion = SesionApp()

    def navegar(nombre: str) -> None:
        if nombre in REQUIEREN_SESION and not sesion.autenticado:
            nombre = "login"
        page.controls.clear()
        page.add(VISTAS[nombre](page, sesion, navegar))

    navegar("login")


if __name__ == "__main__":
    ft.run(main)
