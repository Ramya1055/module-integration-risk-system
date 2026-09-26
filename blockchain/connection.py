from web3 import Web3


RPC_URL = "http://127.0.0.1:8545"


def get_web3() -> Web3:
    web3 = Web3(
        Web3.HTTPProvider(RPC_URL)
    )

    if not web3.is_connected():
        raise ConnectionError(
            f"Unable to connect to blockchain at {RPC_URL}"
        )

    return web3