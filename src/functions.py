import flet as ft
import logging as lg
import os
import requests
import io

from statics import *

def clear_logs(e):
    e.page.show_snack_bar(ft.SnackBar(ft.Text("Clearing logs...")))
    with open('assets/app.log', 'w') as f:
        pass

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
        lg.info('[FLET] Saved file to: output.xlsx')

def open_file_picker(e):
    file_picker.pick_files(allow_multiple=False)

def open_file_saver(e):
    file_saver.save_file()

def delete_files(e):
    for file in os.listdir(uploads):
        file_path = os.path.join(uploads, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            lg.info(f'[FLET] deleted {file_path} by __Call__ fn delete_files')

    for file in os.listdir(downloads):
        file_path = os.path.join(downloads, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            lg.info(f'[FLET] deleted {file_path} by __Call__ fn delete_files')

    e.page.show_snack_bar(ft.SnackBar(ft.Text("Files deleted.")))

def download_file(e) -> None:
    try:
        lg.info("[Flet] __Call__ Download fn")
        file_name = r'output.xlsx'
        file_path = 'downloads/' + file_name
        e.page.launch_url(f"/{file_path}")
        e.page.show_snack_bar(ft.SnackBar(ft.Text("File upload successful.")))
    except Exception as e:
        e.page.show_snack_bar(ft.SnackBar(ft.Text('No files available for download.')))
        lg.info(e)

file_picker = ft.FilePicker(on_result=upload_files)
file_saver = ft.FilePicker(on_result=download_file)
file_list = ft.Text("")
selected_files = ft.Text()
save_filepath = ft.Text()
recent_upload_text = ft.TextField(value='', 
                                  color=ft.colors.BLUE, 
                                  read_only=True)