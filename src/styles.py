import flet as ft
import logging as lg

from logics import entry

def btn_clck(e):
    lg.info("Executing logics.")
    try:
        entry.execute()
    except Exception as global_error:
        lg.error(f"Err in button's core. {global_error}")
    lg.info('Program completed.')

input_style = {
    'height': 38,
    'focused_border_color': 'amber800',
    'border_radius': 5,  
    'cursor_height': 18,
    'cursor_color': 'white',
    'content_padding': 10,
    'border_width': 1.5,
    'text_size': 12,
    'bgcolor': ft.colors.with_opacity(0.08, 'white70')
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
    'width': 500,
    'height': 800,
    'padding': 20,
    'border_radius': 10,
    'bgcolor': ft.colors.with_opacity(0.045, ft.colors.WHITE70), 
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
    'icon': ft.Icon(name=ft.icons.SETTINGS, color='black87'),
    'text_size': 17,
    'color': ft.colors.BLACK87,
    'border_color': ft.colors.BLUE,
    'focused_bgcolor': ft.colors.BLUE,
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