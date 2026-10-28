
import json
import sys
from pathlib import Path
from web3.logs import DISCARD

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from blockchain.connection import get_web3
from database.db import SessionLocal
from database.models import Integration
from blockchain.collect_onchain_events import collect_receipt_events




ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "blockchain" / "contracts"


def load_artifact(relative_path):
    path = ARTIFACTS / relative_path
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def deploy(web3, account, artifact):
    contract = web3.eth.contract(
        abi=artifact["abi"],
        bytecode=artifact["bytecode"],
    )

    tx_hash = contract.constructor().transact(
        {"from": account, "gas": 3_000_000}
    )
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        raise RuntimeError("Contract deployment failed")

    return web3.eth.contract(
        address=receipt.contractAddress,
        abi=artifact["abi"],
    )


def main(integration_id):
    web3 = get_web3()
    account = web3.eth.accounts[0]

    host_artifact = load_artifact("v2/ModuleHost.sol/ModuleHost.json")
    module_artifact = load_artifact("v2/TestModule.sol/TestModule.json")
    delegate_module_artifact = load_artifact(
    "v2/DelegatecallTestModule.sol/DelegatecallTestModule.json"
    )

    host = deploy(web3, account, host_artifact)
    db = SessionLocal()

    integration = (
        db.query(Integration)
        .filter(Integration.integration_id == integration_id)
        .first()
    )

    if integration is None:
        db.close()
        raise SystemExit(f"Integration not found: {integration_id}")

    if str(integration.status).upper() == "FINALIZED":
        db.close()
        raise SystemExit(
            f"Refusing to append test evidence to finalized integration "
            f"{integration_id}. Create a new integration first."
        )

    module = deploy(web3, account, module_artifact)
    delegate_module = deploy(web3, account, delegate_module_artifact)

    print("ModuleHost deployed:", host.address)
    print("TestModule deployed:", module.address)

    # Test 1: Successful module execution.
    success_data = module.functions.succeed(42)._encode_transaction_data()

    receipt = web3.eth.wait_for_transaction_receipt(
        host.functions.execute(module.address, success_data).transact(
            {"from": account, "gas": 1_000_000}
        )
    )
    collect_receipt_events(
        db=db,
        integration_id=integration_id,
        host_address=host.address,
        receipt=receipt,
    )
    reports = host.events.ModuleCallReport().process_receipt(receipt)

    assert receipt.status == 1, "Successful call transaction reverted"
    assert reports, "Missing ModuleCallReport event"
    assert reports[0]["args"]["success"] is True

    print("PASS: successful call produced a report event")

    # Test 2: Failed module execution.
    
    fail_data = module.functions.fail()._encode_transaction_data()

    receipt = web3.eth.wait_for_transaction_receipt(
        host.functions.execute(module.address, fail_data).transact(
            {"from": account, "gas": 1_000_000}
        )
    )

    # Save the failed-call transaction evidence to SQLite.
    collect_receipt_events(
        db=db,
        integration_id=integration_id,
        host_address=host.address,
        receipt=receipt,
    )


    reports = host.events.ModuleCallReport().process_receipt(
        receipt, errors=DISCARD
    )
    violations = host.events.InvariantViolation().process_receipt(
        receipt, errors=DISCARD
    )


    assert receipt.status == 1, "Host failed to record the module failure"
    assert reports, "Missing failure report"
    assert reports[0]["args"]["success"] is False

    assert any(
        event["args"]["violation"] == "MODULE_CALL_FAILED"
        for event in violations
    ), "Missing MODULE_CALL_FAILED violation"

    print("PASS: failed call produced a violation event")
    # Test 3: Detect storage corruption through delegatecall.
    
    corrupt_data = delegate_module.functions.corruptCanary(
        99999
    )._encode_transaction_data()

    receipt = web3.eth.wait_for_transaction_receipt(
        host.functions.executeDelegate(
            delegate_module.address,
            corrupt_data,
        ).transact({"from": account, "gas": 1_000_000})
    )

    # Save the delegatecall transaction evidence to SQLite.
    collect_receipt_events(
        db=db,
        integration_id=integration_id,
        host_address=host.address,
        receipt=receipt,
    )


    reports = host.events.ModuleCallReport().process_receipt(
        receipt, errors=DISCARD
    )
    violations = host.events.InvariantViolation().process_receipt(
        receipt, errors=DISCARD
    )



    assert receipt.status == 1, "Delegatecall transaction reverted"
    assert reports, "Missing delegatecall report"

    assert any(
        event["args"]["violation"] == "STORAGE_CANARY_CHANGED"
        for event in violations
    ), "Storage corruption was not detected"

    print("PASS: delegatecall storage corruption was detected")
    print("All ModuleHost integration tests passed.")

    db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python scripts/test_module_host.py <integration_id>"
        )
    main(sys.argv[1])
