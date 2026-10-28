import json
from pathlib import Path
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
assert w3.is_connected(), "Hardhat node is not running"

account = w3.eth.accounts[0]
artifact_path = Path(
    "artifacts/blockchain/contracts/v2/AssessmentRegistry.sol/AssessmentRegistry.json"
)
artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

Registry = w3.eth.contract(
    abi=artifact["abi"],
    bytecode=artifact["bytecode"],
)

tx_hash = Registry.constructor().transact({"from": account})
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
assert receipt.status == 1, "Deployment failed"

registry = w3.eth.contract(
    address=receipt.contractAddress,
    abi=artifact["abi"],
)

module = w3.eth.accounts[1]
report_hash = Web3.keccak(text="test-report-INT-TEST-001")

tx_hash = registry.functions.recordAssessment(
    "INT-TEST-001",
    report_hash,
    1,  # LOW
    module,
    True,
).transact({"from": account})
assert w3.eth.wait_for_transaction_receipt(tx_hash).status == 1

assessment = registry.functions.getAssessment("INT-TEST-001").call()
assert assessment[0] == report_hash
assert assessment[2] is True
assert registry.functions.isModuleApproved(module).call() is True

tx_hash = registry.functions.recordAssessment(
    "INT-TEST-002",
    Web3.keccak(text="test-report-INT-TEST-002"),
    3,  # HIGH
    module,
    True,
).transact({"from": account})
assert w3.eth.wait_for_transaction_receipt(tx_hash).status == 1

high_assessment = registry.functions.getAssessment("INT-TEST-002").call()
assert high_assessment[2] is False
assert registry.functions.isModuleApproved(module).call() is False

print("PASS: Registry deployed:", receipt.contractAddress)
print("PASS: LOW-risk approval recorded")
print("PASS: HIGH-risk approval denied")
print("AssessmentRegistry tests passed.")
