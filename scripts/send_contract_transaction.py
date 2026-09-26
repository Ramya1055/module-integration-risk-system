import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

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

CONTRACT_ADDRESS = (
    "0x5FbDB2315678afecb367f032d93F642f64180aa3"
)


def main():
    web3 = get_web3()

    with open(
        ARTIFACT_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        artifact = json.load(file)

    contract = web3.eth.contract(
        address=CONTRACT_ADDRESS,
        abi=artifact["abi"],
    )

    accounts = web3.eth.accounts

    if not accounts:
        raise RuntimeError(
            "No Hardhat accounts were found."
        )

    sender = accounts[0]

    current_value = contract.functions.getValue().call()

    print("Current contract value:", current_value)

    transaction = contract.functions.setValue(
        300
    ).build_transaction(
        {
            "from": sender,
            "nonce": web3.eth.get_transaction_count(
                sender
            ),
            "gas": 200_000,
            "gasPrice": web3.eth.gas_price,
        }
    )

    tx_hash = web3.eth.send_transaction(
        transaction
    )

    receipt = web3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    new_value = contract.functions.getValue().call()

    print()
    print("Contract transaction successful.")
    print("--------------------------------")
    print("Contract:", CONTRACT_ADDRESS)
    print("Function:", "setValue(200)")
    print("Transaction hash:", tx_hash.hex())
    print("Block number:", receipt.blockNumber)
    print("Gas used:", receipt.gasUsed)
    print("Status:", receipt.status)
    print("New contract value:", new_value)


if __name__ == "__main__":
    main()