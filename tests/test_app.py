import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activity store before and after each test."""
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


@pytest.fixture
def client():
    """Create a FastAPI test client for each test."""
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_catalog(client):
    # Arrange
    # No special setup needed beyond the test client.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == (
        "Learn strategies and compete in chess tournaments"
    )


def test_signup_for_activity_adds_a_new_participant(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_participant(client):
    # Arrange
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_them_from_activity(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_participant_returns_404_when_not_found(client):
    # Arrange
    email = "not-a-student@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
