# src/metrics.py

import json
import time
import os

METRICS_FILE = "metrics.json"

def log_metric(code: str, runtime: str, duration: float, success: bool):
    entry = {
        "timestamp": time.time(),
        "runtime": runtime,
        "duration": round(duration, 4),
        "success": success
    }

    # Load existing
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    # Save updated
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)
