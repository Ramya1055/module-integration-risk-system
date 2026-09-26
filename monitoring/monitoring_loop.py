import time

from sqlalchemy.orm import Session

from monitoring.runtime_monitor import (
    collect_runtime_metric,
)
from monitoring.event_recorder import (
    record_event,
)

def collect_runtime_samples(
    db: Session,
    integration_id: str,
    sample_count: int = 5,
    interval_seconds: int = 2,
) -> list:

    metrics = []

    for _ in range(sample_count):

        metric = collect_runtime_metric(
            db=db,
            integration_id=integration_id,
        )

        metrics.append(metric)
        record_event(
            db=db,
            integration_id=integration_id,
            event_type="RUNTIME_METRIC_COLLECTED",
            component="runtime_monitor",
            severity="INFO",
            source="monitoring_loop",
            description=(
                "A runtime system metric was collected "
                "during repeated integration monitoring."
            ),
        )

        if _ < sample_count - 1:
            time.sleep(interval_seconds)

    return metrics
