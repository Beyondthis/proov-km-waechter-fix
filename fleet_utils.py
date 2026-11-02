# fleet_utils.py
# Shared helpers for KM-Waechter. Cleaned up 2026.
# Removed: is_due() (duplicate of km_wachter logic), parse_service_date() (dead since 2014),
# chunk_list() (never called).

KM_PER_MILE = 1.60934                   # 1 mile = 1.60934 km, so km ÷ KM_PER_MILE → miles


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles. Used by the nightly UK partner report."""
    return km / KM_PER_MILE


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list of numbers, or 0.0 for an empty list."""
    if not values:
        return 0.0
    return sum(values) / len(values)
