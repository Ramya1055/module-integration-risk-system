from sqlalchemy.orm import Session

from database.models import ModuleProfile
from monitoring.module_profiler import profile_solidity_file


def create_module_profile(
    db: Session,
    integration_id: str,
    file_path: str,
) -> ModuleProfile:

    profile_data = profile_solidity_file(
        file_path
    )

    profile = ModuleProfile(
        integration_id=integration_id,
        module_name=profile_data["module_name"],
        source_file=profile_data["source_file"],
        source_lines=profile_data["source_lines"],
        function_count=profile_data["function_count"],
        state_variable_count=profile_data[
            "state_variable_count"
        ],
        external_call_count=profile_data[
            "external_call_count"
        ],
        event_count=profile_data["event_count"],
        modifier_count=profile_data[
            "modifier_count"
        ],
        payable_function_count=profile_data[
            "payable_function_count"
        ],
        interface_count=profile_data[
            "interface_count"
        ],
        dependency_count=profile_data[
            "dependency_count"
        ],
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile