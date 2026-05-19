"""
Dynamic planning algorithms - Advanced itinerary simulation.

This module contains dynamic simulation systems used for:
    - Budget recovery through jobs
    - Activity scheduling
    - Dynamic traveler decisions
    - Airport stop management
"""


def job_recommendation_engine(
    airport,
    traveler,
    available_hours
):
    """
    Recommend jobs when the traveler budget
    falls below the minimum threshold.

    According to project rules:
        Jobs become available when remaining
        budget <= 35% of initial budget.

    Args:
        airport:
            Current airport object.

        traveler:
            Traveler object.

        available_hours (int):
            Maximum work hours available.

    Returns:
        dict:
            Job recommendation result.
    """

    # -----------------------------------------
    # CHECK BUDGET THRESHOLD
    # -----------------------------------------

    if not traveler.budget_threshold_reached():

        return {

            "worked": False,

            "reason":
                "Budget threshold not reached.",

            "earnings": 0
        }

    # -----------------------------------------
    # CHECK AVAILABLE JOBS
    # -----------------------------------------

    if not airport.trabajos:

        return {

            "worked": False,

            "reason":
                "No jobs available at airport.",

            "earnings": 0
        }

    # -----------------------------------------
    # FIND BEST JOB
    # -----------------------------------------

    best_job = None

    best_earnings = 0

    best_hours = 0

    for job in airport.trabajos:

        # Maximum hours allowed
        workable_hours = min(

            available_hours,

            job["maxHoras"]
        )

        # Calculate earnings
        earnings = (
            workable_hours
            * job["tarifaHora"]
        )

        if earnings > best_earnings:

            best_earnings = earnings

            best_job = job

            best_hours = workable_hours

    # -----------------------------------------
    # APPLY JOB TO TRAVELER
    # -----------------------------------------

    traveler.earn_money(
        best_earnings
    )

    traveler.consume_time(
        best_hours * 60
    )

    traveler.jobs_done.append({

        "airport": airport.id,

        "job_name":
            best_job["nombre"],

        "hours":
            best_hours,

        "earnings":
            best_earnings
    })

    # -----------------------------------------
    # RETURN RESULT
    # -----------------------------------------

    return {

        "worked": True,

        "airport": airport.id,

        "job_name":
            best_job["nombre"],

        "hours":
            best_hours,

        "earnings":
            best_earnings,

        "remaining_budget":
            traveler.current_budget,

        "remaining_time":
            traveler.remaining_time
    }


def print_job_summary(result):
    """
    Print formatted job result.

    Args:
        result (dict):
            Job simulation result.
    """

    print(
        "\n===== JOB SIMULATION =====\n"
    )

    if not result["worked"]:

        print(
            f"No work performed.\n"
            f"Reason: {result['reason']}"
        )

        return

    print(
        f"Airport: {result['airport']}"
    )

    print(
        f"Job: {result['job_name']}"
    )

    print(
        f"Hours Worked: "
        f"{result['hours']}"
    )

    print(
        f"Earnings: "
        f"${result['earnings']:.2f}"
    )

    print()

    print(
        f"Remaining Budget: "
        f"${result['remaining_budget']:.2f}"
    )

    print(
        f"Remaining Time: "
        f"{result['remaining_time']:.2f} min"
    )

def simulate_airport_stay(
    airport,
    traveler,
    activity_limit=2,
    lodging_interval_hours: float = 20.0,
    meal_interval_hours: float = 8.0,
):
    """
    Simulate traveler stay at an airport.

    The simulation includes:
        - Accommodation expenses
        - Food expenses
        - Tourist activities
        - Time consumption

    Args:
        airport:
            Airport object.

        traveler:
            Traveler object.

        activity_limit (int):
            Maximum number of activities.

    Returns:
        dict:
            Stay simulation summary.
    """

    # -----------------------------------------
    # INITIALIZE SUMMARY
    # -----------------------------------------

    summary = {

        "airport": airport.id,

        "activities_done": [],

        "lodging_cost": 0,

        "food_cost": 0,

        "activities_cost": 0,

        "activities_time": 0,

        "total_cost": 0,

        "total_time": 0
    }

    # -----------------------------------------
    # ACCOMMODATION (only if required by traveler state)
    # -----------------------------------------

    lodging_cost = 0
    lodging_time = 0
    if getattr(traveler, "hours_since_last_lodging", 0) >= lodging_interval_hours:
        lodging_cost = getattr(airport, "costo_alojamiento", 0)
        # Apply lodging
        traveler.spend_money(lodging_cost)
        summary["lodging_cost"] = lodging_cost
        # Assume 1 hotel night = 8 hours -> 480 minutes
        lodging_time = 480
        traveler.consume_time(lodging_time)
        # update hours counters
        if hasattr(traveler, "hours_since_last_meal"):
            traveler.hours_since_last_meal += lodging_time / 60.0
        if hasattr(traveler, "hours_since_last_lodging"):
            traveler.hours_since_last_lodging += lodging_time / 60.0
        summary["total_time"] += lodging_time
        # reset lodging counter
        if hasattr(traveler, "hours_since_last_lodging"):
            traveler.hours_since_last_lodging = 0

    # -----------------------------------------
    # FOOD (only if required by traveler state)
    # -----------------------------------------

    food_cost = 0
    food_time = 0
    if getattr(traveler, "hours_since_last_meal", 0) >= meal_interval_hours:
        food_cost = getattr(airport, "costo_alimentacion", 0)
        traveler.spend_money(food_cost)
        summary["food_cost"] = food_cost
        # Assume meals consume 1 hour -> 60 minutes
        food_time = 60
        traveler.consume_time(food_time)
        # update hours counters
        if hasattr(traveler, "hours_since_last_meal"):
            traveler.hours_since_last_meal += food_time / 60.0
        if hasattr(traveler, "hours_since_last_lodging"):
            traveler.hours_since_last_lodging += food_time / 60.0
        summary["total_time"] += food_time
        # reset meal counter
        if hasattr(traveler, "hours_since_last_meal"):
            traveler.hours_since_last_meal = 0

    # -----------------------------------------
    # ACTIVITIES
    # -----------------------------------------

    selected_activities = (airport.actividades[:activity_limit])

    for activity in (
        selected_activities
    ):

        activity_cost = (
                activity["costoUSD"]
            )

        activity_time = (
                activity["duracionMin"]
            )
        if (
            traveler.current_budget
            < activity_cost
        ):
         continue

        # Skip activity if no time
        if (
            traveler.remaining_time
            < activity_time
        ):
            continue

        # Apply activity effects
        traveler.spend_money(
            activity_cost
        )

        traveler.consume_time(activity_time)
        # update hours counters
        if hasattr(traveler, "hours_since_last_meal"):
            traveler.hours_since_last_meal += activity_time / 60.0
        if hasattr(traveler, "hours_since_last_lodging"):
            traveler.hours_since_last_lodging += activity_time / 60.0

        traveler.activities_done.append({

            "airport":
                airport.id,

            "activity":
                activity["nombre"]
        })

        summary[
            "activities_done"
        ].append(

            activity["nombre"]
        )

        summary[
            "activities_cost"
        ] += activity_cost

        summary[
            "activities_time"
        ] += activity_time

    # -----------------------------------------
    # CALCULATE TOTALS
    # -----------------------------------------

    total_cost = (

        summary["lodging_cost"]

        + summary["food_cost"]

        + summary["activities_cost"]
    )

    summary["total_cost"] = (
        total_cost
    )

    summary["total_time"] += (
        summary["activities_time"]
    )

    # -----------------------------------------
    # RETURN SUMMARY
    # -----------------------------------------

    return summary


def print_stay_summary(summary):
    """
    Print formatted airport stay summary.

    Args:
        summary (dict):
            Stay simulation summary.
    """

    print(
        "\n===== AIRPORT STAY SUMMARY =====\n"
    )

    print(
        f"Airport: {summary['airport']}"
    )

    print()

    print(
        f"Lodging Cost: "
        f"${summary['lodging_cost']:.2f}"
    )

    print(
        f"Food Cost: "
        f"${summary['food_cost']:.2f}"
    )

    print(
        f"Activities Cost: "
        f"${summary['activities_cost']:.2f}"
    )

    print()

    print(
        "Activities:"
    )

    if not summary["activities_done"]:

        print(
            "   No activities performed."
        )

    else:

        for activity in (
            summary["activities_done"]
        ):

            print(
                f"   - {activity}"
            )

    print()

    print(
        f"Total Cost: "
        f"${summary['total_cost']:.2f}"
    )

    print(
        f"Total Time: "
        f"{summary['total_time']} min"
    )

    