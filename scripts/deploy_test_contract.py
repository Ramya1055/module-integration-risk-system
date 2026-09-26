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


def main():
    # Connect to local Hardhat blockchain
    web3 = get_web3()

    # Load the compiled contract artifact
    with open(
        ARTIFACT_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        artifact = json.load(file)

    abi = artifact["abi"]
    bytecode = artifact["bytecode"]

    # Get the accounts provided by the local Hardhat node
    accounts = web3.eth.accounts

    if not accounts:
        raise RuntimeError(
            "No Hardhat accounts were found."
        )

    deployer = accounts[0]

    # Create the contract object
    contract = web3.eth.contract(
        abi=abi,
        bytecode=bytecode,
    )

    # Build the deployment transaction
    transaction = contract.constructor(
        100
    ).build_transaction(
        {
            "from": deployer,
            "nonce": web3.eth.get_transaction_count(
                deployer
            ),
            "gas": 2_000_000,
            "gasPrice": web3.eth.gas_price,
        }
    )

    # Send transaction through the local Hardhat node
    tx_hash = web3.eth.send_transaction(
        transaction
    )

    # Wait until the deployment transaction is mined
    receipt = web3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    print("Local contract deployment successful.")
    print("--------------------------------")
    print("Contract:", "SafeModule")
    print("Deployer:", deployer)
    print("Address:", receipt.contractAddress)
    print("Transaction hash:", tx_hash.hex())
    print("Block number:", receipt.blockNumber)
    print("Gas used:", receipt.gasUsed)


if __name__ == "__main__":
    main()