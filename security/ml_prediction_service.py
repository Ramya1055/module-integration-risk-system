
import csv
from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from database.models import (
    Integration,
    ModuleProfile,
    SystemMetric,
    IntegrationEvent,
    PerformanceAnalysis,
    SecurityFinding,
    BlockchainTransaction,
    OnchainObservation,
)

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "artifacts" / "stage3" / "risk_model.joblib"
DATASET_PATH = ROOT / "stage3_reviewed_dataset.csv"


def _average(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def _unique(values):
    return ";".join(sorted({
        str(v) for v in values if v not in (None, "")
    }))


def predict_integration_risk(db: Session, integration_id: str) -> dict:
    """Return a preliminary ML prediction independently of rule-based risk."""

    if not MODEL_PATH.exists():
        return {
            "ml_status": "MODEL_UNAVAILABLE",
            "ml_prediction": None,
            "ml_confidence": None,
            "ml_warning": "Trained model artifact was not found.",
        }

    integration = db.query(Integration).filter_by(
        integration_id=integration_id
    ).first()

    if integration is None:
        return {
            "ml_status": "INTEGRATION_NOT_FOUND",
            "ml_prediction": None,
            "ml_confidence": None,
        }

    try:
        model = joblib.load(MODEL_PATH)

        profiles_all = (
            db.query(ModuleProfile)
            .filter_by(integration_id=integration_id)
            .order_by(ModuleProfile.created_at.desc(), ModuleProfile.id.desc())
            .all()
        )

        latest_by_module = {}
        for p in profiles_all:
            if p.module_name not in latest_by_module:
                latest_by_module[p.module_name] = p
        profiles = list(latest_by_module.values())

        metrics = db.query(SystemMetric).filter_by(
            integration_id=integration_id
        ).all()
        events = db.query(IntegrationEvent).filter_by(
            integration_id=integration_id
        ).all()
        performance = db.query(PerformanceAnalysis).filter_by(
            integration_id=integration_id
        ).all()
        findings = db.query(SecurityFinding).filter_by(
            integration_id=integration_id
        ).all()
        transactions = db.query(BlockchainTransaction).filter_by(
            integration_id=integration_id
        ).all()
        observations = db.query(OnchainObservation).filter_by(
            integration_id=integration_id
        ).all()

        row = {
            "existing_module": integration.existing_module,
            "proposed_module": integration.proposed_module,
            "profile_count": len(profiles_all),
            "distinct_module_count": len(profiles),
            "module_names": _unique(p.module_name for p in profiles),
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
            "system_metric_count": len(metrics),
            "average_cpu_percent": _average(
                m.cpu_percent for m in metrics
            ),
            "average_memory_percent": _average(
                m.memory_percent for m in metrics
            ),
            "performance_record_count": len(performance),
            "baseline_cpu_average": _average(
                p.baseline_cpu for p in performance
            ),
            "baseline_memory_average": _average(
                p.baseline_memory for p in performance
            ),
            "runtime_cpu_average": _average(
                p.average_runtime_cpu for p in performance
            ),
            "runtime_memory_average": _average(
                p.average_runtime_memory for p in performance
            ),
            "cpu_change_average": _average(
                p.cpu_change for p in performance
            ),
            "memory_change_average": _average(
                p.memory_change for p in performance
            ),
            "runtime_sample_count_total": sum(
                p.runtime_sample_count or 0 for p in performance
            ) if performance else None,
            "integration_event_count": len(events),
            "event_types": _unique(e.event_type for e in events),
            "security_finding_count": len(findings),
            "finding_types": _unique(f.finding_type for f in findings),
            "finding_sources": _unique(f.source for f in findings),
            "transaction_count": len(transactions),
            "transaction_success_count": sum(
                1 for t in transactions if t.status == 1
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
        }

        # Use the exact feature order captured during model training.
        feature_names = getattr(model, "feature_names_in_", None)
        if feature_names is None:
            if not DATASET_PATH.exists():
                raise ValueError("Cannot determine the trained feature columns.")
            with DATASET_PATH.open(
                "r", newline="", encoding="utf-8-sig"
            ) as f:
                feature_names = [
                    c for c in (csv.DictReader(f).fieldnames or [])
                    if c != "risk_label"
                ]

        features = pd.DataFrame(
            [{name: row.get(name) for name in feature_names}],
            columns=list(feature_names),
        )

        prediction = str(model.predict(features)[0])
        probabilities = model.predict_proba(features)[0]
        confidence = float(max(probabilities))

        return {
            "ml_status": "PRELIMINARY",
            "ml_prediction": prediction,
            "ml_confidence": round(confidence, 4),
            "ml_confidence_percent": round(confidence * 100, 2),
            "ml_warning": (
                "Research prototype trained on a small reviewed dataset. "
                "Prediction is not proof of safety and does not approve "
                "or reject an integration."
            ),
        }

    except Exception as exc:
        return {
            "ml_status": "PREDICTION_ERROR",
            "ml_prediction": None,
            "ml_confidence": None,
            "ml_warning": str(exc)[:500],
        }
