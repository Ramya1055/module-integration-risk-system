from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from blockchain.assessment_registry_service import (
    publish_reviewed_assessment,
)
from database.db import SessionLocal
from database.models import Assessment
from security.assessment_service import (
    create_assessment,
    get_assessment,
    review_assessment,
)
from security.ml_prediction_service import predict_integration_risk
router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def assessment_response(assessment, db=None):
    return {
        "assessment_id": assessment.assessment_id,
        "integration_id": assessment.integration_id,
        "assessment_status": assessment.assessment_status,
        "risk_level": assessment.risk_level,
        "findings_count": assessment.findings_count,
        "evidence_summary": assessment.evidence_summary,
        "created_at": assessment.created_at,
        "reviewer_decision": assessment.reviewer_decision,
        "reviewer_notes": assessment.reviewer_notes,
        "reviewed_at": assessment.reviewed_at,
        "reviewed_risk_level": assessment.reviewed_risk_level,
        "blockchain_status": assessment.blockchain_status,
        "blockchain_registry_address": assessment.blockchain_registry_address,
        "blockchain_transaction_hash": assessment.blockchain_transaction_hash,
        "blockchain_report_hash": assessment.blockchain_report_hash,
        "blockchain_error": assessment.blockchain_error,
        "ml_result": (
            predict_integration_risk(db, assessment.integration_id)
            if db is not None
            else {
                "ml_status": "NOT_RUN",
                "ml_prediction": None,
                "ml_confidence": None,
            }
        ),

    }


@router.get("")
def list_assessments(db: Session = Depends(get_db)):
    rows = (
        db.query(Assessment)
        .order_by(Assessment.id.desc())
        .all()
    )
    return [assessment_response(item,db) for item in rows]


@router.post("/{integration_id}")
def create_assessment_endpoint(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        assessment = create_assessment(db, integration_id)
        return assessment_response(assessment,db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{assessment_id}")
def get_assessment_endpoint(
    assessment_id: str,
    db: Session = Depends(get_db),
):
    assessment = get_assessment(db, assessment_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment_response(assessment,db)


@router.post("/{assessment_id}/review")
def review_assessment_endpoint(
    assessment_id: str,
    payload: dict,
    db: Session = Depends(get_db),
):
    try:
        assessment = review_assessment(
            db=db,
            assessment_id=assessment_id,
            decision=payload.get("decision", ""),
            notes=payload.get("notes", ""),
            reviewed_risk_level=payload.get("reviewed_risk_level", ""),
        )

        try:
            blockchain_result = publish_reviewed_assessment(assessment)

            assessment.blockchain_status = blockchain_result.get(
                "onchain_status", "UNKNOWN"
            )
            assessment.blockchain_registry_address = (
                blockchain_result.get("registry_address")
            )
            assessment.blockchain_transaction_hash = (
                blockchain_result.get("transaction_hash")
            )
            assessment.blockchain_report_hash = (
                blockchain_result.get("report_hash")
            )
            assessment.blockchain_error = None

        except Exception as exc:
            blockchain_result = {
                "onchain_status": "FAILED",
                "error": str(exc),
                "module_approval": False,
            }
            assessment.blockchain_status = "FAILED"
            assessment.blockchain_error = str(exc)[:2000]

        # Persist publication success or failure separately from the review.
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        response = assessment_response(assessment, db)
        response["blockchain"] = blockchain_result
        return response

    except LookupError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
