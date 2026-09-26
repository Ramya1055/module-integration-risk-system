import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from monitoring.profile_service import (
    create_module_profile,
)


db = SessionLocal()

try:
    profile = create_module_profile(
        db=db,
        integration_id="INT-000002",
        file_path=(
            "blockchain/contracts/SafeModule.sol"
        ),
    )

    print("Module profile stored successfully.")
    print("--------------------------------")
    print(f"Profile ID: {profile.id}")
    print(
        f"Integration ID: "
        f"{profile.integration_id}"
    )
    print(
        f"Module name: "
        f"{profile.module_name}"
    )
    print(
        f"Source lines: "
        f"{profile.source_lines}"
    )
    print(
        f"Functions: "
        f"{profile.function_count}"
    )
    print(
        f"State variables: "
        f"{profile.state_variable_count}"
    )
    print(
        f"Events: "
        f"{profile.event_count}"
    )
    print(
        f"Modifiers: "
        f"{profile.modifier_count}"
    )

finally:
    db.close()