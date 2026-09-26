import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from security.analyzer import analyze_solidity_file


project_root = Path(__file__).resolve().parents[1]

contract_file = (
    project_root
    / "blockchain"
    / "contracts"
    / "SecurityTestModule.sol"
)

findings = analyze_solidity_file(
    str(contract_file)
)

print("Security analysis completed.")
print("--------------------------------")
print(f"Contract: {contract_file.name}")
print(f"Findings detected: {len(findings)}")

for finding in findings:
    print("--------------------------------")
    print(f"Type: {finding['finding_type']}")
    print(f"Severity: {finding['severity']}")
    print(f"Location: {finding['location']}")
    print(f"Description: {finding['description']}")
    print(f"Evidence: {finding['evidence']}")