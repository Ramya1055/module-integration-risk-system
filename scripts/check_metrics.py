import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from database.models import SystemMetric


db = SessionLocal()

try:
    metrics = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.integration_id
            == "INT-000005"
        )
        .order_by(SystemMetric.id)
        .all()
    )

    print(
        f"Metrics found for INT-000005: "
        f"{len(metrics)}"
    )

    for metric in metrics:
        print("--------------------------------")
        print(f"Metric ID: {metric.id}")
        print(f"Phase: {metric.phase}")
        print(f"CPU: {metric.cpu_percent}%")
        print(
            f"Memory: "
            f"{metric.memory_percent}%"
        )
        print(
            f"Errors: "
            f"{metric.error_count}"
        )
        print(
            f"Timestamp: "
            f"{metric.timestamp}"
        )

finally:
    db.close()