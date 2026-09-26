import psutil
from datetime import datetime

from sqlalchemy.orm import Session

from database.models import SystemMetric


def collect_baseline(
    db: Session,
    integration_id: str,
) -> SystemMetric:

    cpu_percent = psutil.cpu_percent(interval=1)

    memory_percent = psutil.virtual_memory().percent

    metric = SystemMetric(
        integration_id=integration_id,
        phase="BASELINE",
        timestamp=datetime.utcnow(),
        cpu_percent=cpu_percent,
        memory_percent=memory_percent,
        error_count=0,
    )

    db.add(metric)
    db.commit()
    db.refresh(metric)

    return metric