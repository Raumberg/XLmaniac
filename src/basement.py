import flet as ft

from styles import *
from functions import *
from instances import *


TF = TField()  
CB = CheckBox()
CB_PH = CheckBoxPH()
PR = ft.ProgressRing(width=20, height=20, stroke_width=3)

class Body(ft.Container):
    def __init__(self, page: ft.Page, **kwargs) -> None:
        super().__init__(**body_style)
        self.page = page
        self.name = Input(password=False)
        self.password = Input(password=True)
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                    ft.Text('FASP.cnv', 
                            size=30, 
                            color=ft.colors.with_opacity(0.8, ft.colors.BLUE), 
                            weight=ft.FontWeight.W_900, 
                            italic=False, 
                            text_align='center'),
                    ft.Icon(name='settings', 
                            size=50, 
                            color=ft.colors.BLUE),
                    ]
                ),
                ft.Divider(height=8, 
                           color='blue', 
                           thickness=3),
                ft.Row(controls=[
                    Button('Parse file')
                ]),
                ft.Divider(height=8, 
                           color='blue', 
                           thickness=3),
                ft.Divider(height=8, 
                           color='transparent', 
                           thickness=3),
                ft.Row(controls=[
                    ft.Icon(name=ft.icons.CLOUD_UPLOAD, 
                            size=60),
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
                ft.Divider(height=15, 
                           color='transparent', 
                           thickness=3),
                ft.Row(controls=[
                    ft.Text(value='Recent Upload: ', 
                            size=20, 
                            color=ft.colors.with_opacity(0.8, ft.colors.BLUE_800),
                            weight=ft.FontWeight.W_900, 
                            italic=False,
                            selectable=False),
                    recent_upload_text,
                ]),
                ft.Divider(height=12, 
                           color='transparent', 
                           thickness=3),
                ft.Divider(height=8, 
                           color='blue', 
                           thickness=3),
                ft.Divider(height=8, 
                           color='transparent', 
                           thickness=3),
                ft.Row(controls=[
                    ft.Icon(name=ft.icons.CLOUD_DOWNLOAD, size=60),
                    ft.ElevatedButton('Download', 
                            on_click=download_file,
                            height=60, 
                            width=120,)
                ]),
                ft.Divider(height=200, 
                           color='transparent', 
                           thickness=3),
                ft.Row(controls=[
                    ft.Icon(name=ft.icons.EDIT_DOCUMENT, size=30),
                    ft.ElevatedButton(
                        'Clear Logs',
                        height=40,
                        width=120,
                        on_click=clear_logs
                    ),
                ]),
                ft.Divider(height=10, 
                           color='transparent', 
                           thickness=3),
                ft.Text('Build: 1.0.0', 
                        size=20, 
                        color=ft.colors.with_opacity(0.8, ft.colors.BLUE_800), 
                        weight=ft.FontWeight.W_900, 
                        italic=False, 
                        text_align='center')
            ]
        )