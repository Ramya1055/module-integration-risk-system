import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from database.db import SessionLocal
from database.models import ModuleProfile


db = SessionLocal()

try:
    profiles = (
        db.query(ModuleProfile)
        .order_by(ModuleProfile.id)
        .all()
    )

    print(
        f"Module profiles found: {len(profiles)}"
    )

    for profile in profiles:
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
            f"Source file: "
            f"{profile.source_file}"
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
            f"External calls: "
            f"{profile.external_call_count}"
        )
        print(
            f"Events: "
            f"{profile.event_count}"
        )
        print(
            f"Modifiers: "
            f"{profile.modifier_count}"
        )
        print(
            f"Payable functions: "
            f"{profile.payable_function_count}"
        )
        print(
            f"Interfaces: "
            f"{profile.interface_count}"
        )
        print(
            f"Dependencies: "
            f"{profile.dependency_count}"
        )

finally:
    db.close()