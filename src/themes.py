import flet as ft

LIGHT = ft.Theme(
                color_scheme = ft.ColorScheme(
                surface=ft.colors.BLACK,
                on_surface=ft.colors.BLACK,
                primary=ft.colors.BLUE_GREY_500,
                on_primary=ft.colors.RED,
                background=ft.colors.BLACK,
                on_background=ft.colors.WHITE,
                )
            )

DARK = ft.Theme(
                color_scheme=ft.ColorScheme(
                surface=ft.colors.WHITE,
                on_surface=ft.colors.GREY_400,
                primary=ft.colors.LIGHT_BLUE_300,
                on_primary=ft.colors.LIGHT_BLUE_600,
                background=ft.colors.WHITE,
                on_background=ft.colors.BLACK,
                )
            )