import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from backend.app.services.integration_service import (
    complete_integration,
)


db = SessionLocal()

try:
    integration = complete_integration(
        db=db,
        integration_id="INT-000005",
    )

    print("Integration completed successfully.")
    print("--------------------------------")
    print(
        f"Integration ID: "
        f"{integration.integration_id}"
    )
    print(
        f"Status: "
        f"{integration.status}"
    )
    print(
        f"Start Time: "
        f"{integration.start_time}"
    )
    print(
        f"End Time: "
        f"{integration.end_time}"
    )

finally:
    db.close()