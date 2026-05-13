"""
Project entrypoint.
"""

from src.app.simulation_app import (
    SimulationApp
)


def main():
    """
    Application entrypoint.
    """

    app = SimulationApp()

    app.run()


if __name__ == "__main__":

    main()