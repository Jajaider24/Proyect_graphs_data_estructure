"""
Report generator module - Simulation analytics.

This module contains utilities used to generate:
    - Traveler reports
    - Simulation statistics
    - Route analytics
    - Graph metrics

The generated reports are intended for:
    - Console visualization
    - Future Flet dashboards
    - Academic presentations
    - PDF export support
"""


def generate_traveler_report(solution):
    """
    Generate complete traveler simulation report.

    Args:
        solution (dict):
            Planning solution dictionary.

    Returns:
        dict:
            Structured traveler report.
    """

    # -----------------------------------------
    # BASIC METRICS
    # -----------------------------------------
    total_destinations = (solution["total_destinations"])
    total_flights = len(solution["flight_history"])
    total_jobs = len(solution["jobs_completed"])
    total_activities = len(solution["activities_completed"])

    # -----------------------------------------
    # FINANCIAL ANALYSIS
    # -----------------------------------------
    total_flight_cost = sum(flight["cost"] for flight in (solution["flight_history"]))
    total_job_earnings = sum(job["earnings"] for job in (solution["jobs_completed"]))

    # -----------------------------------------
    # TIME ANALYSIS
    # -----------------------------------------

    total_flight_time = sum(flight["time"] for flight in (solution["flight_history"]))

    # -----------------------------------------
    # AIRCRAFT ANALYSIS
    # -----------------------------------------
    aircraft_usage = {}

    for flight in (solution["flight_history"]):
        aircraft = (flight["aircraft"])
        aircraft_usage[aircraft] = aircraft_usage.get(aircraft, 0) + 1

    # Most used aircraft
    most_used_aircraft = None

    if aircraft_usage:
        most_used_aircraft = max(aircraft_usage,key=aircraft_usage.get)

    # -----------------------------------------
    # REPORT STRUCTURE
    # -----------------------------------------

    report = {
        "total_destinations": total_destinations,
        "total_flights": total_flights,
        "total_jobs": total_jobs,
        "total_activities": total_activities,
        "remaining_budget": solution["remaining_budget"],
        "remaining_time": solution["remaining_time"],
        "total_flight_cost": total_flight_cost,
        "total_job_earnings": total_job_earnings,
        "net_balance": total_job_earnings - total_flight_cost,
        "total_flight_time": total_flight_time,
        "most_used_aircraft": most_used_aircraft,
        "aircraft_usage": aircraft_usage,
        "visited_airports": solution["visited_airports"]
    }
    return report


def print_traveler_report(report):
    """
    Print formatted traveler report.

    Args:
        report (dict):
            Traveler report dictionary.
    """
    print("\n========================================")
    print(" TRAVELER REPORT")

    print("========================================\n")

    # -----------------------------------------
    # GENERAL METRICS
    # -----------------------------------------

    print("===== GENERAL METRICS =====\n")

    print(
        f"Visited Destinations: "
        f"{report['total_destinations']}"
    )

    print(
        f"Flights Taken: "
        f"{report['total_flights']}"
    )

    print(
        f"Activities Completed: "
        f"{report['total_activities']}"
    )

    print(
        f"Jobs Completed: "
        f"{report['total_jobs']}"
    )

    print()
    # -----------------------------------------
    # FINANCIAL ANALYSIS
    # -----------------------------------------

    print("===== FINANCIAL ANALYSIS =====\n")

    print(
        f"Flight Expenses: "
        f"${report['total_flight_cost']:.2f}"
    )

    print(
        f"Job Earnings: "
        f"${report['total_job_earnings']:.2f}"
    )

    print(
        f"Net Balance: "
        f"${report['net_balance']:.2f}"
    )

    print(
        f"Remaining Budget: "
        f"${report['remaining_budget']:.2f}"
    )

    print()

    # -----------------------------------------
    # TIME ANALYSIS
    # -----------------------------------------

    print("===== TIME ANALYSIS =====\n")

    print(
        f"Total Flight Time: "
        f"{report['total_flight_time']:.2f} min"
    )

    print(
        f"Remaining Time: "
        f"{report['remaining_time']:.2f} min"
    )

    print()

    # -----------------------------------------
    # AIRCRAFT ANALYSIS
    # -----------------------------------------

    print("===== AIRCRAFT ANALYSIS =====\n")

    print(
        f"Most Used Aircraft: "
        f"{report['most_used_aircraft']}"
    )

    print()

    for aircraft, usage in (report["aircraft_usage"].items()):
        print(
            f"{aircraft}: "
            f"{usage} flights"
        )
    print()

    # -----------------------------------------
    # ROUTE SUMMARY
    # -----------------------------------------

    print("===== ROUTE SUMMARY =====\n")

    print(" -> ".join(report["visited_airports"]))
    print()


def generate_graph_statistics(graph):
    """
    Generate global graph statistics.

    Args:
        graph:
            Graph object.

    Returns:
        dict:
            Graph analytics.
    """

    total_airports = (graph.total_airports())
    total_routes = (graph.total_routes())
    total_distance = 0
    aircraft_distribution = {}
    busiest_airport = None
    max_connections = 0

    # -----------------------------------------
    # ANALYZE GRAPH
    # -----------------------------------------

    for airport in (graph.get_all_airports()):
        connections = len(airport.routes)
        # Track busiest airport
        if connections > max_connections:
            max_connections = connections
            busiest_airport = airport.id
        # Analyze routes
        for route in airport.routes:
            total_distance += (route.distance_km)
            for aircraft in (route.aircraft_options):
                aircraft_distribution[aircraft.name] = (aircraft_distribution.get(aircraft.name, 0) + 1)

    # -----------------------------------------
    # AVERAGE DISTANCE
    # -----------------------------------------

    average_distance = 0
    if total_routes > 0:
        average_distance = (total_distance / total_routes)

    # -----------------------------------------
    # RETURN STATISTICS
    # -----------------------------------------

    return {
        "total_airports": total_airports,
        "total_routes": total_routes,
        "average_distance": average_distance,
        "busiest_airport": busiest_airport,
        "max_connections": max_connections,
        "aircraft_distribution": aircraft_distribution
    }


def print_graph_statistics(stats):
    """
    Print formatted graph statistics.

    Args:
        stats (dict):
            Graph statistics dictionary.
    """
    print("\n========================================")
    print(" GRAPH STATISTICS")
    print("========================================\n")
    print(
        f"Total Airports: "
        f"{stats['total_airports']}"
    )
    print(
        f"Total Routes: "
        f"{stats['total_routes']}"
    )
    print(
        f"Average Distance: "
        f"{stats['average_distance']:.2f} km"
    )
    print(
        f"Busiest Airport: "
        f"{stats['busiest_airport']}"
    )
    print(
        f"Maximum Connections: "
        f"{stats['max_connections']}"
    )
    print()
    print("===== AIRCRAFT DISTRIBUTION =====\n")

    for aircraft, amount in (stats["aircraft_distribution"].items()):
        print(
            f"{aircraft}: "
            f"{amount}"
        )
    print()