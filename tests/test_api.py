from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_integrations_list_endpoint():
    response = client.get("/integrations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        item = response.json()[0]
        assert "integration_id" in item
        assert "status" in item


def test_assessments_list_endpoint():
    response = client.get("/assessments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if response.json():
        item = response.json()[0]
        assert "assessment_id" in item
        assert "integration_id" in item
        assert "risk_level" in item


def test_report_returns_404_for_unknown_integration():
    response = client.get(
        "/integrations/INT-DOES-NOT-EXIST/report"
    )
    assert response.status_code == 404