import json
from pathlib import Path

from web3 import Web3
from blockchain.connection import get_web3


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts" / "blockchain" / "contracts"
    / "v2" / "AssessmentRegistry.sol" / "AssessmentRegistry.json"
)

# Latest address printed by test_assessment_registry.py.
REGISTRY_ADDRESS = "0x5FC8d32690cc91D4c39d9d3abcBD16989F875707"

RISK_VALUES = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}



def publish_reviewed_assessment(assessment):
    if assessment.reviewer_decision not in {"APPROVE", "REJECT"}:
        raise ValueError(
            "Only an explicitly reviewed assessment can be published."
        )

    if assessment.assessment_status not in {"APPROVED", "REJECTED"}:
        raise ValueError(
            "Assessment must have a completed review before publication."
        )

    web3 = get_web3()

    if not ARTIFACT.exists():
        raise FileNotFoundError(f"Registry artifact not found: {ARTIFACT}")

    registry_address = web3.to_checksum_address(REGISTRY_ADDRESS)

    if not web3.eth.get_code(registry_address):
        raise RuntimeError(
            "AssessmentRegistry is not deployed at the configured address. "
            "Check the Hardhat node and deploy the registry again."
        )

    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    registry = web3.eth.contract(
        address=registry_address,
        abi=artifact["abi"],
    )
    existing = registry.functions.getAssessment(
        assessment.assessment_id
    ).call()

    if existing[5]:
        raise ValueError(
            "This assessment ID is already recorded on-chain; "
            "refusing to overwrite the existing record."
        )
    risk = (assessment.reviewed_risk_level or "").strip().upper()
    if risk not in RISK_VALUES:
        raise ValueError(f"Unsupported reviewed risk level: {risk}")

    if not assessment.assessment_id:
        raise ValueError("Assessment ID is required for publication.")

    evidence = assessment.evidence_summary or assessment.assessment_id
    report_hash = Web3.keccak(text=evidence)
    zero_address = "0x0000000000000000000000000000000000000000"

    account = web3.eth.accounts[0]
    tx_hash = registry.functions.recordAssessment(
        assessment.assessment_id,
        report_hash,
        RISK_VALUES[risk],
        zero_address,
        False,
    ).transact({"from": account})

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status != 1:
        raise RuntimeError("AssessmentRegistry transaction failed.")

    return {
        "onchain_status": "RECORDED",
        "registry_address": registry_address,
        "transaction_hash": tx_hash.hex(),
        "report_hash": report_hash.hex(),
        "module_approval": False,
    }
