import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from security.analyzer import analyze_solidity_file
from security.finding_service import store_security_findings


project_root = Path(__file__).resolve().parents[1]

contract_file = (
    project_root
    / "blockchain"
    / "contracts"
    / "SecurityTestModule.sol"
)


db = SessionLocal()

try:
    findings = analyze_solidity_file(
        str(contract_file)
    )

    stored_findings = store_security_findings(
        db=db,
        integration_id="INT-TEST-001",
        findings=findings,
    )

    print("Security finding storage completed.")
    print("--------------------------------")
    print(f"Findings detected: {len(findings)}")
    print(f"Findings stored: {len(stored_findings)}")

    for finding in stored_findings:
        print("--------------------------------")
        print(f"Database ID: {finding.id}")
        print(f"Integration ID: {finding.integration_id}")
        print(f"Type: {finding.finding_type}")
        print(f"Severity: {finding.severity}")
        print(f"Location: {finding.location}")
        print(f"Evidence: {finding.evidence}")

finally:
    db.close()