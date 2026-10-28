
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research_dataset.csv"
OUTPUT = ROOT / "stage3_reviewed_dataset.csv"

ALLOWED_LABELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
ALLOWED_DECISIONS = {"APPROVE", "REJECT"}
TRUE_VALUES = {"TRUE", "1", "YES"}
MIN_LABELLED_ROWS = 30

EXCLUDED_FEATURES = {
    "integration_id",
    "contract_address",
    "integration_created_at",
    "integration_status",
    "assessment_count",
    "assessment_status",
    "reviewer_decision",
    "reviewer_notes",
    "preliminary_risk_level",
    "risk_label",
    "risk_label_validated",
}


def normalized(value):
    return (value or "").strip().upper()


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {SOURCE}. "
            "Run scripts/export_research_dataset.py first."
        )

    with SOURCE.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []
        if not columns:
            raise ValueError("The research dataset has no column headers.")
        required = {
            "reviewer_decision",
            "risk_label",
            "risk_label_validated",
        }
        missing = required - set(columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        rows = list(reader)

    reviewed_rows = []
    rejected_unvalidated = 0
    rejected_invalid = 0

    for row in rows:
        decision = normalized(row.get("reviewer_decision"))
        label = normalized(row.get("risk_label"))
        validated = normalized(row.get("risk_label_validated")) in TRUE_VALUES

        if decision not in ALLOWED_DECISIONS or label not in ALLOWED_LABELS:
            rejected_invalid += 1
            continue
        if not validated:
            rejected_unvalidated += 1
            continue

        reviewed_rows.append((row, label))

    candidates = [
        col for col in columns if col not in EXCLUDED_FEATURES
    ]

    # Drop features with no observed values or no variation.
    # Do not replace missing observations with invented measurements.
    usable_features = []
    constant_features = []
    all_missing_features = []

    for col in candidates:
        observed = {
            (row.get(col) or "").strip()
            for row, _ in reviewed_rows
            if (row.get(col) or "").strip()
        }

        if not observed:
            all_missing_features.append(col)
        elif len(observed) == 1:
            constant_features.append(col)
        else:
            usable_features.append(col)

    output_columns = usable_features + ["risk_label"]

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=output_columns)
        writer.writeheader()
        for row, label in reviewed_rows:
            prepared = {col: row.get(col, "") for col in usable_features}
            prepared["risk_label"] = label
            writer.writerow(prepared)

    distribution = Counter(label for _, label in reviewed_rows)
    missing_cells = sum(
        not (row.get(col) or "").strip()
        for row, _ in reviewed_rows
        for col in usable_features
    )

    print("===== STAGE 3 DATA PREPARATION =====")
    print(f"Source integrations: {len(rows)}")
    print(f"Accepted validated labels: {len(reviewed_rows)}")
    print(f"Rejected unvalidated rows: {rejected_unvalidated}")
    print(f"Rejected invalid rows: {rejected_invalid}")
    print(f"Risk label distribution: {dict(distribution)}")
    print(f"Candidate features: {len(candidates)}")
    print(f"Usable varying features: {len(usable_features)}")
    print(f"Excluded constant features: {len(constant_features)}")
    print(f"Excluded all-missing features: {len(all_missing_features)}")
    print(f"Missing cells in retained features: {missing_cells}")
    print(f"Prepared dataset: {OUTPUT}")

    if constant_features:
        print("Constant features:", ", ".join(constant_features))
    if all_missing_features:
        print("All-missing features:", ", ".join(all_missing_features))

    if len(reviewed_rows) < MIN_LABELLED_ROWS or len(distribution) < 2:
        print("ML TRAINING: BLOCKED")
        print(
            "Collect more independently reviewed integrations. "
            "Do not fabricate labels to meet the threshold."
        )
    elif not usable_features:
        print("ML TRAINING: BLOCKED — no usable varying features.")
    elif missing_cells:
        print(
            "ML TRAINING: BLOCKED pending a documented, "
            "training-only missing-value preprocessing strategy."
        )
    else:
        print(
            "ML TRAINING: PRELIMINARY ONLY. Check class balance, "
            "data leakage, and evaluation design before training."
        )

    print("Reviewed labels and source evidence were not modified.")


if __name__ == "__main__":
    main()
