import flet as ft
import logging as lg
import os

from statics import *

def show_logs(e):
    log_file = 'app.log'
    try:
        if not os.path.exists(log_file):
            logs = 'Log file not found'
        else:
            with open(log_file, 'r') as f:
                logs = f.read()
    except Exception as ex:
        logs = f'Err reading log file: {str(ex)}'

    dialog = ft.AlertDialog(
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
    # ft.Page.controls.append(dialog)
    ft.Page.update()

def clear_logs(e):
    with open('app.log', 'w') as f:
        pass

def close_dialog(e):
    ft.Page.dialog = None    

def upload_files(e):
    lg.info("[Flet] __Call__ fn upload")
    upload_list = []
    if e.files is not None:
        for f in e.files:
            upload_list.append(
                ft.FilePickerUploadFile(
                    f.name,
                    upload_url=e.page.get_upload_url(file_name=f.name, expires=600),
                )
            )
        lg.info(f"[Flet] Uploaded files: {upload_list}")
        file_picker.upload(upload_list)

def open_file_picker(e):
    file_picker.pick_files()


def delete_files(e):
    for file in os.listdir(uploads):
        file_path = os.path.join(uploads, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            lg.info(f'[FLET] deleted {file_path} by __Call__ fn delete_files')

# def update_file_options():
#     global files
#     files = [f for f in os.listdir(uploads) if os.path.isfile(os.path.join(uploads, f))]
#     file_dropdown.options = [ft.dropdown.Option(file) for file in files]
#     file_dropdown.update()


file_picker = ft.FilePicker(on_result=upload_files)
file_list = ft.Text("")
selected_files = ft.Text()