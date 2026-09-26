import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from blockchain.monitor import get_transaction_details
from blockchain.transaction_service import store_transaction


TRANSACTION_HASH = (
    "4311d6c5ce63d12d4bef0c60343ee2986b52ba7d854395ae404f7052f7ff72c7"
)


def main():
    transaction_data = get_transaction_details(
        TRANSACTION_HASH
    )

    db = SessionLocal()

    try:
        transaction = store_transaction(
            db=db,
            integration_id="INT-TEST-001",
            transaction_data=transaction_data,
        )

        print("Transaction storage successful.")
        print("--------------------------------")
        print(
            "Integration ID:",
            transaction.integration_id,
        )
        print(
            "Transaction hash:",
            transaction.transaction_hash,
        )
        print(
            "Block number:",
            transaction.block_number,
        )
        print(
            "Gas limit:",
            transaction.gas_limit,
        )
        print(
            "Gas used:",
            transaction.gas_used,
        )
        print(
            "Status:",
            transaction.status,
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()