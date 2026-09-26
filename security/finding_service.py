from sqlalchemy.orm import Session

from database.models import SecurityFinding


def store_security_findings(
    db: Session,
    integration_id: str,
    findings: list[dict],
) -> list[SecurityFinding]:

    stored_findings = []

    for finding in findings:

        security_finding = SecurityFinding(
            integration_id=integration_id,
            finding_type=finding["finding_type"],
            severity=finding["severity"],
            component="smart_contract",
            location=finding.get("location"),
            description=finding.get("description"),
            evidence=finding.get("evidence"),
            source="security_analyzer",
        )

        db.add(security_finding)
        stored_findings.append(security_finding)

    db.commit()

    for finding in stored_findings:
        db.refresh(finding)

    return stored_findings