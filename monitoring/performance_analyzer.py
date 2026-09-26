from sqlalchemy.orm import Session

from database.models import (
    SystemMetric,
    PerformanceAnalysis,
)

def analyze_performance(
    db: Session,
    integration_id: str,
) -> dict:

    existing_analysis = (
        db.query(PerformanceAnalysis)
        .filter(
            PerformanceAnalysis.integration_id
            == integration_id
        )
        .first()
    )

    if existing_analysis:
        db.delete(existing_analysis)
        db.commit()
    
    
    metrics = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.integration_id
            == integration_id
        )
        .order_by(SystemMetric.id)
        .all()
    )

    if not metrics:
        raise ValueError(
            f"No metrics found for {integration_id}."
        )

    baseline_metrics = [
        metric
        for metric in metrics
        if metric.phase == "BASELINE"
    ]

    runtime_metrics = [
        metric
        for metric in metrics
        if metric.phase == "DURING_INTEGRATION"
    ]

    if not baseline_metrics:
        raise ValueError(
            f"No baseline metric found for "
            f"{integration_id}."
        )

    if not runtime_metrics:
        raise ValueError(
            f"No runtime metrics found for "
            f"{integration_id}."
        )

    baseline = baseline_metrics[0]

    runtime_cpu_values = [
        metric.cpu_percent
        for metric in runtime_metrics
        if metric.cpu_percent is not None
    ]

    runtime_memory_values = [
        metric.memory_percent
        for metric in runtime_metrics
        if metric.memory_percent is not None
    ]

    average_runtime_cpu = (
        sum(runtime_cpu_values)
        / len(runtime_cpu_values)
        if runtime_cpu_values
        else None
    )

    average_runtime_memory = (
        sum(runtime_memory_values)
        / len(runtime_memory_values)
        if runtime_memory_values
        else None
    )

    cpu_change = (
        average_runtime_cpu
        - baseline.cpu_percent
        if (
            average_runtime_cpu is not None
            and baseline.cpu_percent is not None
        )
        else None
    )

    memory_change = (
        average_runtime_memory
        - baseline.memory_percent
        if (
            average_runtime_memory is not None
            and baseline.memory_percent is not None
        )
        else None
    )

    total_runtime_errors = sum(
        metric.error_count
        for metric in runtime_metrics
    )

    analysis = PerformanceAnalysis(
        integration_id=integration_id,
        baseline_cpu=baseline.cpu_percent,
        baseline_memory=baseline.memory_percent,
        runtime_sample_count=len(runtime_metrics),
        average_runtime_cpu=average_runtime_cpu,
        average_runtime_memory=average_runtime_memory,
        cpu_change=cpu_change,
        memory_change=memory_change,
        total_runtime_errors=total_runtime_errors,
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return {
        "integration_id": integration_id,
        "baseline_cpu": analysis.baseline_cpu,
        "baseline_memory": analysis.baseline_memory,
        "runtime_sample_count": analysis.runtime_sample_count,
        "average_runtime_cpu": analysis.average_runtime_cpu,
        "average_runtime_memory": analysis.average_runtime_memory,
        "cpu_change": analysis.cpu_change,
        "memory_change": analysis.memory_change,
        "total_runtime_errors": analysis.total_runtime_errors,
    }