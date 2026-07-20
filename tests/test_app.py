import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)

    activities.clear()
    activities.update(copy.deepcopy(original_state))

    yield

    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_catalog(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_with_existing_email_returns_400(client):
    # Arrange
    existing_email = activities["Chess Club"]["participants"][0]

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={existing_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_unknown_activity_returns_404(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/Unknown Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email_from_activity(client):
    # Arrange
    email = "test@mergington.edu"
    activities["Chess Club"]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/Chess Club/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_participant_returns_404_for_unknown_participant(client):
    # Arrange
    unknown_email = "unknown@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/participants/{unknown_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
