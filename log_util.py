# log_util.py
# Homemade logger. Modernized 2026.
# Removed: debug() — DEBUG has been False since 2014 and the branch was permanently dead.

import time

LOG_LINES: list[str] = []   # module-level buffer; cleared after each flush_log() call


def log(message: str) -> None:
    """Append a timestamped message to the in-memory log buffer and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def flush_log(path: str) -> None:
    """Write all buffered log lines to the given file path (append mode) and clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
