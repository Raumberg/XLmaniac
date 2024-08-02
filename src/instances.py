import flet as ft
import asyncio
import random

from styles import *

class ANM(ft.Container):
    def __init__(self) -> None:
        color: str = self.get_random_color()
        super(ANM, self).__init__(
            bgcolor=color, 
            left=self.get_random_pos(),
            top=self.get_random_pos(),
            width=2.5,
            height=2.5,
            opacity=0,
            shape=ft.BoxShape('circle'),
            offset=ft.transform.Offset(0, 0),
            shadow=ft.BoxShadow(
                spread_radius=20,
                blur_radius=100,
                color=color
            )
        )
        self.wait = self.get_random_wait()
        self.animate_opacity = ft.Animation(self.wait, 'ease')
        self.animate_offset = ft.Animation(self.wait, 'ease')

    async def anm_animate(self, event=None):
        self.opacity = 1
        self.offset = ft.transform.Offset(
            self.get_random_offset() ** 2.5,
            self.get_random_offset() ** 2.5
        )
        self.update()
        await asyncio.sleep(self.wait/1000)
        self.opacity = 1
        self.offset = ft.transform.Offset(
            self.get_random_offset() ** 2,
            self.get_random_offset() ** 2
        )
        self.update()

        await self.anm_animate()

    @staticmethod
    def get_random_pos():
        return random.randint(-100, 2000)

    @staticmethod
    def get_random_color():
        colors: list = ['blue', 'purple']
        return random.choice(colors)

    @staticmethod
    def get_random_offset():
        return random.randint(1, 7)

    @staticmethod
    def get_random_wait():
        return random.randrange(3000, 7000, 1000)

class DropDown(ft.Dropdown):
    def __init__(self, label: str) -> None:
        super().__init__(**dropdown_style, label=label)
        self.options = [
            ft.dropdown.Option('FASP'),
            ft.dropdown.Option('Money Man'),
            ft.dropdown.Option('MTS'),
            ft.dropdown.Option('Pochta'),
            ft.dropdown.Option('BGorod'),
            ft.dropdown.Option('Barville'),
            ft.dropdown.Option('MC Mobile'),
        ]

class Input(ft.TextField):
    def __init__(self, password: bool) -> None:
        super().__init__(**input_style, password=password)

class Button(ft.ElevatedButton):
    def __init__(self, text: str):
        super().__init__(**button_style, text=text)

class CheckBox(ft.Checkbox):
    def __init__(self):
        super().__init__(**checkbox_style)

class CheckBoxPH(ft.Checkbox):
    def __init__(self):
        super().__init__(**checkbox_ph_style)

class TField(ft.TextField):
    def __init__(self):
        super().__init__(**textfield_style)

