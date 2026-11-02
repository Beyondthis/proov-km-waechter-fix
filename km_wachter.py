# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Modernized 2026.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service: float, interval: float) -> float:
    """Return wear as a percentage (0–100+) of one service interval."""
    ratio = km_since_service / interval   # true division: 14900/15000 → 0.9933
    return ratio * 100


def needs_service(car: dict) -> bool:
    """Return True if the car has reached the service warning threshold.

    A car with no last_service_km reading is treated as unknown — it is NOT
    flagged, because a missing reading cannot be equated with 'serviced at km 0'.
    """
    if "last_service_km" not in car:
        return False
    km_since = car["odometer"] - car["last_service_km"]
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return pct >= WARN_AT_PERCENT


def check_fleet(fleet: list) -> list:
    """Flag every car that is due for service and return a list of their IDs."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
