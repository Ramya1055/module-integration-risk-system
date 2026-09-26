from datetime import datetime

from sqlalchemy.orm import Session

from database.models import IntegrationEvent


def record_event(
    db: Session,
    integration_id: str,
    event_type: str,
    component: str | None = None,
    severity: str = "INFO",
    source: str | None = None,
    description: str | None = None,
) -> IntegrationEvent:

    event = IntegrationEvent(
        integration_id=integration_id,
        event_type=event_type,
        component=component,
        severity=severity,
        source=source,
        description=description,
        timestamp=datetime.utcnow(),
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event