import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from monitoring.monitoring_loop import (
    collect_runtime_samples,
)


db = SessionLocal()

try:
    metrics = collect_runtime_samples(
        db=db,
        integration_id="INT-000004",
        sample_count=3,
        interval_seconds=2,
    )

    print("Runtime monitoring completed.")
    print("--------------------------------")
    print(
        f"Samples collected: {len(metrics)}"
    )

    for metric in metrics:
        print("--------------------------------")
        print(
            f"Metric ID: {metric.id}"
        )
        print(
            f"Integration ID: "
            f"{metric.integration_id}"
        )
        print(
            f"Phase: {metric.phase}"
        )
        print(
            f"CPU: {metric.cpu_percent}%"
        )
        print(
            f"Memory: {metric.memory_percent}%"
        )
        print(
            f"Errors: {metric.error_count}"
        )
        print(
            f"Timestamp: {metric.timestamp}"
        )

finally:
    db.close()