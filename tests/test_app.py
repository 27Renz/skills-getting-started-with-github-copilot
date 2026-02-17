import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    global activities
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural sports",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "maya@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["james@mergington.edu"]
        },
        "Debate Team": {
            "description": "Compete in debate competitions and develop public speaking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["rachel@mergington.edu", "david@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots for competitions",
            "schedule": "Tuesdays, Thursdays, Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu"]
        }
    }
    activities.clear()
    activities.update(initial_state)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Test the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9

    def test_get_activities_includes_participants(self, client):
        """Test that returned activities include participant lists."""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        assert "participants" in chess_club
        assert "michael@mergington.edu" in chess_club["participants"]

    def test_get_activities_includes_activity_details(self, client):
        """Test that activities include all required fields."""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup adds participant to the activity."""
        email = "test@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert email in chess_club["participants"]

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that signup with duplicate email returns 400."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup for nonexistent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_increments_participant_count(self, client):
        """Test that signup increments the participant count."""
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Basketball Team"]["participants"])
        
        # Sign up a new participant
        client.post("/activities/Basketball%20Team/signup?email=newuser@mergington.edu")
        
        # Verify participant count increased
        response2 = client.get("/activities")
        new_count = len(response2.json()["Basketball Team"]["participants"])
        assert new_count == initial_count + 1


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/participants endpoint."""

    def test_unregister_success(self, client):
        """Test successful unregister from an activity."""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from the activity."""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess%20Club/participants?email={email}")
        
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        assert email not in chess_club["participants"]

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """Test that unregister of nonexistent participant returns 404."""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregister from nonexistent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent%20Activity/participants?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_decrements_participant_count(self, client):
        """Test that unregister decrements the participant count."""
        # Get initial participant count
        response1 = client.get("/activities")
        initial_count = len(response1.json()["Chess Club"]["participants"])
        
        # Unregister a participant
        client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")
        
        # Verify participant count decreased
        response2 = client.get("/activities")
        new_count = len(response2.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1


class TestIntegration:
    """Integration tests for multiple operations."""

    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signup and unregister."""
        email = "integration@mergington.edu"
        activity = "Tennis Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/participants?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]

    def test_multiple_signups_tracked_correctly(self, client):
        """Test that multiple signups are tracked correctly."""
        activity = "Drama Club"
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up multiple users
        for email in emails:
            client.post(f"/activities/{activity.replace(' ', '%20')}/signup?email={email}")
        
        # Verify all were added
        response = client.get("/activities")
        final_count = len(response.json()[activity]["participants"])
        assert final_count == initial_count + len(emails)
        
        # Verify each email is in the list
        for email in emails:
            assert email in response.json()[activity]["participants"]
