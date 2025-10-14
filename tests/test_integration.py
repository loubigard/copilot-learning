"""
Integration tests for the complete application workflow
"""
import pytest
from fastapi import status
from app import activities


class TestIntegrationWorkflows:
    """Test complete user workflows"""

    def test_complete_student_journey(self, client, reset_activities):
        """Test a complete student journey: view activities, sign up, view updated list, unregister"""
        student_email = "integration.test@mergington.edu"
        activity_name = "Drama Club"
        
        # Step 1: View all activities
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        initial_data = response.json()
        
        # Verify the activity exists and student is not registered
        assert activity_name in initial_data
        assert student_email not in initial_data[activity_name]["participants"]
        initial_count = len(initial_data[activity_name]["participants"])
        
        # Step 2: Sign up for an activity
        signup_response = client.post(f"/activities/{activity_name}/signup?email={student_email}")
        assert signup_response.status_code == status.HTTP_200_OK
        signup_data = signup_response.json()
        assert "message" in signup_data
        
        # Step 3: Verify signup by fetching activities again
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        updated_data = response.json()
        
        assert student_email in updated_data[activity_name]["participants"]
        assert len(updated_data[activity_name]["participants"]) == initial_count + 1
        
        # Step 4: Unregister from the activity
        unregister_response = client.delete(f"/activities/{activity_name}/participants/{student_email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        unregister_data = unregister_response.json()
        assert "message" in unregister_data
        
        # Step 5: Verify unregistration
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        final_data = response.json()
        
        assert student_email not in final_data[activity_name]["participants"]
        assert len(final_data[activity_name]["participants"]) == initial_count

    def test_multiple_students_same_activity(self, client, reset_activities):
        """Test multiple students signing up for the same activity"""
        activity_name = "Basketball Club"
        students = [
            "student1.integration@mergington.edu",
            "student2.integration@mergington.edu",
            "student3.integration@mergington.edu"
        ]
        
        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data[activity_name]["participants"])
        
        # Sign up all students
        for student_email in students:
            signup_response = client.post(f"/activities/{activity_name}/signup?email={student_email}")
            assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify all students are registered
        response = client.get("/activities")
        updated_data = response.json()
        
        for student_email in students:
            assert student_email in updated_data[activity_name]["participants"]
        
        assert len(updated_data[activity_name]["participants"]) == initial_count + len(students)
        
        # Unregister one student
        unregister_response = client.delete(f"/activities/{activity_name}/participants/{students[0]}")
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Verify only one student was removed
        response = client.get("/activities")
        final_data = response.json()
        
        assert students[0] not in final_data[activity_name]["participants"]
        assert students[1] in final_data[activity_name]["participants"]
        assert students[2] in final_data[activity_name]["participants"]
        assert len(final_data[activity_name]["participants"]) == initial_count + len(students) - 1

    def test_student_multiple_activities(self, client, reset_activities):
        """Test one student signing up for multiple activities"""
        student_email = "multi.activity@mergington.edu"
        activities_to_join = ["Science Club", "Math Olympiad", "Art Workshop"]
        
        # Sign up for multiple activities
        for activity_name in activities_to_join:
            signup_response = client.post(f"/activities/{activity_name}/signup?email={student_email}")
            assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify student is in all activities
        response = client.get("/activities")
        data = response.json()
        
        for activity_name in activities_to_join:
            assert student_email in data[activity_name]["participants"]
        
        # Unregister from one activity
        unregister_response = client.delete(f"/activities/{activities_to_join[0]}/participants/{student_email}")
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Verify student is removed from only that activity
        response = client.get("/activities")
        final_data = response.json()
        
        assert student_email not in final_data[activities_to_join[0]]["participants"]
        assert student_email in final_data[activities_to_join[1]]["participants"]
        assert student_email in final_data[activities_to_join[2]]["participants"]

    def test_activity_capacity_tracking(self, client, reset_activities):
        """Test that activity capacity is properly tracked"""
        # Find an activity with available spots
        response = client.get("/activities")
        data = response.json()
        
        # Use Chess Club (max 12, currently has 2)
        activity_name = "Chess Club"
        activity_data = data[activity_name]
        initial_participants = len(activity_data["participants"])
        max_participants = activity_data["max_participants"]
        available_spots = max_participants - initial_participants
        
        assert available_spots > 0, "Need an activity with available spots for this test"
        
        # Sign up students until we approach capacity
        test_students = []
        for i in range(min(3, available_spots)):  # Add up to 3 students or fill remaining spots
            student_email = f"capacity.test.{i}@mergington.edu"
            test_students.append(student_email)
            
            signup_response = client.post(f"/activities/{activity_name}/signup?email={student_email}")
            assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify participants were added
        response = client.get("/activities")
        updated_data = response.json()
        current_count = len(updated_data[activity_name]["participants"])
        
        assert current_count == initial_participants + len(test_students)
        assert current_count <= max_participants
        
        # Calculate remaining spots
        spots_left = max_participants - current_count
        assert spots_left >= 0