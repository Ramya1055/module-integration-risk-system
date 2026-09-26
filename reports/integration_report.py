from sqlalchemy.orm import Session

from database.models import (
    Integration,
    ModuleProfile,
    SystemMetric,
    IntegrationEvent,
    PerformanceAnalysis,
    SecurityFinding,
    BlockchainTransaction,
)


def generate_integration_report(
    db: Session,
    integration_id: str,
) -> dict:

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

    profiles = (
        db.query(ModuleProfile)
        .filter(
            ModuleProfile.integration_id
            == integration_id
        )
        .all()
    )

    metrics = (
        db.query(SystemMetric)
        .filter(
            SystemMetric.integration_id
            == integration_id
        )
        .order_by(SystemMetric.id)
        .all()
    )

    events = (
        db.query(IntegrationEvent)
        .filter(
            IntegrationEvent.integration_id
            == integration_id
        )
        .order_by(IntegrationEvent.id)
        .all()
    )

    performance = (
        db.query(PerformanceAnalysis)
        .filter(
            PerformanceAnalysis.integration_id
            == integration_id
        )
        .first()
    )

    findings = (
        db.query(SecurityFinding)
        .filter(
            SecurityFinding.integration_id
            == integration_id
        )
        .order_by(SecurityFinding.id)
        .all()
    )

    transactions = (
        db.query(BlockchainTransaction)
        .filter(
            BlockchainTransaction.integration_id
            == integration_id
        )
        .order_by(BlockchainTransaction.id)
        .all()
    )

    return {
        "integration": {
            "integration_id": integration.integration_id,
            "existing_module": integration.existing_module,
            "proposed_module": integration.proposed_module,
            "contract_address": integration.contract_address,
            "network": integration.network,
            "status": integration.status,
            "start_time": integration.start_time,
            "end_time": integration.end_time,
        },

        "module_profiles": [
            {
                "module_name": profile.module_name,
                "source_file": profile.source_file,
                "source_lines": profile.source_lines,
                "function_count": profile.function_count,
                "state_variable_count": profile.state_variable_count,
                "external_call_count": profile.external_call_count,
                "event_count": profile.event_count,
                "modifier_count": profile.modifier_count,
                "payable_function_count": (
                    profile.payable_function_count
                ),
                "interface_count": profile.interface_count,
                "dependency_count": profile.dependency_count,
            }
            for profile in profiles
        ],

        "metrics": [
            {
                "phase": metric.phase,
                "timestamp": metric.timestamp,
                "cpu_percent": metric.cpu_percent,
                "memory_percent": metric.memory_percent,
                "error_count": metric.error_count,
            }
            for metric in metrics
        ],

        "performance_analysis": (
            {
                "baseline_cpu": performance.baseline_cpu,
                "baseline_memory": performance.baseline_memory,
                "runtime_sample_count": (
                    performance.runtime_sample_count
                ),
                "average_runtime_cpu": (
                    performance.average_runtime_cpu
                ),
                "average_runtime_memory": (
                    performance.average_runtime_memory
                ),
                "cpu_change": performance.cpu_change,
                "memory_change": performance.memory_change,
                "total_runtime_errors": (
                    performance.total_runtime_errors
                ),
            }
            if performance
            else None
        ),

        "security_findings": [
            {
                "finding_type": finding.finding_type,
                "severity": finding.severity,
                "component": finding.component,
                "location": finding.location,
                "description": finding.description,
                "evidence": finding.evidence,
                "source": finding.source,
                "created_at": finding.created_at,
            }
            for finding in findings
        ],

        "blockchain_transactions": [
            {
                "transaction_hash": (
                    transaction.transaction_hash
                ),
                "from_address": (
                    transaction.from_address
                ),
                "to_address": (
                    transaction.to_address
                ),
                "block_number": (
                    transaction.block_number
                ),
                "gas_limit": (
                    transaction.gas_limit
                ),
                "gas_used": (
                    transaction.gas_used
                ),
                "status": transaction.status,
                "created_at": (
                    transaction.created_at
                ),
            }
            for transaction in transactions
        ],

        "events": [
            {
                "event_type": event.event_type,
                "component": event.component,
                "severity": event.severity,
                "source": event.source,
                "description": event.description,
                "timestamp": event.timestamp,
            }
            for event in events
        ],
    }

