# project_integrations/tests/test_models.py

from django.contrib.auth.models import User
from django.test import TestCase
from project_integrations.models import Project, APIKey
from uuid import uuid4, UUID
from django.db.utils import IntegrityError


class APIKeyModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create a test project for the user
        self.project = Project.objects.create(name='Test Project', user=self.user)

    def test_create_api_key(self):
        """Test creating an API key for a project."""
        api_key = APIKey.objects.create(user=self.user, project=self.project)

        # Verify that the API key is created successfully
        self.assertIsInstance(api_key, APIKey)
        self.assertEqual(api_key.user, self.user)
        self.assertEqual(api_key.project, self.project)

    def test_api_key_is_uuid(self):
        """Test that the API key is a valid UUID."""
        api_key = APIKey.objects.create(user=self.user, project=self.project)

        # Check if the key is a valid UUID
        try:
            uuid_obj = UUID(str(api_key.key), version=4)
        except ValueError:
            uuid_obj = None
        self.assertIsNotNone(uuid_obj)
        self.assertEqual(uuid_obj.version, 4)

    def test_api_key_uniqueness(self):
        """Test that each API key is unique."""
        api_key1 = APIKey.objects.create(user=self.user, project=self.project)
        api_key2 = APIKey.objects.create(user=self.user, project=self.project)

        # Ensure that each key is unique
        self.assertNotEqual(api_key1.key, api_key2.key)

    def test_api_key_str_representation(self):
        """Test the string representation of the API key."""
        api_key = APIKey.objects.create(user=self.user, project=self.project)

        # Check the string representation
        self.assertEqual(str(api_key), f"Key for {self.project.name}")


class ProjectModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_create_project(self):
        """Test that a project can be created and associated with a user."""
        uuid = uuid4()
        project = Project.objects.create(name='Test Project', user=self.user, uuid=uuid)

        # Check if the project is created successfully
        self.assertIsInstance(project, Project)
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.user, self.user)
        self.assertEqual(project.uuid, uuid)

    def test_project_name_max_length(self):
        """Test that the name field has a max length of 100 characters."""
        project = Project.objects.create(name='A' * 100, user=self.user)

        # Verify that the name length is accepted at exactly 100 characters
        self.assertEqual(len(project.name), 100)

    def test_project_str_representation(self):
        """Test the string representation of the project."""
        project = Project.objects.create(name='My Project', user=self.user)

        # Check that the __str__ method returns the correct project name
        self.assertEqual(str(project), 'My Project')

    def test_project_uuid_uniqueness(self):
        """Test that the UUID field of the project is unique."""
        uuid = uuid4()
        Project.objects.create(name='Project 1', user=self.user, uuid=uuid)

        with self.assertRaises(IntegrityError):
            Project.objects.create(name='Project 2', user=self.user, uuid=uuid)
