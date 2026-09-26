import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from backend.app.services.integration_service import (
    record_blockchain_transaction,
)


TRANSACTION_HASH = (
    "4311d6c5ce63d12d4bef0c60343ee2986b52ba7d854395ae404f7052f7ff72c7"
)


def main():
    db = SessionLocal()

    try:
        transaction = record_blockchain_transaction(
            db=db,
            integration_id="INT-TEST-002",
            transaction_hash=TRANSACTION_HASH,
        )

        print("Integration blockchain recording successful.")
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