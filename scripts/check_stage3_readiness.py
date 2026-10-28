import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "stage3_reviewed_dataset.csv"
TARGET = "risk_label"
MIN_LABELLED_ROWS = 30


def main():
    if not DATASET.exists():
        raise FileNotFoundError(
            f"Prepared dataset not found: {DATASET}. "
            "Run prepare_stage3_dataset.py first."
        )

    with DATASET.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []
        rows = list(reader)

    if not rows:
        raise ValueError("Dataset is empty.")
    if TARGET not in columns:
        raise ValueError(f"Missing target column: {TARGET}")

    features = [column for column in columns if column != TARGET]
    labelled_rows = [
        row for row in rows if (row.get(TARGET) or "").strip()
    ]
    labels = Counter(
        (row.get(TARGET) or "").strip().upper()
        for row in labelled_rows
    )

    constant_features = [
        col for col in features
        if len({
            (row.get(col) or "").strip()
            for row in labelled_rows
        }) <= 1
    ]

    missing_features = [
        col for col in features
        if any(
            not (row.get(col) or "").strip()
            for row in labelled_rows
        )
    ]

    duplicate_groups = sum(
        count > 1
        for count in Counter(
            tuple((row.get(col) or "").strip() for col in features)
            for row in labelled_rows
        ).values()
    )

    print("===== STAGE 3 READINESS REPORT =====")
    print(f"Total rows: {len(rows)}")
    print(f"Labelled rows: {len(labelled_rows)}")
    print(f"Unlabelled rows: {len(rows) - len(labelled_rows)}")
    print(f"Feature count: {len(features)}")
    print(f"Risk label distribution: {dict(labels)}")
    print(f"Repeated feature groups: {duplicate_groups}")
    print(f"Constant features: {len(constant_features)}")
    print(f"Features containing missing values: {len(missing_features)}")

    if constant_features:
        print("Constant feature names:", ", ".join(constant_features))
    if missing_features:
        print("Features with missing values:", ", ".join(missing_features))

    blockers = []

    if len(labelled_rows) < MIN_LABELLED_ROWS:
        blockers.append(
            f"Need at least {MIN_LABELLED_ROWS} reviewed rows; "
            f"currently have {len(labelled_rows)}."
        )
    if len(labels) < 2:
        blockers.append("At least two distinct risk classes are required.")
    if not features:
        blockers.append("No input features are available.")
    if features and len(constant_features) == len(features):
        blockers.append("All input features are constant.")
    if missing_features:
        blockers.append(
            "Missing feature values require documented preprocessing. "
            "Fit any imputer on training data only; do not replace "
            "unknown measurements with zero by default."
        )

    if blockers:
        print("\nTraining readiness: BLOCKED")
        for blocker in blockers:
            print(f"- {blocker}")
        print(
            "Collect independently reviewed integrations and resolve "
            "data-quality blockers before training or evaluation."
        )
    else:
        print("\nTraining readiness: PRELIMINARY")
        print(
            "Check class balance, data leakage, and split strategy "
            "before training and evaluating a model."
        )


if __name__ == "__main__":
    main()
