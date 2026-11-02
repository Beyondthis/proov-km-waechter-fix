# config_loader.py
# Reads settings.cfg. Modernized 2026.

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = [
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
]


def load_settings(path: str | None = None) -> dict:
    """Parse settings.cfg and return a dict of known key/value pairs.

    All values are returned as strings; use get_int() to convert numeric keys.
    Unknown keys are silently ignored so that the caller is not broken by future
    additions to the config file.
    """
    if path is None:
        path = SETTINGS_FILE
    settings: dict = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key in KNOWN_KEYS:
                settings[key] = value
    return settings


def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return settings[key] as an int, or fallback if the key is absent or not an integer."""
    if key in settings:
        try:
            return int(settings[key])
        except ValueError:
            return fallback
    return fallback
