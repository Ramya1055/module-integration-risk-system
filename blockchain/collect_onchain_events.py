
import json
from pathlib import Path
from web3.logs import DISCARD
from sqlalchemy.orm import Session

from database.models import OnchainObservation, IntegrationEvent
from database.models import BlockchainTransaction, SecurityFinding
from blockchain.transaction_service import store_transaction
from blockchain.connection import get_web3
from security.finding_service import store_security_findings


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "blockchain" / "contracts"


def load_artifact(relative_path: str) -> dict:
    path = ARTIFACTS / relative_path
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def collect_receipt_events(
    db: Session,
    integration_id: str,
    host_address: str,
    receipt,
) -> list[OnchainObservation]:
    """Persist ModuleHost evidence from a real transaction receipt."""

    web3 = get_web3()
    artifact = load_artifact("v2/ModuleHost.sol/ModuleHost.json")

    # Save the blockchain transaction as well as its decoded events.
    tx_hash = receipt["transactionHash"]
    transaction_hash = tx_hash.hex()

    existing_transaction = (
        db.query(BlockchainTransaction)
        .filter(
            BlockchainTransaction.transaction_hash == transaction_hash
        )
        .first()
    )

    if existing_transaction is None:
        tx = web3.eth.get_transaction(tx_hash)

        store_transaction(
            db=db,
            integration_id=integration_id,
            transaction_data={
                "transaction_hash": transaction_hash,
                "from": tx["from"],
                "to": tx["to"],
                "block_number": receipt["blockNumber"],
                "gas": tx["gas"],
                "gas_used": receipt["gasUsed"],
                "status": receipt["status"],
            },
        )

    host = web3.eth.contract(
        address=web3.to_checksum_address(host_address),
        abi=artifact["abi"],
    )

    reports = host.events.ModuleCallReport().process_receipt(
        receipt,
        errors=DISCARD,
    )
    violations = host.events.InvariantViolation().process_receipt(
        receipt,
        errors=DISCARD,
    )

    violations_by_call = {}
    for event in violations:
        args = event["args"]
        violations_by_call.setdefault(args["callId"], []).append(
            args["violation"]
        )

    saved = []
    security_findings_to_store = []

    for report in reports:
        args = report["args"]
        call_id = args["callId"]
        violation_names = violations_by_call.get(call_id, [])

        observation = OnchainObservation(
            integration_id=integration_id,
            transaction_hash=receipt["transactionHash"].hex(),
            block_number=receipt["blockNumber"],
            host_address=host.address,
            module_address=web3.to_checksum_address(args["module"]),
            call_id=call_id,
            success=args["success"],
            gas_used=args["gasUsed"],
            max_depth=args["maxDepth"],
            balance_delta=str(args["balanceDelta"]),
            violations=",".join(violation_names),
            return_data=args["returnData"].hex(),
        )

        db.add(observation)

        for violation in violation_names:
            tx_hash_text = receipt["transactionHash"].hex()
            module_address = web3.to_checksum_address(args["module"])

            db.add(
                IntegrationEvent(
                    integration_id=integration_id,
                    event_type="ONCHAIN_INVARIANT_VIOLATION",
                    component="ModuleHost",
                    severity="INFO",
                    source="blockchain",
                    description=(
                        f"Call {call_id}: {violation}; "
                        f"transaction {tx_hash_text}"
                    ),
                )
            )

            # Record the observed invariant violation as a finding.
            # This is evidence for investigation, not proof of exploitability.
            if violation == "STORAGE_CANARY_CHANGED":
                evidence = (
                    f"tx={tx_hash_text}; "
                    f"block={receipt['blockNumber']}; "
                    f"host={host.address}; "
                    f"module={module_address}; "
                    f"call_id={call_id}; "
                    f"violation={violation}"
                )

                security_findings_to_store.append({
                    "finding_type": "ONCHAIN_INVARIANT_VIOLATION",
                    "severity": "WARNING",
                    "component": "ModuleHost",
                    "location": f"{module_address}:call-{call_id}",
                    "description": (
                        "ModuleHost detected a storage-canary invariant "
                        "change during module execution. Investigate the "
                        "execution context and affected storage before "
                        "concluding that a vulnerability is exploitable."
                    ),
                    "evidence": evidence,
                    "source": "blockchain",
                })

        saved.append(observation)

    # Avoid inserting the same finding again if this receipt is reprocessed.
    new_findings = []
    for finding in security_findings_to_store:
        existing_finding = (
            db.query(SecurityFinding)
            .filter(
                SecurityFinding.integration_id == integration_id,
                SecurityFinding.finding_type == finding["finding_type"],
                SecurityFinding.evidence == finding["evidence"],
            )
            .first()
        )

        if existing_finding is None:
            new_findings.append(finding)

    if new_findings:
        store_security_findings(
            db=db,
            integration_id=integration_id,
            findings=new_findings,
        )

    db.commit()

    for observation in saved:
        db.refresh(observation)

    return saved
