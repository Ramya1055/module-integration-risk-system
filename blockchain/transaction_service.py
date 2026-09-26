from sqlalchemy.orm import Session

from database.models import BlockchainTransaction


def store_transaction(
    db: Session,
    integration_id: str,
    transaction_data: dict,
) -> BlockchainTransaction:
    transaction = BlockchainTransaction(
        integration_id=integration_id,
        transaction_hash=transaction_data[
            "transaction_hash"
        ],
        from_address=transaction_data.get(
            "from"
        ),
        to_address=transaction_data.get(
            "to"
        ),
        block_number=transaction_data.get(
            "block_number"
        ),
        gas_limit=transaction_data.get(
            "gas"
        ),
        gas_used=transaction_data.get(
            "gas_used"
        ),
        status=transaction_data.get(
            "status"
        ),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction