# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.
# Written in 2014. Modernized 2026.

from km_wachter import wear_percent, needs_service, SERVICE_INTERVAL_KM
from config_loader import load_settings
from log_util import log, flush_log
import fleet_utils


def car_wear(car: dict) -> float | None:
    """Return wear percentage for a car, or None if no service reading is available."""
    if "last_service_km" not in car:
        return None
    return wear_percent(car["odometer"] - car["last_service_km"], SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list) -> dict:
    """Return a summary dict with count, cars due for service, and average wear.

    Cars with no last_service_km reading are excluded from the wear average
    but are still counted in the total fleet size.
    """
    total = 0.0
    readable_count = 0
    due = 0
    for car in fleet:
        wear = car_wear(car)
        if wear is not None:
            total += wear
            readable_count += 1
        if needs_service(car):
            due += 1
    average = total / readable_count if readable_count > 0 else 0.0
    return {"count": len(fleet), "due": due, "average_wear": average}


def print_report(fleet: list) -> None:
    """Print the nightly fleet-health report to stdout and append it to the log file."""
    settings = load_settings()
    log(settings.get("report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"Average wear: {s['average_wear']:.1f}%")
    total_km = sum(car["odometer"] for car in fleet)
    # The partner garage in England wants the distance in miles (since 2015).
    print(f"Fleet distance: {fleet_utils.format_number(fleet_utils.km_to_miles(total_km))} miles")
    flush_log(settings.get("log_file", "km_wachter.log"))
