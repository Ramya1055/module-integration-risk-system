import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from database.models import PerformanceAnalysis


db = SessionLocal()

try:
    analyses = (
        db.query(PerformanceAnalysis)
        .filter(
            PerformanceAnalysis.integration_id
            == "INT-000005"
        )
        .order_by(PerformanceAnalysis.id)
        .all()
    )

    print(
        f"Performance analyses found for "
        f"INT-000005: {len(analyses)}"
    )

    for analysis in analyses:
        print("--------------------------------")
        print(f"Analysis ID: {analysis.id}")
        print(
            f"Integration ID: "
            f"{analysis.integration_id}"
        )
        print(
            f"Baseline CPU: "
            f"{analysis.baseline_cpu}%"
        )
        print(
            f"Baseline Memory: "
            f"{analysis.baseline_memory}%"
        )
        print(
            f"Runtime Samples: "
            f"{analysis.runtime_sample_count}"
        )
        print(
            f"Average Runtime CPU: "
            f"{analysis.average_runtime_cpu}%"
        )
        print(
            f"Average Runtime Memory: "
            f"{analysis.average_runtime_memory}%"
        )
        print(
            f"CPU Change: "
            f"{analysis.cpu_change}"
        )
        print(
            f"Memory Change: "
            f"{analysis.memory_change}"
        )
        print(
            f"Total Runtime Errors: "
            f"{analysis.total_runtime_errors}"
        )
        print(
            f"Created At: "
            f"{analysis.created_at}"
        )

finally:
    db.close()