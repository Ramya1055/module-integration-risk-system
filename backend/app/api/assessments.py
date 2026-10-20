from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import SessionLocal
from security.assessment_service import (
    create_assessment,
    get_assessment,
    review_assessment,
)

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


def assessment_response(assessment):
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
    }


@router.post("/{integration_id}")
def create_assessment_endpoint(
    integration_id: str,
    db: Session = Depends(get_db),
):
    try:
        assessment = create_assessment(db, integration_id)
        return assessment_response(assessment)
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
    return assessment_response(assessment)

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
        return assessment_response(assessment)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
