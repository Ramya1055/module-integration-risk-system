import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from database.db import SessionLocal
from database.models import SystemMetric


db = SessionLocal()

try:
    metrics = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.phase == "BASELINE"
        )
        .order_by(SystemMetric.id)
        .all()
    )

    print(f"Baseline records found: {len(metrics)}")

    for metric in metrics:
        print("--------------------------------")
        print(f"ID: {metric.id}")
        print(f"Integration ID: {metric.integration_id}")
        print(f"Phase: {metric.phase}")
        print(f"CPU: {metric.cpu_percent}%")
        print(f"Memory: {metric.memory_percent}%")
        print(f"Errors: {metric.error_count}")
        print(f"Timestamp: {metric.timestamp}")

finally:
    db.close()