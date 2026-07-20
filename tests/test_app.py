from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]

    signup_response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert signup_response.status_code == 200

    delete_response = client.delete("/activities/Chess Club/participants/test@mergington.edu")
    assert delete_response.status_code == 200
    assert "test@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_participant_returns_404_for_unknown_participant():
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]

    response = client.delete("/activities/Chess Club/participants/unknown@mergington.edu")
    assert response.status_code == 404
