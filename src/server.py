import flet as ft
from flet import *

import random
import asyncio
import logging
import os

from styles import *
from functions import *
from instances import *
from basement import *

os.environ['FLET_SECRET_KEY'] = 'secret'


def main(page: ft.Page) -> None:
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.padding = 0
    page.bgcolor = colors.WHITE
    page.window_width = 1200
    page.window_height = 1200

    lg.info('Page initialized.')

    background = Stack(
        expand=True,
        controls=[
            ANM() for _ in range(150)
        ],
    )

    stack = Stack(
        expand=True,
        controls=[
            background,
            ft.Column(
                alignment='center',
                horizontal_alignment='center',
                controls=[
                    ft.Row(
                        alignment='center',
                        controls=[Body(),]
                    )
                ]
            )
        ],
    )
    page.add(stack, )
    page.overlay.append(file_picker)
    page.update()

    async def run():
        await asyncio.gather(
            *(item.anm_animate() for item in background.controls),
        )

    #asyncio.run(run())

if __name__ == '__main__':
    lg = logging.getLogger(__name__)
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    ft.app(target=main, assets_dir='assets', upload_dir='assets/uploads')