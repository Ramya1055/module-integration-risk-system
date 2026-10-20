import json
from datetime import datetime

from sqlalchemy.orm import Session

from database.models import (
    Assessment,
    Integration,
    SecurityFinding,
    OnchainObservation,
    IntegrationEvent,
    PerformanceAnalysis,
    BlockchainTransaction,
)


EVIDENCE_SUMMARY_LIMIT = 2000


def _value(record, field):
    """Read an optional ORM field without assuming it always exists."""
    value = getattr(record, field, None)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _records(db, model, integration_id, fields, limit=3):
    """Fetch a small, recent evidence sample for the assessment summary."""
    query = db.query(model).filter(
        model.integration_id == integration_id
    )

    if hasattr(model, "id"):
        query = query.order_by(model.id.desc())

    rows = query.limit(limit).all()
    return [
        {field: _value(row, field) for field in fields}
        for row in rows
    ]


def _build_evidence_summary(db, integration_id, findings):
    evidence = {
        "integration_id": integration_id,
        "evidence_counts": {},
        "security_findings": [],
        "onchain_observations": [],
        "integration_events": [],
        "performance_analysis": [],
        "blockchain_transactions": [],
        "note": (
            "Observations and failed transactions are evidence for review, "
            "not automatic proof of a vulnerability or risk level."
        ),
    }

    sources = [
        (
            "onchain_observations",
            OnchainObservation,
            [
                "transaction_hash", "block_number", "host_address",
                "module_address", "call_id", "success", "gas_used",
                "max_depth", "balance_delta", "violations",
            ],
        ),
        (
            "integration_events",
            IntegrationEvent,
            ["event_type", "component", "severity", "source"],
        ),
        (
            "performance_analysis",
            PerformanceAnalysis,
            [
                "baseline_cpu", "baseline_memory", "runtime_sample_count",
                "average_runtime_cpu", "average_runtime_memory",
                "cpu_change", "memory_change", "total_runtime_errors",
            ],
        ),
        (
            "blockchain_transactions",
            BlockchainTransaction,
            [
                "transaction_hash", "block_number", "status",
                "gas", "gas_used", "from_address", "to_address",
            ],
        ),
    ]

    evidence["evidence_counts"]["security_findings"] = len(findings)

    for finding in findings:
        evidence["security_findings"].append({
            "finding_type": finding.finding_type,
            "severity": finding.severity,
            "source": finding.source,
            "component": finding.component,
            "location": finding.location,
        })

    for key, model, fields in sources:
        evidence["evidence_counts"][key] = (
            db.query(model)
            .filter(model.integration_id == integration_id)
            .count()
        )
        evidence[key] = _records(db, model, integration_id, fields)

    # Keep valid JSON within the database field's existing 2000-character
    # limit. Counts remain available even when some sample records are omitted.
    while len(json.dumps(evidence, default=str)) > EVIDENCE_SUMMARY_LIMIT:
        candidates = [
            key for key, _, _ in sources
            if evidence[key]
        ]
        if evidence["security_findings"]:
            candidates.append("security_findings")

        if not candidates:
            break

        largest_key = max(candidates, key=lambda key: len(evidence[key]))
        evidence[largest_key].pop()

    return json.dumps(evidence, default=str)



def _classify_risk(db, integration_id, findings):
    """Preliminary evidence-based rules; not a validated ML prediction."""
    observations = (
        db.query(OnchainObservation)
        .filter(OnchainObservation.integration_id == integration_id)
        .all()
    )
    performance = (
        db.query(PerformanceAnalysis)
        .filter(PerformanceAnalysis.integration_id == integration_id)
        .order_by(PerformanceAnalysis.id.desc())
        .first()
    )

    finding_severities = {
        str(getattr(f, "severity", "") or "").upper()
        for f in findings
    }
    violations = [
        str(getattr(o, "violations", "") or "").upper()
        for o in observations
    ]
    violations = [v for v in violations if v not in {"", "NONE", "NULL"}]

    # Strong test anomalies require investigation, not proof of exploitation.
    if any(
        "STORAGE_CANARY_CHANGED" in v or "REENTRY" in v
        for v in violations
    ):
        return "HIGH"

    if finding_severities.intersection({"CRITICAL", "HIGH"}):
        return "HIGH"

    if violations or finding_severities.intersection({"MEDIUM", "WARNING"}):
        return "MEDIUM"

    runtime_errors = (
        getattr(performance, "total_runtime_errors", 0) or 0
    ) if performance else 0

    if runtime_errors > 0:
        return "MEDIUM"

    has_evidence = bool(findings or observations or performance)
    if has_evidence:
        return "LOW"

    return "UNASSESSED"




def create_assessment(
    db: Session,
    integration_id: str,
) -> Assessment:
    integration = (
        db.query(Integration)
        .filter(Integration.integration_id == integration_id)
        .first()
    )
    if integration is None:
        raise ValueError(f"Integration not found: {integration_id}")

    findings = (
        db.query(SecurityFinding)
        .filter(SecurityFinding.integration_id == integration_id)
        .all()
    )
    risk_level = _classify_risk(db, integration_id, findings)
    summary = _build_evidence_summary(db, integration_id, findings)

    existing = (
        db.query(Assessment)
        .filter(Assessment.integration_id == integration_id)
        .order_by(Assessment.id.desc())
        .first()
    )

    if existing is not None:
        # Refresh evidence only while the assessment is awaiting review.
        # Never silently alter an assessment that has already been reviewed.
        if existing.reviewer_decision == "PENDING":
            existing.findings_count = len(findings)
            existing.evidence_summary = summary
            existing.risk_level = risk_level
            db.commit()
            db.refresh(existing)
        return existing

    assessment = Assessment(
        assessment_id=f"ASM-{integration_id}",
        integration_id=integration_id,
        assessment_status="PENDING_REVIEW",
        risk_level=risk_level,
        findings_count=len(findings),
        evidence_summary=summary,
        created_at=datetime.utcnow(),
        reviewer_decision="PENDING",
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_assessment(
    db: Session,
    assessment_id: str,
) -> Assessment | None:
    return (
        db.query(Assessment)
        .filter(Assessment.assessment_id == assessment_id)
        .first()
    )



def review_assessment(
    db: Session,
    assessment_id: str,
    decision: str,
    notes: str,
    reviewed_risk_level: str,
) -> Assessment:
    decision = decision.strip().upper()
    notes = notes.strip()
    reviewed_risk_level = reviewed_risk_level.strip().upper()

    allowed_risk_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

    if decision not in {"APPROVE", "REJECT"}:
        raise ValueError("Decision must be APPROVE or REJECT.")

    if not notes:
        raise ValueError("Reviewer notes are required.")

    if reviewed_risk_level not in allowed_risk_levels:
        raise ValueError(
            "Reviewed risk level must be LOW, MEDIUM, HIGH, or CRITICAL."
        )

    assessment = get_assessment(db, assessment_id)
    if assessment is None:
        raise LookupError(f"Assessment not found: {assessment_id}")

    if assessment.reviewer_decision != "PENDING":
        raise ValueError("This assessment has already been reviewed.")

    assessment.reviewer_decision = decision
    assessment.reviewer_notes = notes[:2000]
    assessment.reviewed_risk_level = reviewed_risk_level
    assessment.reviewed_at = datetime.utcnow()
    assessment.assessment_status = (
        "APPROVED" if decision == "APPROVE" else "REJECTED"
    )

    db.commit()
    db.refresh(assessment)
    return assessment

