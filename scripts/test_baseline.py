import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from database.db import SessionLocal
from monitoring.baseline import collect_baseline


db = SessionLocal()

try:
    metric = collect_baseline(
        db=db,
        integration_id="INT-000001",
    )

    print("Baseline captured successfully.")
    print(f"Integration ID: {metric.integration_id}")
    print(f"Phase: {metric.phase}")
    print(f"CPU usage: {metric.cpu_percent}%")
    print(f"Memory usage: {metric.memory_percent}%")
    print(f"Error count: {metric.error_count}")
    print(f"Timestamp: {metric.timestamp}")

finally:
    db.close()