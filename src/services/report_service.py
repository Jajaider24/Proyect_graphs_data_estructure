"""
Report service layer.

This service centralizes:
    - Traveler reports
    - Graph analytics
    - Simulation statistics
"""

from src.utils.report_generator import (

    generate_traveler_report,

    print_traveler_report,

    generate_graph_statistics,

    print_graph_statistics
)


class ReportService:
    """
    Analytics and reporting service.
    """

    def generate_graph_report(
        self,
        graph
    ):
        """
        Generate graph statistics.
        """

        stats = (
            generate_graph_statistics(
                graph
            )
        )

        print_graph_statistics(
            stats
        )

        return stats

    def generate_travel_report(
        self,
        solution
    ):
        """
        Generate traveler report.
        """

        report = (
            generate_traveler_report(
                solution
            )
        )

        print_traveler_report(
            report
        )

        return report