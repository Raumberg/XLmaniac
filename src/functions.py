import flet as ft
import logging as lg
import os
import requests
import pathlib

from logics.entities.program import program

def clear_logs(e):
    e.page.show_snack_bar(ft.SnackBar(ft.Text("Clearing logs...")))
    with open('assets/app.log', 'w') as f:
        pass

def close_dialog(e):
    e.page.dialog.open = False
    e.page.update()

def upload_files(e: ft.FilePickerResultEvent):
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
        
        recent_upload_text.value = e.files[-1].name
        recent_upload_text.update()

    e.page.show_snack_bar(ft.SnackBar(ft.Text("Files uploaded.")))

def d_upload_files(e: ft.FilePickerResultEvent) -> str:
    path = e.files[0].path
    lg.info(f"[Flet] __Call__ fn upload :: selected path: {path}")
    if os.path.exists(path):
        lg.info(f'[Flet] Path verified')
        program.input_path = path
        recent_upload_text.value = e.files[-1].name
    else:
        recent_upload_text.value = "Unable to find file"
    e.page.update()
    
def d_download_files(e: ft.FilePickerResultEvent) -> str:
    path = e.files[0].path
    lg.info(f"[Flet] __Call__ fn download :: selected path: {path}")
    if os.path.exists(path):
        lg.info("[Flet] Path verified")
        program.output_path = path
        recent_download_text.value = path
    else:
        recent_download_text.value = "Unable to verify folder"
    e.page.update()

def request_file(file_name):
    url = f"http://localhost:8080/assets/downloads/{file_name}"
    lg.info(f"[HTTP] Requesting file from: {url}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        lg.info("[HTTP] Request completed")
        return response.content
    else:
        lg.info("[HTTP] Requested status invariant")
        return None

def save_request_file(e):
    file_content = request_file("output.xlsx")
    if file_content is not None:
        with open('output.xlsx', 'wb') as file:
            file.write(file_content)
        lg.info('[Flet] Saved file to: output.xlsx')

def open_file_picker(e):
    file_picker.pick_files(allow_multiple=False)

def get_textfield_path(e):
    t.value = ""
    lg.info(f"[Flet] textfield value set to: {tb.value}")
    try:
        path = pathlib.Path(tb.value)
        if path.is_dir():
            program.output_path = tb.value
            t.value = f"Folder path set to: \n{tb.value}"
            lg.info("[Flet] Path verified")
            print(program.output_path)
        else:
            error_dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text("Invalid folder path", color=ft.colors.RED),
                actions=[
                    ft.TextButton("OK", on_click=close_dialog)
                ],
            )
            e.page.dialog = error_dialog
            error_dialog.open = True
    except Exception as err:
        error_dialog = ft.AlertDialog(
        title=ft.Text("Error"),
        content=ft.Text("Invalid folder path", color=ft.colors.RED),
        actions=[
            ft.TextButton("OK", on_click=close_dialog)
            ],
        )
        e.page.dialog = error_dialog
        error_dialog.open = True
    finally:
        e.page.update()

file_picker = ft.FilePicker(on_result=d_upload_files)
file_saver = ft.FilePicker(on_result=d_download_files)
file_list = ft.Text("")
selected_files = ft.Text()
save_filepath = ft.Text()
recent_upload_text = ft.TextField(value='', 
                                  color=ft.colors.BLUE, 
                                  read_only=True)
recent_download_text = ft.TextField(value='', 
                                  color=ft.colors.BLUE, 
                                  read_only=True)
t = ft.Text(color=ft.colors.BLUE, size=14, weight=ft.FontWeight.BOLD, italic=True)
tb = ft.TextField(label="Folder path:", hint_text="Enter folder path")