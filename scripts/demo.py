import json
from pathlib import Path


REPORT_PATH = Path("reports/INT-000006_report.json")


def main():
    if not REPORT_PATH.exists():
        print("ERROR: Final report not found.")
        print(f"Expected: {REPORT_PATH}")
        return

    with open(REPORT_PATH, "r", encoding="utf-8-sig") as file:
        report = json.load(file)

    integration = report["integration"]
    module = report["module_profiles"][0]
    performance = report["performance_analysis"]

    print("=" * 70)
    print("       MODULE INTEGRATION OBSERVABILITY DEMONSTRATION")
    print("=" * 70)

    print("\n[1] INTEGRATION")
    print("-" * 70)
    print(f"Integration ID    : {integration['integration_id']}")
    print(f"Existing Module   : {integration['existing_module']}")
    print(f"Proposed Module   : {integration['proposed_module']}")
    print(f"Contract Address  : {integration['contract_address']}")
    print(f"Network           : {integration['network']}")
    print(f"Final Status      : {integration['status']}")

    print("\n[2] PROPOSED MODULE PROFILE")
    print("-" * 70)
    print(f"Module Name       : {module['module_name']}")
    print(f"Source Lines      : {module['source_lines']}")
    print(f"Functions         : {module['function_count']}")
    print(f"State Variables   : {module['state_variable_count']}")
    print(f"External Calls    : {module['external_call_count']}")
    print(f"Events            : {module['event_count']}")
    print(f"Modifiers         : {module['modifier_count']}")
    print(f"Payable Functions : {module['payable_function_count']}")
    print(f"Dependencies      : {module['dependency_count']}")

    print("\n[3] PERFORMANCE OBSERVATION")
    print("-" * 70)
    print(f"Baseline CPU      : {performance['baseline_cpu']}%")
    print(f"Average Runtime CPU: {performance['average_runtime_cpu']}%")
    print(f"CPU Change        : {performance['cpu_change']}%")
    print(f"Baseline Memory   : {performance['baseline_memory']}%")
    print(f"Average Runtime Memory: {performance['average_runtime_memory']}%")
    print(f"Memory Change     : {performance['memory_change']}%")
    print(f"Runtime Samples   : {performance['runtime_sample_count']}")
    print(f"Runtime Errors    : {performance['total_runtime_errors']}")

    print("\n[4] SECURITY ANALYSIS")
    print("-" * 70)
    findings = report["security_findings"]
    print(f"Findings Detected : {len(findings)}")

    if findings:
        for finding in findings:
            print(f"  - {finding['finding_type']}")
            print(f"    Severity : {finding['severity']}")
            print(f"    Location: {finding['location']}")
    else:
        print("No findings were detected by the implemented security rules.")

    print("\n[5] BLOCKCHAIN TRANSACTION")
    print("-" * 70)
    transactions = report["blockchain_transactions"]

    if transactions:
        tx = transactions[0]
        print(f"Transaction Hash  : {tx['transaction_hash']}")
        print(f"Block Number      : {tx['block_number']}")
        print(f"Gas Limit         : {tx['gas_limit']}")
        print(f"Gas Used          : {tx['gas_used']}")
        print(f"Transaction Status: {tx['status']}")
    else:
        print("No blockchain transaction recorded.")

    print("\n[6] EVENT HISTORY")
    print("-" * 70)

    for event in report["events"]:
        print(f"- {event['event_type']}")

    print("\n[7] FINAL REPORT")
    print("-" * 70)
    print(f"Report File       : {REPORT_PATH}")
    print(f"Report Status     : {integration['status']}")

    print("\n" + "=" * 70)
    print("                  DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()