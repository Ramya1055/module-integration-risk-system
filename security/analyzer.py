import re
from pathlib import Path


def analyze_solidity_file(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Solidity file not found: {file_path}"
        )

    if path.suffix.lower() != ".sol":
        raise ValueError(
            "The security analyzer expects a Solidity (.sol) file."
        )

    source = path.read_text(encoding="utf-8")

    findings = []

    lines = source.splitlines()

    for line_number, line in enumerate(lines, start=1):

        stripped = line.strip()

        if re.search(
            r"\.\s*delegatecall\s*\(",
            stripped,
        ):
            findings.append(
                {
                    "finding_type": "DELEGATECALL_USAGE",
                    "severity": "WARNING",
                    "location": f"line {line_number}",
                    "description": (
                        "delegatecall usage was detected in the "
                        "Solidity source."
                    ),
                    "evidence": stripped,
                }
            )

        if re.search(
            r"\.\s*(call|send|transfer)\s*\(",
            stripped,
        ):
            findings.append(
                {
                    "finding_type": "EXTERNAL_CALL_USAGE",
                    "severity": "INFO",
                    "location": f"line {line_number}",
                    "description": (
                        "An external call operation was detected "
                        "in the Solidity source."
                    ),
                    "evidence": stripped,
                }
            )

    return findings