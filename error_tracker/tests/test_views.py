from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from project_integrations.models import Project, APIKey
from error_tracker.models import ErrorLog, ErrorGroup


class ErrorTrackerTests(APITestCase):

    def setUp(self):
        # Create a user and project
        self.user = User.objects.create_user(username='testuser', password='password')
        self.project = Project.objects.create(name="Test Project", user=self.user)

        # Create an API key for the project
        self.api_key = APIKey.objects.create(user=self.user, project=self.project)

        # Create JWT token for the user
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # URLs
        self.error_log_list_url = reverse('error-log-list-create')
        self.error_group_list_url = reverse('error-group-list')

    def test_post_error_log_with_valid_api_key(self):
        """
        Test creating an ErrorLog with a valid APIKey associated with the project.
        """
        data = {
            "error_message": "Sample error message",
            "environment": "Production",
            "project": self.project.id,
        }
        self.client.credentials(HTTP_AUTHORIZATION='')  # Clear JWT
        self.client.credentials(HTTP_API_KEY=self.api_key.key)  # Set APIKey in headers

        response = self.client.post(self.error_log_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ErrorLog.objects.count(), 1)
        self.assertEqual(ErrorLog.objects.first().project, self.project)

    def test_post_error_log_with_invalid_api_key(self):
        """
        Test that an ErrorLog cannot be created if an invalid APIKey is provided.
        """
        another_project = Project.objects.create(name="Other Project", user=self.user)
        invalid_api_key = APIKey.objects.create(user=self.user,
                                                project=another_project)  # APIKey for a different project

        data = {
            "error_message": "Sample error message",
            "environment": "Production",
            "project": self.project.id,
        }
        self.client.credentials(HTTP_AUTHORIZATION='')  # Clear JWT
        self.client.credentials(HTTP_API_KEY=invalid_api_key.key)  # Use the invalid APIKey

        response = self.client.post(self.error_log_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ErrorLog.objects.count(), 0)

    def test_get_error_log_list_with_jwt(self):
        """
        Test that an authenticated user can list ErrorLog entries using JWT.
        """
        ErrorLog.objects.create(error_message="Test error", environment="Production", project=self.project)

        response = self.client.get(self.error_log_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_error_group_list_with_jwt(self):
        """
        Test that an authenticated user can list ErrorGroup entries using JWT.
        """
        ErrorGroup.objects.create()  # Create an ErrorGroup instance

        response = self.client.get(self.error_group_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_post_error_log_for_different_project(self):
        """
        Test that an ErrorLog cannot be created for a different project.
        """
        another_project = Project.objects.create(name="Other Project", user=self.user)

        data = {
            "error_message": "Sample error message",
            "environment": "Production",
            "project": another_project.id,
        }
        self.client.credentials(HTTP_AUTHORIZATION='')

        response = self.client.post(self.error_log_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ErrorLog.objects.count(), 0)
