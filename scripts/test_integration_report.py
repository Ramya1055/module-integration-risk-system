import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from reports.integration_report import (
    generate_integration_report,
)


db = SessionLocal()

try:
    report = generate_integration_report(
        db=db,
        integration_id="INT-000005",
    )

    print("Integration report generated.")
    print("--------------------------------")

    integration = report["integration"]

    print(
        f"Integration ID: "
        f"{integration['integration_id']}"
    )

    print(
        f"Existing Module: "
        f"{integration['existing_module']}"
    )

    print(
        f"Proposed Module: "
        f"{integration['proposed_module']}"
    )

    print(
        f"Status: "
        f"{integration['status']}"
    )

    print("--------------------------------")
    print(
        f"Module Profiles: "
        f"{len(report['module_profiles'])}"
    )

    print(
        f"Metrics: "
        f"{len(report['metrics'])}"
    )

    print(
        f"Security Findings: "
        f"{len(report['security_findings'])}"
    )

    print(
        f"Events: "
        f"{len(report['events'])}"
    )

    print("--------------------------------")

    if report["performance_analysis"]:
        print(
            "Performance analysis: available"
        )
    else:
        print(
            "Performance analysis: not available"
        )

finally:
    db.close()