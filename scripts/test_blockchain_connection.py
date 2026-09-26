import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from blockchain.connection import get_web3


web3 = get_web3()

print("Blockchain connection successful.")
print("--------------------------------")
print("Connected:", web3.is_connected())
print("Chain ID:", web3.eth.chain_id)
print("Latest block:", web3.eth.block_number)