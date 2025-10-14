"""
Tests for signup functionality
"""
import pytest
from fastapi import status
from app import activities


class TestSignupEndpoints:
    """Test class for signup-related endpoints"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Get initial participant count
        initial_count = len(activities[activity_name]["participants"])
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was added
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test signup when participant is already registered"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_url_encoding(self, client, reset_activities):
        """Test signup with URL-encoded activity name"""
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        email = "newcoder@mergington.edu"
        
        response = client.post(f"/activities/{encoded_name}/signup?email={email}")
        
        assert response.status_code == status.HTTP_200_OK
        assert email in activities[activity_name]["participants"]

    def test_signup_special_characters_in_email(self, client, reset_activities):
        """Test signup with special characters in email"""
        activity_name = "Art Workshop"
        email = "student.with.dots+tag@mergington.edu"
        # URL encode the email properly
        from urllib.parse import quote
        encoded_email = quote(email, safe='')
        
        response = client.post(f"/activities/{activity_name}/signup?email={encoded_email}")
        
        assert response.status_code == status.HTTP_200_OK
        assert email in activities[activity_name]["participants"]

    def test_signup_capacity_check(self, client, reset_activities):
        """Test that signup respects capacity limits"""
        # Create a small activity for testing
        test_activity = "Test Activity"
        activities[test_activity] = {
            "description": "Test activity with limited capacity",
            "schedule": "Test schedule",
            "max_participants": 2,
            "participants": ["student1@mergington.edu"]
        }
        
        # Should be able to add one more participant
        response = client.post(f"/activities/{test_activity}/signup?email=student2@mergington.edu")
        assert response.status_code == status.HTTP_200_OK
        
        # Activity should now be at capacity
        assert len(activities[test_activity]["participants"]) == 2
        
        # Clean up test activity
        del activities[test_activity]