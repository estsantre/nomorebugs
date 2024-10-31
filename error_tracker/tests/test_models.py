from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from project_integrations.models import Project
from error_tracker.models import ErrorLog, ErrorGroup


class ErrorGroupModelTests(TestCase):

    def test_create_error_group(self):
        """
        Test that an ErrorGroup instance can be created with a timestamp.
        """
        error_group = ErrorGroup.objects.create()
        self.assertIsNotNone(error_group.created_at)
        self.assertTrue(timezone.now() - error_group.created_at < timezone.timedelta(seconds=1))


class ErrorLogModelTests(TestCase):

    def setUp(self):
        # Create a user, project, and error group for testing
        self.user = User.objects.create_user(username="testuser", password="password")
        self.project = Project.objects.create(name="Test Project", user=self.user)
        self.error_group = ErrorGroup.objects.create()

    def test_create_error_log(self):
        """
        Test that an ErrorLog instance can be created with required fields.
        """
        error_log = ErrorLog.objects.create(
            error_message="Sample error message",
            environment="Production",
            project=self.project,
            error_group=self.error_group
        )
        self.assertIsNotNone(error_log.created_at)
        self.assertEqual(error_log.error_message, "Sample error message")
        self.assertEqual(error_log.environment, "Production")
        self.assertEqual(error_log.project, self.project)
        self.assertEqual(error_log.error_group, self.error_group)

    def test_error_log_project_relationship(self):
        """
        Test that an ErrorLog is correctly linked to a Project.
        """
        error_log = ErrorLog.objects.create(
            error_message="Test error message",
            environment="Production",
            project=self.project,
            error_group=self.error_group
        )
        self.assertEqual(error_log.project, self.project)
        self.assertEqual(error_log.project.name, "Test Project")

    def test_error_log_error_group_relationship(self):
        """
        Test that an ErrorLog is correctly linked to an ErrorGroup.
        """
        error_log = ErrorLog.objects.create(
            error_message="Another error message",
            environment="Staging",
            project=self.project,
            error_group=self.error_group
        )
        self.assertEqual(error_log.error_group, self.error_group)
        self.assertEqual(error_log.error_group.created_at, self.error_group.created_at)

    def test_error_log_created_at_auto_set(self):
        """
        Test that the created_at field in ErrorLog is set automatically upon creation.
        """
        error_log = ErrorLog.objects.create(
            error_message="Timestamp check",
            environment="Testing",
            project=self.project,
            error_group=self.error_group
        )
        self.assertIsNotNone(error_log.created_at)
        self.assertTrue(timezone.now() - error_log.created_at < timezone.timedelta(seconds=1))
