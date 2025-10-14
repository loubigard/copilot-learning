"""
Tests for unregister functionality
"""
import pytest
from fastapi import status
from app import activities


class TestUnregisterEndpoints:
    """Test class for unregister-related endpoints"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Get initial participant count
        initial_count = len(activities[activity_name]["participants"])
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was removed
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistration when participant is not registered"""
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Ensure email is not in participants
        assert email not in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from non-existent activity"""
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_url_encoding(self, client, reset_activities):
        """Test unregistration with URL-encoded parameters"""
        activity_name = "Programming Class"
        encoded_activity = "Programming%20Class"
        email = "emma@mergington.edu"  # Already registered
        encoded_email = "emma%40mergington.edu"
        
        # Verify email is initially registered
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(f"/activities/{encoded_activity}/participants/{encoded_email}")
        
        assert response.status_code == status.HTTP_200_OK
        assert email not in activities[activity_name]["participants"]

    def test_unregister_special_characters_in_email(self, client, reset_activities):
        """Test unregistration with email containing special characters"""
        activity_name = "Science Club"
        special_email = "student.with.dots+tag@mergington.edu"
        
        # First, add the special email
        activities[activity_name]["participants"].append(special_email)
        initial_count = len(activities[activity_name]["participants"])
        
        # Then unregister
        encoded_email = "student.with.dots%2Btag%40mergington.edu"
        response = client.delete(f"/activities/{activity_name}/participants/{encoded_email}")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert special_email not in activities[activity_name]["participants"]

    def test_signup_then_unregister_workflow(self, client, reset_activities):
        """Test complete workflow: signup then unregister"""
        activity_name = "Math Olympiad"
        email = "testworkflow@mergington.edu"
        
        # Initial state - participant not registered
        initial_count = len(activities[activity_name]["participants"])
        assert email not in activities[activity_name]["participants"]
        
        # Step 1: Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == status.HTTP_200_OK
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        
        # Step 2: Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count