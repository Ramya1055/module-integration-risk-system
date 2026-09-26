import re
from pathlib import Path


def profile_solidity_file(file_path: str) -> dict:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Solidity file not found: {file_path}"
        )

    if path.suffix.lower() != ".sol":
        raise ValueError(
            "The profiler expects a Solidity (.sol) file."
        )

    source = path.read_text(
        encoding="utf-8"
    )

    source_lines = len(
        source.splitlines()
    )

    function_matches = re.findall(
        r"\bfunction\s+\w+\s*\(",
        source,
    )

    state_variable_pattern = re.compile(
        r"^\s*(?:"
        r"uint(?:8|16|32|64|128|256)?|"
        r"int(?:8|16|32|64|128|256)?|"
        r"address|"
        r"bool|"
        r"string|"
        r"bytes(?:[1-9]|[12][0-9]|3[0-2])?"
        r")"
        r"(?:\s+(?:public|private|internal|constant|immutable))*"
        r"\s+\w+\s*(?:=[^;]+)?;",
        re.MULTILINE,
    )

    state_variable_matches = []

    brace_depth = 0
    inside_function = False

    for line in source.splitlines():

        stripped = line.strip()

        if re.search(
            r"\bfunction\s+\w+\s*\(",
            stripped,
        ):
            inside_function = True

        if not inside_function and brace_depth == 1:
            if state_variable_pattern.match(line):
                state_variable_matches.append(line)

        opening_braces = line.count("{")
        closing_braces = line.count("}")

        brace_depth += opening_braces
        brace_depth -= closing_braces

        if inside_function and brace_depth <= 1:
            inside_function = False

    event_matches = re.findall(
        r"\bevent\s+\w+\s*\(",
        source,
    )

    modifier_matches = re.findall(
        r"\bmodifier\s+\w+\s*\(",
        source,
    )

    payable_function_matches = re.findall(
        r"\bfunction\s+\w+\s*\([^)]*\)[^{;]*\bpayable\b",
        source,
    )

    external_call_matches = re.findall(
        r"\.\s*(?:call|delegatecall|staticcall|transfer|send)\s*\(",
        source,
    )

    interface_matches = re.findall(
        r"\binterface\s+\w+",
        source,
    )

    import_matches = re.findall(
        r'\bimport\s+["\']([^"\']+)["\']',
        source,
    )

    contract_matches = re.findall(
        r"\bcontract\s+(\w+)",
        source,
    )

    return {
        "module_name": (
            contract_matches[0]
            if contract_matches
            else path.stem
        ),
        "source_file": str(path.resolve()),
        "source_lines": source_lines,
        "function_count": len(function_matches),
        "state_variable_count": len(
            state_variable_matches
        ),
        "external_call_count": len(
            external_call_matches
        ),
        "event_count": len(event_matches),
        "modifier_count": len(modifier_matches),
        "payable_function_count": len(
            payable_function_matches
        ),
        "interface_count": len(interface_matches),
        "dependency_count": len(import_matches),
    }