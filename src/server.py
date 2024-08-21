import flet as ft
from flet import *

import logging
import os

from styles import *
from functions import *
from instances import *
from basement import *
from statics import LOGFILE
from themes import LIGHT, DARK

os.environ['FLET_SECRET_KEY'] = 'secret'

def main(page: ft.Page) -> None:

    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.padding = 0
    page.bgcolor = colors.WHITE
    page.window_width = 1920
    page.window_height = 1080

    lg.info('Page initialized.')

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    stack,
                ],
            )
        )
        if page.route == "/dev":
            log_text = open(LOGFILE, 'r').readlines()
            log_entries = [ft.ListTile(title=ft.Text(line.rstrip()), leading=ft.Icon(ft.icons.INFO)) for line in log_text]
            page.views.append(
                ft.View(
                    "/dev",
                    [
                        ft.AppBar(title=ft.Text("Logs!"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ListView(expand=True, auto_scroll=True, controls=log_entries),
                        ft.ElevatedButton("Go back <-", on_click=lambda _: page.go("/"), height=40, width=120),
                    ],
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def switch_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme = DARK
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme = LIGHT
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()

    stack = ft.Stack(
        expand=True,
        controls=[
            ft.Column(
                alignment='center',
                horizontal_alignment='center',
                controls=[
                    ft.Row(
                        alignment='center',
                        controls=[
                            Body(page),
                            ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton("Show logs", on_click=lambda _: page.go("/dev"), height=40, width=120),
                            ft.Switch("Switch theme", on_change=switch_theme, value=False)
                        ]
                    ),
                ]
            )
        ],
    )


    page.theme_mode = ft.ThemeMode.LIGHT
    page.add(stack, )
    page.overlay.append(file_picker)
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.update()

if __name__ == '__main__':
    lg = logging.getLogger(__name__)
    logging.basicConfig(filename=LOGFILE, 
                        level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s'
                        )
    ft.app(target=main, 
            assets_dir='assets', 
            upload_dir='assets/uploads', 
            view=AppView.FLET_APP,
            use_color_emoji=True,
           )