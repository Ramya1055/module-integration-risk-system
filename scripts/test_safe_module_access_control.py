
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from blockchain.connection import get_web3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "blockchain"
    / "contracts"
    / "SafeModule.sol"
    / "SafeModule.json"
)


def send_transaction(web3, tx):
    tx_hash = web3.eth.send_transaction(tx)
    return web3.eth.wait_for_transaction_receipt(tx_hash)


def main():
    web3 = get_web3()
    accounts = web3.eth.accounts

    if len(accounts) < 2:
        raise RuntimeError("At least two Hardhat accounts are required.")

    with open(ARTIFACT_PATH, "r", encoding="utf-8") as file:
        artifact = json.load(file)

    # Deploy a fresh contract for this isolated test.

    # Use the existing contract associated with INT-000012.
    contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

    contract = web3.eth.contract(
        address=web3.to_checksum_address(contract_address),
        abi=artifact["abi"],
    )

    owner = accounts[0]
    non_owner = accounts[1]

    actual_owner = contract.functions.owner().call()
    if actual_owner.lower() != owner.lower():
        raise RuntimeError(
            f"Owner mismatch: contract owner is {actual_owner}, "
            f"but the expected test account is {owner}. "
            "No transaction was sent."
        )

    original_value = contract.functions.value().call()
    test_value = original_value + 1

    print("Existing contract:", contract.address)
    print("Verified owner:", actual_owner)
    print("Original value:", original_value)



    # Test 1: owner should successfully update the value.
    owner_tx = contract.functions.setValue(test_value).build_transaction({
        "from": owner,
        "nonce": web3.eth.get_transaction_count(owner),
        "gas": 200_000,
        "gasPrice": web3.eth.gas_price,
    })
    owner_receipt = send_transaction(web3, owner_tx)

    assert owner_receipt.status == 1, "Owner update unexpectedly failed."
    assert contract.functions.value().call() == test_value
    print("Owner transaction hash:", owner_receipt.transactionHash.hex())
    print("PASS: Owner can update the value.")

    # Test 2: non-owner must be rejected.
    value_before = contract.functions.value().call()

    unauthorized_tx = contract.functions.setValue(999).build_transaction({
        "from": non_owner,
        "nonce": web3.eth.get_transaction_count(non_owner),
        "gas": 200_000,
        "gasPrice": web3.eth.gas_price,
    })

    try:
        unauthorized_receipt = send_transaction(web3, unauthorized_tx)
        unauthorized_reverted = unauthorized_receipt.status == 0
    except Exception as exc:
        # Hardhat may reject a reverting transaction before returning a receipt.
        if "Not owner" not in str(exc):
            raise
        unauthorized_reverted = True

    assert unauthorized_reverted, (
        "SECURITY FAILURE: non-owner update was not rejected."
    )
    assert contract.functions.value().call() == value_before, (
        "SECURITY FAILURE: value changed after unauthorized transaction."
    )

    print("PASS: Non-owner update was rejected.")
    print("PASS: Value remained unchanged after rejection.")
    print("Unauthorized transaction rejected before receipt was returned.")
    print("All SafeModule access-control tests passed.")


if __name__ == "__main__":
    main()
