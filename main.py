"""
Main project entry point.
"""

import flet as ft

from src.ui.main_window import (
    MainWindow
)


def main(page: ft.Page):
    """
    Flet entrypoint.
    """

    window = MainWindow()

    window.start(page)


if __name__ == "__main__":

    ft.run(main)