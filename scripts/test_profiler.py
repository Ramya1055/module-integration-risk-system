import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from monitoring.module_profiler import (
    profile_solidity_file,
)


solidity_file = (
    "blockchain/contracts/SafeModule.sol"
)

try:
    profile = profile_solidity_file(
        solidity_file
    )

    print("Module profiling successful.")
    print("--------------------------------")

    for key, value in profile.items():
        print(f"{key}: {value}")

except Exception as exc:
    print(f"Profiling failed: {exc}")