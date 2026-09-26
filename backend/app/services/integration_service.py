from sqlalchemy.orm import Session
from datetime import datetime
from database.models import Integration
from blockchain.monitor import get_transaction_details
from blockchain.transaction_service import store_transaction
from monitoring.baseline import collect_baseline
from monitoring.profile_service import (
    create_module_profile,
)
from monitoring.runtime_monitor import (
    collect_runtime_metric,
)
from monitoring.monitoring_loop import (
    collect_runtime_samples,
)
from monitoring.event_recorder import (
    record_event,
)
from monitoring.performance_analyzer import (
    analyze_performance,
)
from security.analyzer import (
    analyze_solidity_file,
)

from security.finding_service import (
    store_security_findings,
)



from pathlib import Path


def get_module_file_path(module_name: str) -> str:

    project_root = Path(__file__).resolve().parents[3]

    module_file = (
        project_root
        / "blockchain"
        / "contracts"
        / f"{module_name}.sol"
    )

    if not module_file.exists():
        raise FileNotFoundError(
            f"Solidity module not found: {module_file}"
        )

    return str(module_file)



def generate_integration_id(db: Session) -> str:
    count = db.query(Integration).count()
    return f"INT-{count + 1:06d}"


def create_integration(
    db: Session,
    existing_module: str,
    proposed_module: str,
    contract_address: str | None,
    network: str,
) -> Integration:

    integration_id = generate_integration_id(db)

    integration = Integration(
        integration_id=integration_id,
        existing_module=existing_module,
        proposed_module=proposed_module,
        contract_address=contract_address,
        network=network,
        status="CREATED",
    )

    db.add(integration)
    db.commit()
    db.refresh(integration)

    return integration




def start_integration(
    db: Session,
    integration_id: str,
) -> Integration:

    integration = (
        db.query(Integration)
        .filter(
            Integration.integration_id == integration_id
        )
        .first()
    )

    if integration is None:
        raise ValueError(
            f"Integration {integration_id} not found."
        )

    if integration.status != "CREATED":
        raise ValueError(
            f"Integration {integration_id} cannot be started "
            f"from status {integration.status}."
        )

    integration.status = "INITIALIZING"
    integration.start_time = datetime.utcnow()

    db.commit()

    collect_baseline(
        db=db,
        integration_id=integration_id,
    )

    module_file = get_module_file_path(
        integration.proposed_module
    )

    create_module_profile(
        db=db,
        integration_id=integration_id,
        file_path=module_file,
    )

    integration.status = "BASELINE_CAPTURED"

    db.commit()
    record_event(
        db=db,
        integration_id=integration_id,
        event_type="BASELINE_CAPTURED",
        component="baseline",
        severity="INFO",
        source="integration_service",
        description=(
            "Baseline metrics and proposed module "
            "profile were captured successfully."
        ),
    )

    db.refresh(integration)

    return integration


def begin_integration_monitoring(
    db: Session,
    integration_id: str,
) -> Integration:

    integration = (
        db.query(Integration)
        .filter(
            Integration.integration_id
            == integration_id
        )
        .first()
    )

    if integration is None:
        raise ValueError(
            f"Integration {integration_id} not found."
        )

    if integration.status != "BASELINE_CAPTURED":
        raise ValueError(
            f"Integration {integration_id} cannot "
            f"begin monitoring from status "
            f"{integration.status}."
        )

    integration.status = "IN_PROGRESS"

    db.commit()
    record_event(
        db=db,
        integration_id=integration_id,
        event_type="MONITORING_STARTED",
        component="monitoring",
        severity="INFO",
        source="integration_service",
        description=(
            "Runtime monitoring started for the integration."
        ),
    )

    db.refresh(integration)

    return integration



def collect_integration_runtime_metric(
    db: Session,
    integration_id: str,
):

    integration = (
        db.query(Integration)
        .filter(
            Integration.integration_id
            == integration_id
        )
        .first()
    )

    if integration is None:
        raise ValueError(
            f"Integration {integration_id} not found."
        )

    if integration.status != "IN_PROGRESS":
        raise ValueError(
            f"Integration {integration_id} cannot "
            f"collect runtime metrics from status "
            f"{integration.status}."
        )

    metric = collect_runtime_metric(
        db=db,
        integration_id=integration_id,
    )
    record_event(
        db=db,
        integration_id=integration_id,
        event_type="RUNTIME_METRIC_COLLECTED",
        component="runtime_monitor",
        severity="INFO",
        source="integration_service",
        description=(
            "A runtime system metric was collected "
            "during integration monitoring."
        ),
    )

    return metric



def collect_integration_runtime_samples(
    db: Session,
    integration_id: str,
    sample_count: int = 5,
    interval_seconds: int = 2,
):
    integration = (
        db.query(Integration)
        .filter(
            Integration.integration_id
            == integration_id
        )
        .first()
    )

    if integration is None:
        raise ValueError(
            f"Integration {integration_id} not found."
        )

    if integration.status != "IN_PROGRESS":
        raise ValueError(
            f"Integration {integration_id} cannot "
            f"collect runtime samples from status "
            f"{integration.status}."
        )

    metrics = collect_runtime_samples(
        db=db,
        integration_id=integration_id,
        sample_count=sample_count,
        interval_seconds=interval_seconds,
    )

    return metrics


def complete_integration(
    db: Session,
    integration_id: str,
) -> Integration:

    integration = (
        db.query(Integration)
        .filter(
            Integration.integration_id
            == integration_id
        )
        .first()
    )

    if integration is None:
        raise ValueError(
            f"Integration {integration_id} not found."
        )

    if integration.status != "IN_PROGRESS":
        raise ValueError(
            f"Integration {integration_id} cannot "
            f"be completed from status "
            f"{integration.status}."
        )

    integration.status = "COMPLETED"
    integration.end_time = datetime.utcnow()

    db.commit()

    record_event(
        db=db,
        integration_id=integration_id,
        event_type="INTEGRATION_COMPLETED",
        component="integration_service",
        severity="INFO",
        source="integration_service",
        description=(
            "Integration monitoring completed successfully."
        ),
    )

    db.refresh(integration)

    return integration


def analyze_completed_integration(
    db: Session,
    integration_id: str,
):
    integration = (
        db.query(Integration)
        .filter(
            Integration.integration_id
            == integration_id
        )
        .first()
    )

    if integration is None:
        raise ValueError(
            f"Integration {integration_id} not found."
        )

    if integration.status != "COMPLETED":
        raise ValueError(
            f"Integration {integration_id} cannot "
            f"be analyzed from status "
            f"{integration.status}."
        )

    performance_result = analyze_performance(
        db=db,
        integration_id=integration_id,
    )

    integration.status = "POST_ANALYSIS"

    db.commit()

    record_event(
        db=db,
        integration_id=integration_id,
        event_type="POST_ANALYSIS_COMPLETED",
        component="performance_analyzer",
        severity="INFO",
        source="integration_service",
        description=(
            "Post-integration performance analysis "
            "was completed successfully."
        ),
    )

    db.refresh(integration)

    return {
        "integration_id": integration_id,
        "status": integration.status,
        "performance_analysis": performance_result,
    }

def analyze_integration_security(
    db: Session,
    integration_id: str,
):
    integration = (
        db.query(Integration)
        .filter(
            Integration.integration_id
            == integration_id
        )
        .first()
    )

    if integration is None:
        raise ValueError(
            f"Integration {integration_id} not found."
        )

    if integration.status != "POST_ANALYSIS":
        raise ValueError(
            f"Integration {integration_id} cannot "
            f"perform security analysis from status "
            f"{integration.status}."
        )

    module_file = get_module_file_path(
        integration.proposed_module
    )

    findings = analyze_solidity_file(
        module_file
    )

    stored_findings = store_security_findings(
        db=db,
        integration_id=integration_id,
        findings=findings,
    )

    record_event(
        db=db,
        integration_id=integration_id,
        event_type="SECURITY_ANALYSIS_COMPLETED",
        component="security_analyzer",
        severity="INFO",
        source="integration_service",
        description=(
            f"Security analysis completed. "
            f"{len(stored_findings)} finding(s) recorded."
        ),
    )

    return {
        "integration_id": integration_id,
        "status": integration.status,
        "findings_detected": len(findings),
        "findings_stored": len(stored_findings),
        "findings": [
            {
                "id": finding.id,
                "finding_type": finding.finding_type,
                "severity": finding.severity,
                "component": finding.component,
                "location": finding.location,
                "description": finding.description,
                "evidence": finding.evidence,
                "source": finding.source,
            }
            for finding in stored_findings
        ],
    }

def finalize_integration(
    db: Session,
    integration_id: str,
) -> Integration:

    integration = (
        db.query(Integration)
        .filter(
            Integration.integration_id
            == integration_id
        )
        .first()
    )

    if integration is None:
        raise ValueError(
            f"Integration {integration_id} not found."
        )

    if integration.status != "POST_ANALYSIS":
        raise ValueError(
            f"Integration {integration_id} cannot "
            f"be finalized from status "
            f"{integration.status}."
        )

    integration.status = "FINALIZED"

    db.commit()

    record_event(
        db=db,
        integration_id=integration_id,
        event_type="INTEGRATION_FINALIZED",
        component="integration_service",
        severity="INFO",
        source="integration_service",
        description=(
            "All planned Stage 1 observations and "
            "analyses were completed and the "
            "integration was finalized."
        ),
    )

    db.refresh(integration)

    return integration


def record_blockchain_transaction(
    db: Session,
    integration_id: str,
    transaction_hash: str,
):
    transaction_data = get_transaction_details(
        transaction_hash
    )

    transaction = store_transaction(
        db=db,
        integration_id=integration_id,
        transaction_data=transaction_data,
    )

    return transaction