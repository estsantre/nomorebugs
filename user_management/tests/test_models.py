from django.test import TestCase
from django.contrib.auth.models import User
from user_management.models import UserProfile
from django.core.exceptions import ValidationError


class UserProfileModelTests(TestCase):

    def setUp(self):
        # Create a user and a profile for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = self.user.profile

    def test_user_profile_creation(self):
        """
        Test that a UserProfile instance is created for a user
        and the account_type field defaults to 'free' if not specified.
        """
        # Test profile creation and default account_type
        new_user = User.objects.create_user(username='newuser', password='password')
        profile = UserProfile.objects.get(user=new_user)

        self.assertIsInstance(profile, UserProfile)
        self.assertEqual(profile.account_type, 'free')

    def test_user_profile_string_representation(self):
        """
        Test that the UserProfile string representation returns the username.
        """
        self.assertEqual(str(self.profile), 'testuser')

    def test_user_profile_account_type_choices(self):
        """
        Test that UserProfile accepts only valid choices for account_type.
        """
        self.profile.account_type = 'free'
        self.profile.save()
        self.assertEqual(self.profile.account_type, 'free')

        # Attempting to assign an invalid choice should raise a ValidationError
        with self.assertRaises(ValidationError):
            self.profile.account_type = 'invalid_choice'
            self.profile.full_clean()

    def test_user_profile_account_type_premium(self):
        """
        Test that the account_type can be set to 'premium' and saved correctly.
        """
        self.profile.account_type = 'premium'
        self.profile.save()
        self.assertEqual(self.profile.account_type, 'premium')
