import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from monitoring.performance_analyzer import (
    analyze_performance,
)


db = SessionLocal()

try:
    result = analyze_performance(
        db=db,
        integration_id="INT-000005",
    )

    print("Performance analysis completed.")
    print("--------------------------------")

    for key, value in result.items():
        print(f"{key}: {value}")

finally:
    db.close()