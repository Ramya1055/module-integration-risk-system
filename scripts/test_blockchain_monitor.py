import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from blockchain.monitor import (
    get_blockchain_status,
    get_latest_block,
    get_transaction_details,
)


TRANSACTION_HASH = (
    "4311d6c5ce63d12d4bef0c60343ee2986b52ba7d854395ae404f7052f7ff72c7"
)


status = get_blockchain_status()
block = get_latest_block()
transaction = get_transaction_details(
    TRANSACTION_HASH
)

print("Blockchain monitor test successful.")
print("--------------------------------")
print("Connected:", status["connected"])
print("Chain ID:", status["chain_id"])
print("Latest block:", status["latest_block"])

print()
print("Latest block details:")
print("--------------------------------")
print("Block number:", block["block_number"])
print("Timestamp:", block["timestamp"])
print("Transaction count:", block["transaction_count"])
print("Gas used:", block["gas_used"])
print("Gas limit:", block["gas_limit"])

print()
print("Transaction details:")
print("--------------------------------")
print(
    "Transaction hash:",
    transaction["transaction_hash"],
)
print("From:", transaction["from"])
print("To:", transaction["to"])
print(
    "Block number:",
    transaction["block_number"],
)
print("Gas:", transaction["gas"])
print("Gas used:", transaction["gas_used"])
print("Status:", transaction["status"])