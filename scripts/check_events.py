import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from database.models import IntegrationEvent


db = SessionLocal()

try:
    events = (
        db.query(IntegrationEvent)
        .filter(
            IntegrationEvent.integration_id
            == "INT-000005"
        )
        .order_by(IntegrationEvent.timestamp)
        .all()
    )

    print(
        f"Events found for INT-000005: {len(events)}"
    )
    print("--------------------------------")

    for event in events:
        print(f"Event ID: {event.id}")
        print(
            f"Integration ID: "
            f"{event.integration_id}"
        )
        print(
            f"Event Type: {event.event_type}"
        )
        print(
            f"Component: {event.component}"
        )
        print(
            f"Severity: {event.severity}"
        )
        print(
            f"Source: {event.source}"
        )
        print(
            f"Description: {event.description}"
        )
        print(
            f"Timestamp: {event.timestamp}"
        )
        print("--------------------------------")

finally:
    db.close()