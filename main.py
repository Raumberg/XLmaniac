import flet as ft
from flet import *
import random
import asyncio

import pandas as pd
import os
import pandas as pd
import logging
from win10toast import ToastNotifier

from time import sleep

from app.logics import *
from app.pochta import *
from app.phones import *

def btn_clck(e):
    if CB.value:
        #lg.info(f"TextField value: {TF.value}")
        #columns = TF.value.upper().split(' ')
        #lg.info(f"Excel columns: {columns}")
        #macro.macro(text_value=columns) # execute macro
        lg.info("Executing pochta")
        execute_pochta()
    elif CB_PH.value:
        execute_phones()
        lg.info("Executing phones.")
    else:
        lg.info("Executing logics.")
        try:
            execute()
        except Exception as global_error:
            toast = ToastNotifier()
            toast.show_toast("ERROR!", global_error, duration=10)
    lg.info('Program completed.')

def show_logs(e):
    with open('app.log', 'r') as f:
        logs = f.read()
    ft.Page.dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text('Logs'),
        content=ft.Text(logs),
        actions=[
            ft.TextButton('Close', on_click=close_dialog),
            ft.TextButton('Clear', on_click=clear_logs),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Closed!"),
    )
    ft.Page.dialog.open = True
    ft.Page.update()

def clear_logs(e):
    with open('app.log', 'w') as f:
        pass

def close_dialog(e):
    ft.Page.dialog = None    

def upload_file(e):
    print('workin')
    file_picker = ft.FilePicker()
    file_picker.pick_files(allow_multiple=True)
    file_picker.on_result = lambda e: display_files(e.files)
    ft.Page.update()

def display_files(files):
    file_list.text = ", ".join([file.name for file in files])
    ft.Page.update()

def pick_files_result(e: ft.FilePickerResultEvent):
    selected_files.value = (
        ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!"
    )
    selected_files.update()

def get_random_pos():
    return random.randint(-100, 2000)

def get_random_color():
    colors: list = ['blue', 'purple']
    return random.choice(colors)

def get_random_offset():
    return random.randint(1, 7)

def get_random_wait():
    return random.randrange(3000, 7000, 1000)

# def dropdown_change(e):
#     t = ft.Text()
#     t.value = f"Dropdown changed to {.value}"

class ANM(ft.Container):
    def __init__(self) -> None:
        color: str = get_random_color()
        super(ANM, self).__init__(
            bgcolor=color, 
            left=get_random_pos(),
            top=get_random_pos(),
            width=2.5,
            height=2.5,
            opacity=0,
            shape=BoxShape('circle'),
            offset=ft.transform.Offset(0, 0),
            shadow=BoxShadow(
                spread_radius=20,
                blur_radius=100,
                color=color
            )
        )
        self.wait = get_random_wait()
        self.animate_opacity = ft.Animation(self.wait, 'ease')
        self.animate_offset = ft.Animation(self.wait, 'ease')

    async def anm_animate(self, event=None):
        self.opacity = 1
        self.offset = ft.transform.Offset(
            get_random_offset() ** 2.5,
            get_random_offset() ** 2.5
        )
        self.update()
        await asyncio.sleep(self.wait/1000)
        self.opacity = 1
        self.offset = ft.transform.Offset(
            get_random_offset() ** 2,
            get_random_offset() ** 2
        )
        self.update()

        await self.anm_animate()



input_style = {
    'height': 38,
    'focused_border_color': 'amber800',
    'border_radius': 5,  
    'cursor_height': 18,
    'cursor_color': 'white',
    'content_padding': 10,
    'border_width': 1.5,
    'text_size': 12,
    'bgcolor': colors.with_opacity(0.08, 'white70')
}

button_style = {
    'expand': True,
    'height': 65,
    'bgcolor': 'blue',
    'style': ft.ButtonStyle(shape={'': ft.RoundedRectangleBorder(radius=5)}),
    'color': 'white87',
    'on_click': btn_clck, 
}

body_style = {
    'width': 350,
    'height': 500,
    'padding': 20,
    'border_radius': 10,
    'bgcolor': ft.colors.with_opacity(0.045, colors.WHITE70), 
    'shadow': ft.BoxShadow(
        spread_radius=20,
        blur_radius=45,
        color=ft.colors.with_opacity(0.15, 'blue'),
    )
}

dropdown_style = {
    'width': 230,
    'height': 50,
    'bgcolor': 'black45',            
    'border_radius': 10,
    'icon': ft.Icon(name=icons.SETTINGS, color='black87'),
    'text_size': 17,
    'color': colors.BLACK87,
    'border_color': colors.BLUE,
    'focused_bgcolor': colors.BLUE,
#     'on_change': dropdown_change,
}

checkbox_style = {
    'label': 'Apply to Pochta Bank',
    'value': False
}

checkbox_ph_style = {
    'label': 'Format Phones',
    'value': False
}

textfield_style = {
    'label': '$Macro Rows',
    'hint_text': 'Please, enter rows to affect',
    'border_color': 'blue',
    'disabled': True
}

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

TF = TField()  

CB = CheckBox()
CB_PH = CheckBoxPH()

PR = ft.ProgressRing(width=20, height=20, stroke_width=3)

file_list = ft.Text("")
pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
selected_files = ft.Text()

class Body(ft.Container):
    def __init__(self) -> None:
        super().__init__(**body_style)
        self.name = Input(password=False)
        self.password = Input(password=True)
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                    ft.Text('FASP.cnv', size=30, color=colors.with_opacity(0.8, colors.BLUE), weight=ft.FontWeight.W_900, italic=False, text_align='center'),
                    ft.Icon(name='settings', size=50, color=colors.BLUE),
                    ]
                ),
                #ft.Row(
                #    controls=[
                #        DropDown('Client selection') # переменная 
                #        ]
                #    ),
                ft.Divider(height=8, color='blue', thickness=3),
                ft.Row(controls=[Button('Parse file')]),
                ft.Divider(height=8, color='blue', thickness=3),
                ft.Row(controls=[TF]),
                ft.Row(controls=[CB]),
                ft.Row(controls=[CB_PH]),
                ft.Divider(height=8, color='blue', thickness=3),
                ft.Row(controls=[
                    ft.ElevatedButton(
                        'Upload file',
                        on_click=lambda event: pick_files_dialog.pick_files(
                            allow_multiple=False
                        ),
                        height=40,
                        width=120,
                    ),
                    ft.ElevatedButton(
                        'Show Logs',
                        on_click=show_logs
                    ),
                    ft.Icon(name=ft.icons.EDIT_DOCUMENT, size=30),
                    ft.ElevatedButton(
                        'Clear Logs',
                        height=40,
                        width=120,
                        on_click=clear_logs
                    ),
                    ft.Text('Build: 0.8.1', size=20, color=colors.with_opacity(0.8, colors.BLUE_800), weight=ft.FontWeight.W_900, italic=False, text_align='right')
                ]),
            
            ]
        )

def main(page: ft.Page) -> None:
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'
    page.padding = 0
    page.bgcolor = colors.WHITE
    page.window_width = 600
    page.window_height = 600

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
    page.update()

    async def run():
        await asyncio.gather(
            *(item.anm_animate() for item in background.controls),
        )

    #asyncio.run(run())  # OFFED FOR LOGGING
    #lg.debug('page initialized')

if __name__ == '__main__':
    lg = logging.getLogger(__name__)
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    ft.app(main)