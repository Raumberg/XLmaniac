import flet as ft

from styles import *
from functions import *
from instances import *


TF = TField()  
CB = CheckBox()
CB_PH = CheckBoxPH()
PR = ft.ProgressRing(width=20, height=20, stroke_width=3)

class Body(ft.Container):
    def __init__(self) -> None:
        super().__init__(**body_style)
        self.name = Input(password=False)
        self.password = Input(password=True)
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                    ft.Text('FASP.cnv', size=30, color=ft.colors.with_opacity(0.8, ft.colors.BLUE), weight=ft.FontWeight.W_900, italic=False, text_align='center'),
                    ft.Icon(name='settings', size=50, color=ft.colors.BLUE),
                    ]
                ),
                ft.Divider(height=8, color='blue', thickness=3),
                ft.Dropdown(
                    width=500,
                    label='Select a file',
                    options=[ft.dropdown.Option(file) for file in files]
                ),
                ft.Divider(height=8, color='blue', thickness=3),
                ft.Row(controls=[Button('Parse file')]),
                ft.Divider(height=8, color='blue', thickness=3),
                ft.Divider(height=8, color='transparent', thickness=3),
                # ft.Row(controls=[TF]),
                # ft.Row(controls=[CB]),
                # ft.Row(controls=[CB_PH]),
                ft.Row(controls=[
                    ft.Icon(name=ft.icons.CLOUD_UPLOAD, size=60),
                    ft.ElevatedButton(
                        'Upload',
                        on_click=open_file_picker,
                        height=60,
                        width=120,
                    ),
                    ft.ElevatedButton(
                        'Clear',
                        on_click=delete_files,
                        height=60,
                        width=120,
                    ),
                ]),
                ft.Divider(height=12, color='transparent', thickness=3),
                ft.Divider(height=8, color='blue', thickness=3),
                ft.Divider(height=8, color='transparent', thickness=3),
                ft.Row(controls=[
                    ft.Icon(name=ft.icons.EDIT_DOCUMENT, size=30),
                    ft.ElevatedButton(
                        'Show Logs',
                        on_click=show_logs,
                        height=40,
                        width=120,
                    ),
                    ft.ElevatedButton(
                        'Clear Logs',
                        height=40,
                        width=120,
                        on_click=clear_logs
                    ),
                ]),
                ft.Divider(height=270, color='transparent', thickness=3),
                ft.Text('Build: 0.9.1', size=20, color=ft.colors.with_opacity(0.8, ft.colors.BLUE_800), weight=ft.FontWeight.W_900, italic=False, text_align='center')
            
            ]
        )