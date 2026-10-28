from types import SimpleNamespace

import pytest

from database.models import OnchainObservation, PerformanceAnalysis
from security import assessment_service as service


class QueryStub:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None


class FakeDB:
    def __init__(self, observations=None, performance=None):
        self.observations = observations or []
        self.performance = performance or []

    def query(self, model):
        if model is OnchainObservation:
            return QueryStub(self.observations)
        if model is PerformanceAnalysis:
            return QueryStub(self.performance)
        raise AssertionError(f"Unexpected model queried: {model}")


def test_no_evidence_is_unassessed():
    result = service._classify_risk(
        FakeDB(),
        "INT-TEST",
        [],
    )
    assert result == "UNASSESSED"


def test_failed_call_is_preliminary_risk_not_a_confirmed_vulnerability():
    observation = SimpleNamespace(violations="MODULE_CALL_FAILED")

    result = service._classify_risk(
        FakeDB(observations=[observation]),
        "INT-TEST",
        [],
    )

    # Current rules assign MEDIUM for a recorded violation.
    # This is a preliminary classification, not proof of exploitation.
    assert result == "MEDIUM"


def test_review_rejects_invalid_decision(monkeypatch):
    assessment = SimpleNamespace(reviewer_decision="PENDING")
    monkeypatch.setattr(
        service, "get_assessment", lambda db, assessment_id: assessment
    )

    with pytest.raises(ValueError, match="Decision must be APPROVE or REJECT"):
        service.review_assessment(
            db=object(),
            assessment_id="ASM-TEST",
            decision="MAYBE",
            notes="Reviewed",
            reviewed_risk_level="LOW",
        )


def test_review_requires_valid_risk_level(monkeypatch):
    assessment = SimpleNamespace(reviewer_decision="PENDING")
    monkeypatch.setattr(
        service, "get_assessment", lambda db, assessment_id: assessment
    )

    with pytest.raises(ValueError, match="Reviewed risk level must be"):
        service.review_assessment(
            db=object(),
            assessment_id="ASM-TEST",
            decision="APPROVE",
            notes="Reviewed evidence",
            reviewed_risk_level="UNASSESSED",
        )


def test_valid_review_records_label_separately_from_preliminary_level(
    monkeypatch,
):
    assessment = SimpleNamespace(
        reviewer_decision="PENDING",
        risk_level="MEDIUM",
        reviewer_notes=None,
        reviewed_risk_level=None,
        reviewed_at=None,
        assessment_status="PENDING_REVIEW",
    )
    monkeypatch.setattr(
        service, "get_assessment", lambda db, assessment_id: assessment
    )

    class CommitDB:
        def commit(self):
            pass

        def refresh(self, item):
            pass

    result = service.review_assessment(
        db=CommitDB(),
        assessment_id="ASM-TEST",
        decision="APPROVE",
        notes="Reviewed the recorded evidence.",
        reviewed_risk_level="HIGH",
    )

    assert result.risk_level == "MEDIUM"
    assert result.reviewed_risk_level == "HIGH"
    assert result.reviewer_decision == "APPROVE"
    assert result.assessment_status == "APPROVED"
    assert result.reviewed_at is not None


def test_assessment_cannot_be_reviewed_twice(monkeypatch):
    assessment = SimpleNamespace(reviewer_decision="APPROVE")
    monkeypatch.setattr(
        service, "get_assessment", lambda db, assessment_id: assessment
    )

    with pytest.raises(ValueError, match="already been reviewed"):
        service.review_assessment(
            db=object(),
            assessment_id="ASM-TEST",
            decision="REJECT",
            notes="Second review",
            reviewed_risk_level="LOW",
        )
