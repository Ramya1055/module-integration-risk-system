import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from database.models import BlockchainTransaction


def main():
    db = SessionLocal()

    try:
        transactions = (
            db.query(BlockchainTransaction)
            .order_by(
                BlockchainTransaction.id
            )
            .all()
        )

        print("Blockchain transaction records:")
        print("--------------------------------")

        for transaction in transactions:
            print(
                transaction.id,
                "|",
                transaction.integration_id,
                "|",
                transaction.transaction_hash,
                "| block:",
                transaction.block_number,
                "| gas:",
                transaction.gas_used,
                "| status:",
                transaction.status,
            )

        print()
        print(
            "Total transactions:",
            len(transactions),
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()