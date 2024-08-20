import flet as ft
from flet import *
from flet.fastapi import flet_fastapi
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import asyncio
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

from styles import *
from functions import *
from instances import *
from basement import *
from statics import downloads

os.environ['FLET_SECRET_KEY'] = 'secret'

# class ServerState:
#     instance = None

#     def __init__(self):
#         self.upload_path = None
#         self.download_path = None

#     def __call__(self):
#         self.logger.info('Server started')

#     @classmethod
#     def get_instance(cls):
#         if cls.instance is None:
#             cls.instance = cls()
#         return cls.instance

def main(page: ft.Page) -> None:

    # server_state = ServerState.get_instance()

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
            log_text = open('assets/app.log', 'r').readlines()
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

    stack = Stack(
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
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton("Show logs", on_click=lambda _: page.go("/dev"), height=40, width=120)
                        ]
                    )
                ]
            )
        ],
    )
    page.add(stack, )
    page.overlay.append(file_picker)
    page.overlay.append(file_saver)
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.update()

if __name__ == '__main__':
    logfile_path = 'assets/app.log'
    lg = logging.getLogger(__name__)
    logging.basicConfig(filename=logfile_path, 
                        level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s'
                        )
    ft.app(target=main, 
            assets_dir='assets', 
            upload_dir='assets/uploads', 
            view=AppView.FLET_APP,
            use_color_emoji=True,
           )