import copy
from urllib.parse import quote_plus

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

# Keep a snapshot of initial activity data to reset state after each test.
INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: reset shared in-memory state
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities():
    # Arrange: already setup by fixture

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{quote_plus(activity)}/signup?email={quote_plus(email)}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in app_module.activities[activity]["participants"]


def test_signup_duplicate_fails():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{quote_plus(activity)}/signup?email={quote_plus(email)}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_invalid_activity_404():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Nonexistent Activity"

    # Act
    response = client.post(f"/activities/{quote_plus(activity)}/signup?email={quote_plus(email)}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{quote_plus(activity)}/participants?email={quote_plus(email)}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity}"
    assert email not in app_module.activities[activity]["participants"]


def test_remove_participant_not_found():
    # Arrange
    email = "notregistered@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{quote_plus(activity)}/participants?email={quote_plus(email)}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_remove_from_invalid_activity_404():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Nonexistent Activity"

    # Act
    response = client.delete(f"/activities/{quote_plus(activity)}/participants?email={quote_plus(email)}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
