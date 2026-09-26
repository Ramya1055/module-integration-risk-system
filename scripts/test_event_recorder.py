import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from monitoring.event_recorder import record_event


db = SessionLocal()

try:
    event = record_event(
        db=db,
        integration_id="INT-000004",
        event_type="TEST_EVENT",
        component="test",
        severity="INFO",
        source="test_event_recorder",
        description="Testing integration event recording.",
    )

    print("Event recorded successfully.")
    print("--------------------------------")
    print(f"Event ID: {event.id}")
    print(f"Integration ID: {event.integration_id}")
    print(f"Event Type: {event.event_type}")
    print(f"Component: {event.component}")
    print(f"Severity: {event.severity}")
    print(f"Source: {event.source}")
    print(f"Description: {event.description}")
    print(f"Timestamp: {event.timestamp}")

finally:
    db.close()