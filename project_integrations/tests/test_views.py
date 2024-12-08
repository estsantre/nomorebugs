from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from project_integrations.models import Project, APIKey
from uuid import uuid4


class ProjectIntegrationTests(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password')

        # Generate token for the user
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # URL paths for project list/create and detail endpoints
        self.project_list_url = reverse('project_list_create')

    def test_create_project(self):
        """Test creating a project."""
        data = {'name': 'Test Project'}
        response = self.client.post(self.project_list_url, data, format='json')

        # Check if the response is successful and project is created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Project')
        self.assertEqual(Project.objects.count(), 1)

    def test_list_projects(self):
        """Test listing all projects for the authenticated user."""
        # Create multiple projects
        Project.objects.create(name='Project 1', user=self.user)
        Project.objects.create(name='Project 2', user=self.user)

        response = self.client.get(self.project_list_url)

        # Ensure correct projects are returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Project 1')
        self.assertEqual(response.data[1]['name'], 'Project 2')

    def test_retrieve_project(self):
        """Test retrieving a single project by ID."""
        project = Project.objects.create(name='Retrieve Test Project', user=self.user)
        project_detail_url = reverse('project_detail', args=[project.id])

        response = self.client.get(project_detail_url)

        # Check if the project is retrieved correctly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Retrieve Test Project')

    def test_update_project(self):
        """Test updating an existing project."""
        project = Project.objects.create(name='Old Project Name', user=self.user)
        project_detail_url = reverse('project_detail', args=[project.id])

        data = {'name': 'Updated Project Name'}
        response = self.client.put(project_detail_url, data, format='json')

        # Ensure project name is updated
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Project Name')
        project.refresh_from_db()
        self.assertEqual(project.name, 'Updated Project Name')

    def test_delete_project(self):
        """Test deleting an existing project."""
        project = Project.objects.create(name='Project to Delete', user=self.user)
        project_detail_url = reverse('project_detail', args=[project.id])

        response = self.client.delete(project_detail_url)

        # Ensure project is deleted
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)

    def test_project_owner_access_and_restricted_access_for_other_users(self):
        """Test that project owner can access the project and other users cannot."""
        # Create new project
        data = {'name': 'Test Project'}
        response = self.client.post(self.project_list_url, data, format='json')
        project_id = response.data['id']

        # The owner should be able to access the project
        project_detail_url = reverse('project_detail', args=[project_id])
        response = self.client.get(project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create a new user
        new_user = User.objects.create_user(username='newuser', password='password')
        refresh = RefreshToken.for_user(new_user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # The new user should not be able to access the project
        response = client.get(project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_owner_access_and_restricted_access_for_unauthenticated_users(self):
        """Test that project owner can access the project and unauthenticated users cannot."""

        # Create new project
        data = {'name': 'Test Project'}
        response = self.client.post(self.project_list_url, data, format='json')
        project_id = response.data['id']

        # The owner should be able to access the project
        project_detail_url = reverse('project_detail', args=[project_id])
        response = self.client.get(project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Unauthenticated user should not be able to access the project
        client = APIClient()
        response = client.get(project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access_to_project_list(self):
        """Test that unauthenticated users cannot access the project list."""
        client = APIClient()
        response = client.get(self.project_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access_to_project_detail(self):
        """Test that unauthenticated users cannot access the project detail."""
        project = Project.objects.create(name='Test Project', user=self.user)
        project_detail_url = reverse('project_detail', args=[project.id])

        client = APIClient()
        response = client.get(project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access_to_project_update(self):
        """Test that unauthenticated users cannot update the project."""
        project = Project.objects.create(name='Test Project', user=self.user)
        project_detail_url = reverse('project_detail', args=[project.id])

        client = APIClient()
        response = client.put(project_detail_url, {'name': 'Updated Project Name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access_to_project_delete(self):
        """Test that unauthenticated users cannot delete the project."""
        project = Project.objects.create(name='Test Project', user=self.user)
        project_detail_url = reverse('project_detail', args=[project.id])

        client = APIClient()
        response = client.delete(project_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access_to_project_create(self):
        """Test that unauthenticated users cannot create a project."""
        client = APIClient()
        response = client.post(self.project_list_url, {'name': 'Test Project'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class APIKeyCreateViewTests(APITestCase):
    def setUp(self):
        # Create a user and generate JWT token
        self.user = User.objects.create_user(username='testuser', password='password')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a test project
        self.project = Project.objects.create(name='Test Project', user=self.user)

        # URL for creating an API key
        self.api_key_create_url = reverse('api_key_create')

    def test_create_api_key_success(self):
        """Test that an authenticated user can create an API key successfully."""
        data = {'project': self.project.uuid}
        response = self.client.post(self.api_key_create_url, data, format='json')

        # Check response status and content
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('key', response.data)

        # Verify that the API key is created in the database
        self.assertEqual(APIKey.objects.count(), 1)
        self.assertEqual(APIKey.objects.first().project, self.project)
        self.assertEqual(APIKey.objects.first().user, self.user)

    def test_create_api_key_unauthenticated(self):
        """Test that an unauthenticated request is forbidden from creating an API key."""
        # Clear authorization header to simulate unauthenticated request
        self.client.credentials()

        data = {'project': self.project.uuid}
        response = self.client.post(self.api_key_create_url, data, format='json')

        # Verify that access is forbidden
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_api_key_invalid_data(self):
        """Test that an error is returned when invalid data is provided."""
        # Provide invalid project ID
        data = {'project': str(uuid4())}  # Non-existent project ID
        response = self.client.post(self.api_key_create_url, data, format='json')

        # Verify response status and error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('project', response.data)


class APIKeyListViewTests(APITestCase):
    def setUp(self):
        # Create a user and generate JWT token
        self.user = User.objects.create_user(username='testuser', password='password')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a test project
        self.project = Project.objects.create(name='Test Project', user=self.user)

        # Create an API key for the project
        self.api_key = APIKey.objects.create(project=self.project, user=self.user)

        # URL for listing API keys
        self.api_key_list_url = reverse('api_key_list')

    def test_list_api_keys_success(self):
        """Test that an authenticated user can list their API keys."""
        response = self.client.get(self.api_key_list_url)

        # Verify response status and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0]['project'], self.project.name)
        self.assertEqual(response.data[0]['project_uuid'], str(self.project.uuid))

        # Key should not be returned in the response
        self.assertNotIn('key', response.data[0])

    def test_list_api_keys_unauthenticated(self):
        """Test that an unauthenticated request is forbidden from listing API keys."""
        # Clear authorization header to simulate unauthenticated request
        self.client.credentials()

        response = self.client.get(self.api_key_list_url)

        # Verify that access is forbidden
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_api_keys_no_keys(self):
        """Test that an empty list is returned when the user has no API keys."""
        # Delete the API key created in the setUp method
        self.api_key.delete()

        response = self.client.get(self.api_key_list_url)

        # Verify response status and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertIsInstance(response.data, list)

    def test_list_api_keys_multiple_keys(self):
        """Test that multiple API keys are listed correctly."""
        # Create a second API key for the project
        api_key_2 = APIKey.objects.create(project=self.project, user=self.user)

        response = self.client.get(self.api_key_list_url)

        # Verify response status and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0]['project'], self.project.name)
        self.assertEqual(response.data[1]['project'], self.project.name)
        self.assertNotIn('key', response.data[0])
        self.assertNotIn('key', response.data[1])
        self.assertEqual(self.api_key.id, response.data[0]['id'])
        self.assertEqual(api_key_2.id, response.data[1]['id'])

    def test_list_api_key_does_not_show_other_users_keys(self):
        """Test that API keys of other users are not listed."""
        # Create a new user and project
        new_user = User.objects.create_user(username='newuser', password='password')
        new_project = Project.objects.create(name='New Project', user=new_user)
        APIKey.objects.create(project=new_project, user=new_user)

        response = self.client.get(self.api_key_list_url)

        # Verify that only the user's API keys are listed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['project'], self.project.name)


class APIKeyDeleteViewTests(APITestCase):
    def setUp(self):
        # Create a user and generate JWT token
        self.user = User.objects.create_user(username='testuser', password='password')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create a test project
        self.project = Project.objects.create(name='Test Project', user=self.user)

        # Create an API key for the project
        self.api_key = APIKey.objects.create(project=self.project, user=self.user)

        # URL for deleting an API key
        self.api_key_delete_url = reverse('api_key_delete', args=[self.api_key.id])

    def test_delete_api_key_success(self):
        """Test that an authenticated user can delete an API key successfully."""
        response = self.client.delete(self.api_key_delete_url)

        # Verify response status and content
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(APIKey.objects.count(), 0)

    def test_delete_api_key_unauthenticated(self):
        """Test that an unauthenticated request is forbidden from deleting an API key."""
        # Clear authorization header to simulate unauthenticated request
        self.client.credentials()

        response = self.client.delete(self.api_key_delete_url)

        # Verify that access is forbidden
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_api_key_not_found(self):
        """Test that a 404 error is returned when the API key does not exist."""
        # Delete the API key created in the setUp method
        self.api_key.delete()

        response = self.client.delete(self.api_key_delete_url)

        # Verify response status and content
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(APIKey.objects.count(), 0)

    def test_delete_api_key_wrong_user(self):
        """Test that a user cannot delete another user's API key."""
        # Create a new user and project
        new_user = User.objects.create_user(username='newuser', password='password')
        new_project = Project.objects.create(name='New Project', user=new_user)
        new_api_key = APIKey.objects.create(project=new_project, user=new_user)

        # Attempt to delete the new user's API key
        api_key_delete_url = reverse('api_key_delete', args=[new_api_key.id])
        response = self.client.delete(api_key_delete_url)

        # Verify that the API key is not deleted
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(APIKey.objects.count(), 2)
        self.assertEqual(APIKey.objects.get(id=self.api_key.id), self.api_key)
        self.assertEqual(APIKey.objects.get(id=new_api_key.id), new_api_key)
