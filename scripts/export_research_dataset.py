import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import func
from database.db import SessionLocal
from database.models import (
    Integration,
    ModuleProfile,
    SystemMetric,
    IntegrationEvent,
    PerformanceAnalysis,
    SecurityFinding,
    BlockchainTransaction,
    OnchainObservation,
    Assessment,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research_dataset.csv"


def average(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def unique_values(values):
    return sorted({str(v) for v in values if v not in (None, "")})


def main():
    db = SessionLocal()
    try:
        integrations = (
            db.query(Integration)
            .order_by(Integration.integration_id)
            .all()
        )

        rows = []

        for integration in integrations:
            iid = integration.integration_id

            all_profiles = (
            db.query(ModuleProfile)
            .filter_by(integration_id=iid)
            .order_by(ModuleProfile.created_at.desc(), ModuleProfile.id.desc())
            .all()
        )

        # Keep the latest profile record for each module.
            latest_by_module = {}
            for profile in all_profiles:
                if profile.module_name not in latest_by_module:
                    latest_by_module[profile.module_name] = profile

            profiles = list(latest_by_module.values())
            metrics = db.query(SystemMetric).filter_by(
                integration_id=iid
            ).all()
            events = db.query(IntegrationEvent).filter_by(
                integration_id=iid
            ).all()
            performance = db.query(PerformanceAnalysis).filter_by(
                integration_id=iid
            ).all()
            findings = db.query(SecurityFinding).filter_by(
                integration_id=iid
            ).all()
            transactions = db.query(BlockchainTransaction).filter_by(
                integration_id=iid
            ).all()
            observations = db.query(OnchainObservation).filter_by(
                integration_id=iid
            ).all()
            assessments = (
                db.query(Assessment)
                .filter_by(integration_id=iid)
                .order_by(Assessment.created_at.desc())
                .all()
            )

            row = {
                "integration_id": iid,
                "existing_module": integration.existing_module,
                "proposed_module": integration.proposed_module,
                "network": integration.network,
                "integration_status": integration.status,
                "contract_address": integration.contract_address,
                "integration_created_at": (
                    integration.created_at.isoformat()
                    if integration.created_at else None
                ),

                # Module structure
                "profile_count": len(all_profiles),
                "distinct_module_count": len(profiles),
                "module_names": ";".join(unique_values(
                    p.module_name for p in profiles
                )),
                "source_lines_total": sum(
                    p.source_lines or 0 for p in profiles
                ) if profiles else None,
                "function_count_total": sum(
                    p.function_count or 0 for p in profiles
                ) if profiles else None,
                "state_variable_count_total": sum(
                    p.state_variable_count or 0 for p in profiles
                ) if profiles else None,
                "external_call_count_total": sum(
                    p.external_call_count or 0 for p in profiles
                ) if profiles else None,
                "dependency_count_total": sum(
                    p.dependency_count or 0 for p in profiles
                ) if profiles else None,

                # Runtime observations
                "system_metric_count": len(metrics),
                "average_cpu_percent": average(
                    m.cpu_percent for m in metrics
                ),
                "average_memory_percent": average(
                    m.memory_percent for m in metrics
                ),
                "runtime_error_count_total": sum(
                    m.error_count or 0 for m in metrics
                ) if metrics else None,
                "performance_record_count": len(performance),
                "baseline_cpu_average": average(
                    p.baseline_cpu for p in performance
                ),
                "baseline_memory_average": average(
                    p.baseline_memory for p in performance
                ),
                "runtime_cpu_average": average(
                    p.average_runtime_cpu for p in performance
                ),
                "runtime_memory_average": average(
                    p.average_runtime_memory for p in performance
                ),
                "cpu_change_average": average(
                    p.cpu_change for p in performance
                ),
                "memory_change_average": average(
                    p.memory_change for p in performance
                ),
                "runtime_sample_count_total": sum(
                    p.runtime_sample_count or 0 for p in performance
                ) if performance else None,
                "performance_runtime_errors_total": sum(
                    p.total_runtime_errors or 0 for p in performance
                ) if performance else None,

                # Events and findings
                "integration_event_count": len(events),
                "event_types": ";".join(unique_values(
                    e.event_type for e in events
                )),
                "event_severities": ";".join(unique_values(
                    e.severity for e in events
                )),
                "security_finding_count": len(findings),
                "finding_types": ";".join(unique_values(
                    f.finding_type for f in findings
                )),
                "finding_severities": ";".join(unique_values(
                    f.severity for f in findings
                )),
                "finding_sources": ";".join(unique_values(
                    f.source for f in findings
                )),

                # Blockchain evidence
                "transaction_count": len(transactions),
                "transaction_success_count": sum(
                    1 for t in transactions if t.status == 1
                ),
                "transaction_failed_count": sum(
                    1 for t in transactions if t.status == 0
                ),
                "gas_used_total": sum(
                    t.gas_used or 0 for t in transactions
                ) if transactions else None,
                "onchain_observation_count": len(observations),
                "onchain_failed_call_count": sum(
                    1 for o in observations if o.success is False
                ),
                "onchain_violation_observation_count": sum(
                    1 for o in observations if o.violations
                ),
                "onchain_violation_types": ";".join(unique_values(
                    o.violations for o in observations
                )),
                "onchain_max_depth_observed": max(
                    (o.max_depth for o in observations
                     if o.max_depth is not None),
                    default=None,
                ),

                # Review information; not ground-truth labels
                
                # Review information and human-reviewed labels
                "assessment_count": len(assessments),
                "assessment_status": (
                    assessments[0].assessment_status if assessments else None
                ),
                "reviewer_decision": (
                    assessments[0].reviewer_decision if assessments else None
                ),
                "reviewer_notes": (
                    assessments[0].reviewer_notes if assessments else None
                ),

                # Keep automated classification separate from reviewed label.
                "preliminary_risk_level": (
                    assessments[0].risk_level if assessments else None
                ),
                "risk_label": (
                    assessments[0].reviewed_risk_level
                    if assessments
                    and assessments[0].reviewer_decision in {"APPROVE", "REJECT"}
                    and assessments[0].reviewed_risk_level
                    else None
                ),
                "risk_label_validated": bool(
                    assessments
                    and assessments[0].reviewer_decision in {"APPROVE", "REJECT"}
                    and assessments[0].reviewed_risk_level
                    in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
                ),

        }

            rows.append(row)

        if not rows:
            print("No integrations found. CSV was not created.")
            return

        fieldnames = list(rows[0].keys())
        with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print("===== RESEARCH DATASET EXPORTED =====")
        print(f"Output: {OUTPUT}")
        print(f"Rows (integrations): {len(rows)}")
        print(f"Columns (features): {len(fieldnames)}")
        print("Risk labels are marked unvalidated.")
        print("No database records were modified.")

    finally:
        db.close()


if __name__ == "__main__":
    main()


