import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from monitoring.runtime_monitor import (
    collect_runtime_metric,
)


db = SessionLocal()

try:
    metric = collect_runtime_metric(
        db=db,
        integration_id="INT-000004",
    )

    print("Runtime metric captured successfully.")
    print("--------------------------------")
    print(f"Metric ID: {metric.id}")
    print(
        f"Integration ID: "
        f"{metric.integration_id}"
    )
    print(f"Phase: {metric.phase}")
    print(f"CPU: {metric.cpu_percent}%")
    print(f"Memory: {metric.memory_percent}%")
    print(f"Errors: {metric.error_count}")
    print(f"Timestamp: {metric.timestamp}")

finally:
    db.close()