import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_has_expected_activities(self, client):
        """Test that expected activities are in the response"""
        response = client.get("/activities")
        data = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club",
        ]
        for activity in expected_activities:
            assert activity in data

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data

    def test_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_student_returns_200(self, client):
        """Test successful signup with valid mergington.edu email"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_valid_student_returns_message(self, client):
        """Test that successful signup returns confirmation message"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_invalid_email_returns_400(self, client):
        """Test that non-mergington email is rejected"""
        response = client.post(
            "/activities/Chess Club/signup?email=invalid@example.com"
        )
        assert response.status_code == 400

    def test_signup_invalid_email_error_message(self, client):
        """Test error message for invalid email domain"""
        response = client.post(
            "/activities/Chess Club/signup?email=invalid@example.com"
        )
        data = response.json()
        assert "mergington.edu" in data["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_signup_nonexistent_activity_error_message(self, client):
        """Test error message for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that duplicate signup is rejected"""
        email = "michael@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400

    def test_signup_duplicate_email_error_message(self, client):
        """Test error message for duplicate signup"""
        email = "michael@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_at_capacity_returns_400(self, client, sample_activity_data):
        """Test that signup at max capacity is rejected"""
        # Find an activity at capacity
        for activity_name, activity_data in sample_activity_data.items():
            if len(activity_data["participants"]) >= activity_data["max_participants"]:
                response = client.post(
                    f"/activities/{activity_name}/signup?email=atcapacity@mergington.edu"
                )
                assert response.status_code == 400
                break
        else:
            # If no activity at capacity, skip this test
            pytest.skip("No activity at capacity to test")

    def test_signup_adds_to_participants_list(self, client):
        """Test that signup actually adds participant to activity"""
        email = "adding@mergington.edu"
        # Get initial state
        response_before = client.get("/activities")
        initial_count = len(response_before.json()["Art Studio"]["participants"])

        # Attempt signup
        response_signup = client.post(f"/activities/Art Studio/signup?email={email}")

        if response_signup.status_code == 200:
            # Get updated state
            response_after = client.get("/activities")
            final_count = len(response_after.json()["Art Studio"]["participants"])
            assert final_count > initial_count


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_existing_participant_returns_200(self, client):
        """Test successful removal of existing participant"""
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/participants?email={email}"
        )
        assert response.status_code == 200

    def test_remove_participant_returns_message(self, client):
        """Test that removal returns confirmation message"""
        email = "emma@mergington.edu"
        response = client.delete(
            f"/activities/Programming Class/participants?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_remove_nonexistent_activity_returns_404(self, client):
        """Test removal from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/participants?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_remove_nonexistent_activity_error_message(self, client):
        """Test error message for non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/participants?email=test@mergington.edu"
        )
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test removal of non-participant returns 404"""
        response = client.delete(
            "/activities/Chess Club/participants?email=notreal@mergington.edu"
        )
        assert response.status_code == 404

    def test_remove_nonexistent_participant_error_message(self, client):
        """Test error message for non-existent participant"""
        response = client.delete(
            "/activities/Chess Club/participants?email=notreal@mergington.edu"
        )
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_remove_actually_removes_participant(self, client):
        """Test that removal actually removes participant from activity"""
        # First add a participant
        add_email = "removeme@mergington.edu"
        client.post(f"/activities/Science Club/signup?email={add_email}")

        # Verify they're added
        response_check = client.get("/activities")
        assert add_email in response_check.json()["Science Club"]["participants"]

        # Remove the participant
        response_remove = client.delete(
            f"/activities/Science Club/participants?email={add_email}"
        )
        assert response_remove.status_code == 200

        # Verify they're removed
        response_final = client.get("/activities")
        assert add_email not in response_final.json()["Science Club"]["participants"]


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_signup_and_remove_workflow(self, client):
        """Test complete signup and removal workflow"""
        activity_name = "Tennis Club"
        email = "workflow@mergington.edu"

        # Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200

        # Verify signup
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

        # Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        assert remove_response.status_code == 200

        # Verify removal
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_multiple_signups_same_activity(self, client):
        """Test that multiple different students can signup for same activity"""
        activity_name = "Drama Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        response1 = client.post(f"/activities/{activity_name}/signup?email={email1}")
        response2 = client.post(f"/activities/{activity_name}/signup?email={email2}")

        assert response1.status_code == 200
        assert response2.status_code == 200

        activities = client.get("/activities").json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]
