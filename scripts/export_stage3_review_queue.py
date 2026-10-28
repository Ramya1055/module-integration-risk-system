import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database.db import SessionLocal
from database.models import Assessment

OUTPUT = ROOT / "stage3_review_queue_latest.csv"


def main():
    db = SessionLocal()
    try:
        assessments = db.query(Assessment).order_by(
            Assessment.created_at
        ).all()

        queue = [
            a for a in assessments
            if a.reviewer_decision not in ("APPROVE", "REJECT")
        ]

        unresolved_labels = [
            a for a in assessments
            if a.reviewer_decision in ("APPROVE", "REJECT")
            and not a.reviewed_risk_level
        ]


        fields = [
            "assessment_id",
            "integration_id",
            "assessment_status",
            "preliminary_risk_level",
            "reviewer_decision",
            "reviewed_risk_level",
            "reviewer_notes",
            "evidence_summary",
        ]

        with OUTPUT.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            for a in queue:
                writer.writerow({
                    "assessment_id": a.assessment_id,
                    "integration_id": a.integration_id,
                    "assessment_status": a.assessment_status,
                    "preliminary_risk_level": a.risk_level,
                    "reviewer_decision": a.reviewer_decision,
                    "reviewed_risk_level": a.reviewed_risk_level or "",
                    "reviewer_notes": a.reviewer_notes or "",
                    "evidence_summary": a.evidence_summary or "",
                })

        print("===== STAGE 3 REVIEW QUEUE =====")
        print("Assessments examined:", len(assessments))
        print("Assessments needing review:", len(queue))
        print("Reviewed assessments missing a risk label:", len(unresolved_labels))
        for a in unresolved_labels:
            print(
                "  -",
                a.assessment_id,
                "|",
                a.integration_id,
                "| decision:",
                a.reviewer_decision,
                "| risk label missing"
            )
        print("Exported to:", OUTPUT)
        print("Database unchanged; no labels generated.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
