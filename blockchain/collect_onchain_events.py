
import json
from pathlib import Path

from sqlalchemy.orm import Session
from web3.logs import DISCARD

from database.models import (
    OnchainObservation,
    IntegrationEvent,
    BlockchainTransaction,
    SecurityFinding,
)
from blockchain.connection import get_web3
from blockchain.transaction_service import store_transaction
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
    """Persist ModuleHost transaction, event, and finding evidence."""

    web3 = get_web3()
    artifact = load_artifact("v2/ModuleHost.sol/ModuleHost.json")

    tx_hash = receipt["transactionHash"]
    transaction_hash = tx_hash.hex()

    existing_transaction = (
        db.query(BlockchainTransaction)
        .filter(
            BlockchainTransaction.transaction_hash == transaction_hash
        )
        .first()
    )

    if existing_transaction is not None:
        if existing_transaction.integration_id != integration_id:
            raise ValueError(
                f"Transaction {transaction_hash} already belongs to "
                f"{existing_transaction.integration_id}, not {integration_id}."
            )
    else:
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
        receipt, errors=DISCARD
    )
    violations = host.events.InvariantViolation().process_receipt(
        receipt, errors=DISCARD
    )

    violations_by_call = {}
    for event in violations:
        args = event["args"]
        violations_by_call.setdefault(args["callId"], []).append(
            args["violation"]
        )

    saved = []
    findings_to_store = []

    for report in reports:
        args = report["args"]
        call_id = args["callId"]
        violation_names = violations_by_call.get(call_id, [])
        module_address = web3.to_checksum_address(args["module"])

        observation = (
            db.query(OnchainObservation)
            .filter(
                OnchainObservation.integration_id == integration_id,
                OnchainObservation.transaction_hash == transaction_hash,
                OnchainObservation.call_id == call_id,
            )
            .first()
        )

        if observation is None:
            observation = OnchainObservation(
                integration_id=integration_id,
                transaction_hash=transaction_hash,
                block_number=receipt["blockNumber"],
                host_address=host.address,
                module_address=module_address,
                call_id=call_id,
                success=args["success"],
                gas_used=args["gasUsed"],
                max_depth=args["maxDepth"],
                balance_delta=str(args["balanceDelta"]),
                violations=",".join(violation_names),
                return_data=args["returnData"].hex(),
            )
            db.add(observation)

        saved.append(observation)

        for violation in violation_names:
            event_description = (
                f"Call {call_id}: {violation}; "
                f"transaction {transaction_hash}"
            )

            existing_event = (
                db.query(IntegrationEvent)
                .filter(
                    IntegrationEvent.integration_id == integration_id,
                    IntegrationEvent.event_type
                    == "ONCHAIN_INVARIANT_VIOLATION",
                    IntegrationEvent.description == event_description,
                )
                .first()
            )

            if existing_event is None:
                db.add(
                    IntegrationEvent(
                        integration_id=integration_id,
                        event_type="ONCHAIN_INVARIANT_VIOLATION",
                        component="ModuleHost",
                        severity="INFO",
                        source="blockchain",
                        description=event_description,
                    )
                )

            if violation == "STORAGE_CANARY_CHANGED":
                evidence = (
                    f"tx={transaction_hash}; "
                    f"block={receipt['blockNumber']}; "
                    f"host={host.address}; "
                    f"module={module_address}; "
                    f"call_id={call_id}; "
                    f"violation={violation}"
                )

                existing_finding = (
                    db.query(SecurityFinding)
                    .filter(
                        SecurityFinding.integration_id == integration_id,
                        SecurityFinding.finding_type
                        == "ONCHAIN_INVARIANT_VIOLATION",
                        SecurityFinding.evidence == evidence,
                    )
                    .first()
                )

                if existing_finding is None:
                    findings_to_store.append({
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

    try:
        if findings_to_store:
            store_security_findings(
                db=db,
                integration_id=integration_id,
                findings=findings_to_store,
            )

        db.commit()

        for observation in saved:
            db.refresh(observation)

        return saved

    except Exception:
        db.rollback()
        raise
