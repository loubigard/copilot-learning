"""
Tests for activities endpoints
"""
import pytest
from fastapi import status


class TestActivitiesEndpoints:
    """Test class for activities-related endpoints"""

    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of all activities"""
        response = client.get("/activities")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that we get a dictionary of activities
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check specific activities exist
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check activity structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            
            # Check required fields
            required_fields = ["description", "schedule", "max_participants", "participants"]
            for field in required_fields:
                assert field in activity_data, f"Missing field {field} in activity {activity_name}"
            
            # Check data types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Check that max_participants is positive
            assert activity_data["max_participants"] > 0
            
            # Check that participants don't exceed max
            assert len(activity_data["participants"]) <= activity_data["max_participants"]

    def test_activities_count(self, client, reset_activities):
        """Test that we have the expected number of activities"""
        response = client.get("/activities")
        data = response.json()
        
        # We should have 9 activities in total
        assert len(data) == 9
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Club", "Art Workshop", "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data, f"Missing activity: {activity}"