import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "stage3_reviewed_dataset.csv"
OUTPUT_DIR = ROOT / "artifacts" / "stage3"
MODEL_PATH = OUTPUT_DIR / "risk_model.joblib"
METRICS_PATH = OUTPUT_DIR / "evaluation_metrics.json"
MIN_ROWS = 15
RANDOM_STATE = 42


def main():
    if not DATASET.exists():
        raise FileNotFoundError(
            f"{DATASET} not found. Run prepare_stage3_dataset.py first."
        )

    with DATASET.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []
        rows = list(reader)

    target = "risk_label"
    if target not in columns:
        raise ValueError(f"Required target column '{target}' is missing.")

    rows = [
        row for row in rows
        if (row.get(target) or "").strip().upper()
    ]

    print("===== STAGE 3 MODEL TRAINING =====")
    print(f"Reviewed labelled rows: {len(rows)}")
    print(f"Candidate features: {len(columns) - 1}")

    if len(rows) < MIN_ROWS:
        print(
            f"TRAINING BLOCKED: need at least {MIN_ROWS} reviewed rows; "
            f"currently have {len(rows)}."
        )
        print("No model was trained and no model artifact was written.")
        return 2

    labels = [row[target].strip().upper() for row in rows]
    from collections import Counter
    distribution = Counter(labels)
    print(f"Class distribution: {dict(distribution)}")

    if len(distribution) < 2 or min(distribution.values()) < 2:
        print(
            "TRAINING BLOCKED: each represented class needs at least "
            "two examples for a stratified hold-out evaluation."
        )
        return 2

    try:
        import numpy as np
        import joblib
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import (
            accuracy_score,
            balanced_accuracy_score,
            classification_report,
            confusion_matrix,
        )
    except ImportError as exc:
        print(
            f"Missing ML dependency: {exc}. Install requirements with "
            "python -m pip install scikit-learn joblib"
        )
        return 2

    feature_names = [col for col in columns if col != target]
    numeric_features = []
    categorical_features = []

    # Determine feature types from observed values; blanks remain missing.
    for name in feature_names:
        observed = [
            (row.get(name) or "").strip()
            for row in rows
            if (row.get(name) or "").strip()
        ]
        if observed:
            try:
                for value in observed:
                    float(value)
                numeric_features.append(name)
                continue
            except ValueError:
                pass
        categorical_features.append(name)

    X = []
    for row in rows:
        values = {}
        for name in numeric_features:
            raw = (row.get(name) or "").strip()
            try:
                values[name] = float(raw) if raw else np.nan
            except ValueError:
                values[name] = np.nan

        for name in categorical_features:
            raw = (row.get(name) or "").strip()
            values[name] = raw if raw else np.nan

        X.append(values)

    import pandas as pd
    X = pd.DataFrame(X, columns=feature_names)
    y = np.asarray(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    transformers = []
    if numeric_features:
        numeric_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
        ])
        transformers.append(("numeric", numeric_pipeline, numeric_features))

    if categorical_features:
        categorical_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ])
        transformers.append(
            ("categorical", categorical_pipeline, categorical_features)
        )

    preprocessing = ColumnTransformer(transformers=transformers)

    model = Pipeline([
        ("preprocessing", preprocessing),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )),
    ])

    # Imputation, encoding and model fitting use training data only.
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "dataset": DATASET.name,
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "feature_count": len(feature_names),
        "class_distribution": dict(distribution),
        "random_state": RANDOM_STATE,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "balanced_accuracy": float(
            balanced_accuracy_score(y_test, predictions)
        ),
        "classification_report": classification_report(
            y_test,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(
            y_test,
            predictions,
            labels=sorted(distribution),
        ).tolist(),
        "confusion_matrix_labels": sorted(distribution),
        "warning": (
            "Small research dataset. Metrics are preliminary and do not "
            "establish generalisation or production security reliability."
        ),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Balanced accuracy: {metrics['balanced_accuracy']:.3f}")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved metrics: {METRICS_PATH}")
    print("Evaluation is preliminary; inspect class-wise metrics.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
