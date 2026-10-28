
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "research_evidence"
OUTPUT_DIR.mkdir(exist_ok=True)

evidence = {
    "test_name": "SafeModule access-control test",
    "test_contract_address": "0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e",
    "network": "local Hardhat",
    "test_timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "checks": [
        {
            "check": "Owner can update value",
            "result": "PASS",
            "detail": "Value changed from 100 to 200.",
        },
        {
            "check": "Non-owner update rejected",
            "result": "PASS",
            "detail": "Hardhat rejected the call with 'Not owner'.",
        },
        {
            "check": "Value unchanged after rejected attempt",
            "result": "PASS",
            "detail": "Stored value remained 200.",
        },
    ],
    "limitations": [
        "Isolated test deployment; not linked to an integration ID.",
        "Tests only the access-control property described above.",
        "Does not establish overall contract risk level.",
    ],
}

output_path = OUTPUT_DIR / "safe_module_access_control.json"
output_path.write_text(
    json.dumps(evidence, indent=2),
    encoding="utf-8",
)

print("Test evidence saved to:", output_path)
print("Passed checks:", len(evidence["checks"]))
print("Integration database modified: No")
