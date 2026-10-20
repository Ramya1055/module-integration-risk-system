from sqlalchemy.orm import Session

from database.models import SecurityFinding


def store_security_findings(
    db: Session,
    integration_id: str,
    findings: list[dict],
) -> list[SecurityFinding]:

    stored_findings = []

    try:
        for finding in findings:
            query = db.query(SecurityFinding).filter(
                SecurityFinding.integration_id == integration_id,
                SecurityFinding.finding_type == finding["finding_type"],
                SecurityFinding.evidence == finding.get("evidence"),
            )

            existing = query.first()

            if existing is not None:
                stored_findings.append(existing)
                continue

            security_finding = SecurityFinding(
                integration_id=integration_id,
                finding_type=finding["finding_type"],
                severity=finding["severity"],
                component=finding.get("component", "smart_contract"),
                location=finding.get("location"),
                description=finding.get("description"),
                evidence=finding.get("evidence"),
                source=finding.get("source", "security_analyzer"),
            )

            db.add(security_finding)
            stored_findings.append(security_finding)

        db.commit()

        for finding in stored_findings:
            db.refresh(finding)

        return stored_findings

    except Exception:
        db.rollback()
        raise
