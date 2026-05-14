"""
Main Flet window.

This module handles:
    - User interface
    - Inputs
    - Result visualization
"""

import flet as ft

from src.app.simulation_app import (
    SimulationApp
)


class MainWindow:
    """
    Main application window.
    """

    def __init__(self):

        # Backend application
        self.app = (
            SimulationApp()
        )

    def start(
        self,
        page: ft.Page
    ):
        """
        Initialize UI.
        """

        # -----------------------------------------
        # PAGE CONFIGURATION
        # -----------------------------------------

        page.title = (
            "Airline Graph Simulator"
        )

        page.window_width = 1000
        page.window_height = 700

        page.padding = 20

        page.scroll = "auto"

        # -----------------------------------------
        # INPUTS
        # -----------------------------------------

        origin_input = ft.TextField(

            label="Origin Airport",

            value="BOG",

            width=200
        )

        destination_input = ft.TextField(

            label="Destination Airport",

            value="MEX",

            width=200
        )

        criterion_dropdown = ft.Dropdown(

            label="Optimization Criterion",

            width=250,

            value="cost",

            options=[

                ft.dropdown.Option(
                    "distance"
                ),

                ft.dropdown.Option(
                    "cost"
                ),

                ft.dropdown.Option(
                    "time"
                )
            ]
        )

        # -----------------------------------------
        # RESULTS AREA
        # -----------------------------------------

        results_text = ft.Text(

            value="Simulation results will appear here.",

            selectable=True,

            size=16
        )

        # -----------------------------------------
        # RUN DIJKSTRA
        # -----------------------------------------

        def run_dijkstra(event):

            graph = (
                self.app.graph_service
                .load_graph(
                    "data/sample_network.json"
                )
            )

            result = (
                self.app.simulation_service
                .run_dijkstra(

                    graph,

                    origin_input.value,

                    destination_input.value,

                    criterion_dropdown.value
                )
            )

            distances, predecessors, path = result

            results_text.value = (

                f"Optimal Path:\n\n"

                f"{' -> '.join(path)}"
            )

            page.update()

        # -----------------------------------------
        # BUTTONS
        # -----------------------------------------

        run_button = ft.ElevatedButton(

            content=ft.Text(
                "Run Dijkstra"
            ),

            on_click=run_dijkstra
        )

        # -----------------------------------------
        # LAYOUT
        # -----------------------------------------

        page.add(

            ft.Text(

                "AIRLINE GRAPH SIMULATOR",

                size=28,

                weight="bold"
            ),

            ft.Divider(),

            ft.Row([

                origin_input,

                destination_input,

                criterion_dropdown
            ]),

            run_button,

            ft.Divider(),

            results_text
        )