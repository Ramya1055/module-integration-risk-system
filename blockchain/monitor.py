from blockchain.connection import get_web3


def get_blockchain_status() -> dict:
    web3 = get_web3()

    return {
        "connected": web3.is_connected(),
        "chain_id": web3.eth.chain_id,
        "latest_block": web3.eth.block_number,
    }


def get_latest_block() -> dict:
    web3 = get_web3()

    block_number = web3.eth.block_number
    block = web3.eth.get_block(block_number)

    return {
        "block_number": block_number,
        "timestamp": block["timestamp"],
        "transaction_count": len(
            block["transactions"]
        ),
        "gas_used": block["gasUsed"],
        "gas_limit": block["gasLimit"],
    }


def get_transaction_details(
    transaction_hash: str,
) -> dict:
    web3 = get_web3()

    transaction = web3.eth.get_transaction(
        transaction_hash
    )

    receipt = web3.eth.get_transaction_receipt(
        transaction_hash
    )

    return {
        "transaction_hash": transaction_hash,
        "from": transaction["from"],
        "to": transaction["to"],
        "block_number": transaction["blockNumber"],
        "gas": transaction["gas"],
        "gas_used": receipt["gasUsed"],
        "status": receipt["status"],
    }